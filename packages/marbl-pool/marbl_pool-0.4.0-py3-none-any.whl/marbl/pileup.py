import sys
import gzip
import re
from collections import Counter
from typing import Tuple, List, Dict, NamedTuple
import csv
import logging
from pathlib import Path
import multiprocessing as mp
from functools import partial
from .matrix_context import MatrixContext

class Variant(NamedTuple):
    chrom: str
    pos: int
    ref: str
    alt: str

class PileupInfo(NamedTuple):
    chrom: str
    pos: int
    ref: str
    alt: str
    var_depth: int
    total_depth: int
    vaf: str

class PileupRead(NamedTuple):
    chrom: str
    pos: int
    ref: str
    depth: int
    bases: str
    qualities: str

def parse_pileup_line(line: str) -> PileupRead:
    fields = line.strip().split('\t')
    return PileupRead(
        chrom=fields[0],
        pos=int(fields[1]),
        ref=fields[2].upper(),
        depth=int(fields[3]),
        bases=fields[4],
        qualities=fields[5]
    )

def group_variants_by_chrom(variants: List[Variant]) -> Dict[str, List[Variant]]:
    chrom_variants = {}
    for var in variants:
        chrom_variants.setdefault(var.chrom, []).append(var)
    return chrom_variants

def remove_indels(match):
    # This removes indels and their preceding "," or ".".
    # Impossible to read in documentation if they are always preceded by 
    length = int(match.group(2))
    sequence = match.group(3)
    return sequence[length:] if len(sequence) > length else ''

def trim_indels(match):
    # This only removes the indel and not the preceding "," or ".".
    length = int(match.group(1))
    sequence = match.group(2)
    return sequence[length:] if len(sequence) > length else ''

def count_bases(pileup_read):
    bases = pileup_read.bases.upper()
    # Remove read markers
    bases = re.sub(r'\^.', '', bases)
    bases = re.sub(r'\$', '', bases)
    
    base_counts = Counter()
    
    # First pass: count indels
    indel_pattern = r'[+-](\d+)([ACGTNacgtn]+)'
    for match in re.finditer(indel_pattern, bases):
        indel_type = match.group(0)[0]  # + or -
        length = int(match.group(1))
        sequence = match.group(2)
        indel_seq = sequence[:length]
        indel_key = indel_type + indel_seq
        base_counts[indel_key] += 1
    
    # Second pass: count regular bases after cleaning indels
    # This could over estimate reference base counts. (Indels are maybe always preceded by a reference base indicator ('.' or ','))
    # Use remove_indels function instead.
    clean_bases = re.sub(r'[+-](\d+)([ACGTNacgtn]+)', trim_indels, bases)  # Replace indel patterns with their preceding reference character

    for base in clean_bases:
        if base == '.':
            base_counts[pileup_read.ref] += 1
        elif base == ',':
            base_counts[pileup_read.ref] += 1
        elif base in 'ACGTN*':
            base_counts[base] += 1
    
    return base_counts

def count_variant_bases(pileup: PileupRead, variant: Variant) -> Tuple[int, int]:
    bases = re.sub(r'\^.', '', pileup.bases.upper())
    bases = re.sub(r'\$', '', bases)
    total_depth = pileup.depth
    var_count = 0

    if variant.alt.startswith('+'):
        pattern = r'\+' + str(len(variant.alt[2:])) + variant.alt[2:]
        var_count = len(re.findall(pattern, bases))
    elif variant.alt.startswith('-'):
        pattern = r'-' + str(len(variant.ref[1:])) + variant.ref[1:]
        var_count = len(re.findall(pattern, bases))
    else:
        # clean_bases = re.sub(r'([.,])[+-](\d+)([ACGTNacgtn]+)', remove_indels, bases)
        clean_bases = re.sub(r'[+-](\d+)([ACGTNacgtn]+)', trim_indels, bases)
        var_count = clean_bases.count(variant.alt)
    if var_count > total_depth:
        print(variant, 'Variant count: ', var_count, "Total depth: ", total_depth)
        sys.exit('Alternative depth exceeds total depth')
    return var_count, total_depth

def process_pileup_file(pool_id: str, mpileup_dir:Path, chrom_variants: Dict[str, List[Variant]]) -> Tuple[str, Dict[Tuple[str, int, str, str], Tuple[int, int]]]:
    results = {}
    pileup_file = mpileup_dir / f'{pool_id}.mpileup'
    if not pileup_file.is_file() and pileup_file.with_suffix('.mpileup.gz').is_file():
        pileup_file = pileup_file.with_suffix('.mpileup.gz')
    opener = gzip.open if pileup_file.suffix == '.gz' else open
    mode = 'rt' if pileup_file.suffix == '.gz' else 'r'

    with opener(pileup_file, mode) as f:
        for line in f:
            pileup = parse_pileup_line(line)
            if pileup.chrom not in chrom_variants:
                continue
            for var in chrom_variants[pileup.chrom]:
                if var.pos == pileup.pos and var.ref[0] == pileup.ref:
                    var_key = (var.chrom, var.pos, var.ref, var.alt)
                    var_depth, total_depth = count_variant_bases(pileup, var)
                    results[var_key] = (var_depth, total_depth)
    return pool_id, results

def write_results(output_folder: Path, pool_id: str, results: Dict[Tuple[str, int, str, str], Tuple[int, int]], variants: List[Variant]):
    output_file = output_folder / (pool_id + "_pileup.tsv")
    with open(output_file, 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['CHROM', 'POS', 'REF', 'ALT', 'VAR_DEPTH', 'TOTAL_DEPTH', 'VAF'])
        for var in variants:
            key = (var.chrom, var.pos, var.ref, var.alt)
            alt_clean = var.alt.replace('-', '').replace('+', '')
            if key in results:
                var_depth, total_depth = results[key]
                vaf = var_depth / total_depth if total_depth > 0 else 0.0
                writer.writerow([var.chrom, var.pos, var.ref, alt_clean, var_depth, total_depth, f"{vaf:.4f}"])
            else:
                writer.writerow([var.chrom, var.pos, var.ref, alt_clean, 0, 0, "0.0000"])
    logging.info(f"Results written to {output_file}")

def get_pileup_info(variant_sites:set, matrix_context:MatrixContext, mpileup_dir:Path, output_dir:Path, max_threads:int) -> Dict[str, Dict[str, int]]:

    pool_ids = matrix_context.all_pools

    logging.info(f"Loaded {len(variant_sites)} variants.")

    variants = []
    for varid in variant_sites:
        chrom, pos, ref, alt = varid.split(':')
        if len(ref) > len(alt):
            alt = f"-{alt}"
        elif len(ref) < len(alt):
            alt = f"+{alt}"
        variants.append(Variant(chrom=chrom, pos=int(pos), ref=ref, alt=alt))
    variants = sorted(variants, key=lambda x: (x.chrom, x.pos))

    logging.info(f"Processing {len(variants)} variants")

    chrom_variants = group_variants_by_chrom(variants)

    if max_threads == 0:
        n_jobs = max(1, mp.cpu_count() - 1)
    else:
        n_jobs = min(max_threads, mp.cpu_count() - 1)

    with mp.Pool(n_jobs) as pool:
        process_func = partial(process_pileup_file, chrom_variants=chrom_variants, mpileup_dir=mpileup_dir)
        results = pool.map(process_func, pool_ids)

    pileup_data = {}
    for pool_id, file_results in results:
        pileup_data[pool_id] = {}
        for var in variants:
            key = (var.chrom, var.pos, var.ref, var.alt)
            alt_clean = var.alt.replace('-', '').replace('+', '')
            varid = f"{var.chrom}:{var.pos}:{var.ref}:{alt_clean}"
            var_depth, total_depth = file_results.get(key, (0, 0))
            vaf = var_depth / total_depth if total_depth > 0 else 0.0
            pileup_data[pool_id][varid] = PileupInfo(
                chrom=var.chrom,
                pos=var.pos,
                ref=var.ref,
                alt=alt_clean,
                var_depth=var_depth,
                total_depth=total_depth,
                vaf=f"{vaf:.4f}"
            )

    for pool_id, file_results in results:
        write_results(output_dir, pool_id, file_results, variants)
    
    return pileup_data