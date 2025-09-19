from pathlib import Path
from .vcf_utils import collect_variant_ids
from collections import defaultdict
from typing import Set, Dict
from .matrix_context import MatrixContext

# mads
# 2025-04-08
"""
This script extracts is under development.
It outputs reasonable combinations of pools and variants for pileup analysis.
This is based on:
    1. Pinpointables
    2. Singletons
    3. Single-multi - One call in one dimension and multiple in other.
    4. Two-by-two - Exactly two calls in each dimension.
"""

def get_other_variants(pools, idx):
    return set().union(*(pools[i] for i in range(len(pools)) if i != idx))

def pinpoint(vcf_dir: Path, caller: str, matrix_context: str) -> Dict[str, Dict[str, Set[str]]]:
    """
    Performs the actual pinpointing logic and returns a dictionary of variants per sample.
    
    Parameters:
    vcf_folder (Path): Path to the folder containing pool vcfs.
    caller (str): Variant caller name.
    
    Returns:
    A dictionary mapping sample IDs to their corresponding unique variants and all pinpointable variants.
    """
    sample_variants: Dict[str, Dict[str, Set[str]]] = {}

    row_vcfs = [vcf_dir / f"{pool}.{caller}.vcf.gz" for pool in matrix_context.row_pools]
    column_vcfs = [vcf_dir / f"{pool}.{caller}.vcf.gz" for pool in matrix_context.col_pools]

    row_pools = [set(collect_variant_ids(vcf)) for vcf in row_vcfs]
    column_pools = [set(collect_variant_ids(vcf)) for vcf in column_vcfs]

    # Pinning logic:
    for cell in matrix_context._ctx["matrix"]["cells"]:
        sample_id = cell["alias"]
        row_idx = cell["row_index"]
        col_idx = cell["col_index"]
        # Extract all variants from all other pools in each dimension
        other_row_variants = get_other_variants(row_pools, row_idx)
        other_col_variants = get_other_variants(column_pools, col_idx)
        
        # Extract unique and pool-specific variants
        unique_row_variants = row_pools[row_idx].difference(other_row_variants)
        unique_col_variants = column_pools[col_idx].difference(other_col_variants)
        unique_pins = unique_row_variants.intersection(unique_col_variants)

        # Extract all pinnable variants. Only required to be unique in one dimension
        unique_one_dimension_row = unique_row_variants.intersection(column_pools[col_idx])
        unique_one_dimension_col = unique_col_variants.intersection(row_pools[row_idx])
        all_pins = unique_one_dimension_row.union(unique_one_dimension_col)

        sample_variants[sample_id] = {
            "unique_pins": unique_pins,
            "all_pins": all_pins
        }
    
    return sample_variants

def get_pool_variants(vcf_dir:Path, matrix_context:MatrixContext, caller:str='GATK') -> Set:
    pool_variants = set()
    for pool in matrix_context.all_pools:
        pool_variants |= {f"{pool}:{varid}" for varid in collect_variant_ids(vcf_dir / f"{pool}.{caller}.vcf.gz")}
    return pool_variants

def get_rescue_combinations(matrix_ctx: MatrixContext, varids:Set, pileup_data:Dict[str, Dict[str, int]]):
    """
    Classify variants and generate rescue combinations.
    
    Returns:
        rescue_combinations: dict with 'single_multi' and 'two_by_two' sets
        counts: dict with classification counts for reporting
    """
    rescue_combinations = {
        'single_multi': set(),
        'two_by_two': set(),
        'row_singleton': set(),
        'column_singleton': set(),
        'singleton': set()
    }
    
    # Group variants by pools and dimension
    variant_pools = defaultdict(lambda: {'row': [], 'column': []})
    
    for varid in varids:
        pool_id, variant = varid.split(':', 1)
        dim = matrix_ctx.pool_dim(pool_id)
        variant_pools[variant][dim].append(pool_id)
    
    for variant, pools in variant_pools.items():
        row_count = len(pools['row'])
        col_count = len(pools['column'])
        
        if row_count == 1 and col_count == 0:
            # Generate combinations: single row × zero cols
            row_pool = pools['row'][0]
            for col_pool in matrix_ctx.col_pools:
                pile = pileup_data[col_pool][variant]
                if float(pile.vaf) > 0.0:
                    rescue_combinations['row_singleton'].add(f"{row_pool}:{col_pool}:{variant}")
                    rescue_combinations['singleton'].add(f"{row_pool}:{col_pool}:{variant}")
        elif col_count == 1 and row_count == 0:
            # Generate combinations: zero row × single cols
            col_pool = pools['column'][0]
            for row_pool in matrix_ctx.row_pools:
                pile = pileup_data[row_pool][variant]
                if float(pile.vaf) > 0.0:
                    rescue_combinations['column_singleton'].add(f"{row_pool}:{col_pool}:{variant}")
                    rescue_combinations['singleton'].add(f"{row_pool}:{col_pool}:{variant}")
        elif row_count == 1 and col_count > 1:
            # Generate combinations: single row × multiple cols
            row_pool = pools['row'][0]
            for col_pool in pools['column']:
                rescue_combinations['single_multi'].add(f"{row_pool}:{col_pool}:{variant}")
        elif col_count == 1 and row_count > 1:
            # Generate combinations: single col × multiple rows
            col_pool = pools['column'][0]
            for row_pool in pools['row']:
                rescue_combinations['single_multi'].add(f"{row_pool}:{col_pool}:{variant}")
        elif row_count == 2 and col_count == 2:
            # Generate combinations: 2 rows × 2 cols = 4 combinations
            for row_pool in pools['row']:
                for col_pool in pools['column']:
                    rescue_combinations['two_by_two'].add(f"{row_pool}:{col_pool}:{variant}")
    
    return rescue_combinations

def get_pool_combinations(pileup_data:Dict[str, Dict[str, int]], vcf_dir:Path, matrix_context:MatrixContext, output_dir:str, caller:str='GATK'):

    combinations = {'pool_pinpoint': set(), 'singleton': set(), 'single_multi': set(), 'two_by_two': set()}

    pool_pins_dict = pinpoint(vcf_dir=vcf_dir, caller=caller, matrix_context=matrix_context)
    for alias, pins in pool_pins_dict.items():
        cell = matrix_context.cell_from_alias(alias)
        combinations['pool_pinpoint'] |= {f"{cell['row_pool_id']}:{cell['col_pool_id']}:{p}" for p in pins['unique_pins']}

    print(f"Found {len(combinations['pool_pinpoint'])} pool pinpoints.")

    pool_variants = get_pool_variants(vcf_dir=vcf_dir,matrix_context=matrix_context)
    rescue_combinations = get_rescue_combinations(matrix_context, pool_variants, pileup_data)

    print(f"Found {len(rescue_combinations['row_singleton'])} unpaired row combinations.")
    print(f"Found {len(rescue_combinations['column_singleton'])} unpaired column combinations.")
    print(f"Found {len(rescue_combinations['single_multi'])} unpaired single-multi combinations.")
    print(f"Found {len(rescue_combinations['two_by_two'])} unpaired two-two combinations.")

    combinations['singleton'] = rescue_combinations['singleton']
    combinations['single_multi'] = rescue_combinations['single_multi']
    combinations['two_by_two'] = rescue_combinations['two_by_two']

    all_combinations = set().union(*combinations.values())
    for types in combinations:
        for var in combinations[types]:
            print(types, var)
            break

    # Write variants to file as uvarid, varid, pool 1, pool 2, chrom, pos, ref, alt
    with open(output_dir / 'variant_combinations.tsv', 'w') as f:
        print(
            "uvarid",
            "varid",
            "row",
            "column",
            "alias",
            "sample_id",
            "chrom",
            "pos",
            "ref",
            "alt",
            "is_pool_pin",
            "is_single",
            "is_single_multi",
            "is_two_by_two",
            "is_row_call",
            "is_column_call",
            sep="\t",
            file=f
        )
        for uvarid in all_combinations:
            row, column, chrom, pos, ref, alt = uvarid.split(':')
            varid = ":".join([chrom, pos, ref, alt])
            cell = matrix_context.cell(row, column)
            sample_id = cell.get('sample_id', 'Na')
            alias = cell['alias']
            print(
                uvarid,
                varid,
                row,
                column,
                alias,
                sample_id,
                chrom,
                pos,
                ref,
                alt,
                1 if uvarid in combinations['pool_pinpoint'] else 0,
                1 if uvarid in combinations['singleton'] else 0,
                1 if uvarid in combinations['single_multi'] else 0,
                1 if uvarid in combinations['two_by_two'] else 0,
                1 if f"{row}:{varid}" in pool_variants else 0,
                1 if f"{column}:{varid}" in pool_variants else 0,
                sep="\t",
                file=f
            )
    return combinations, pool_variants
