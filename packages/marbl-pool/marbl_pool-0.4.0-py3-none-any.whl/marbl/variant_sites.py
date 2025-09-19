from .matrix_context import MatrixContext
from .vcf_utils import collect_variant_ids
from pathlib import Path
from typing import Set

def collect_variant_sites(matrix_context:MatrixContext, vcf_dir:Path, output_dir:Path, caller:str='GATK') -> Set:
    
    row_vcfs = [vcf_dir / f"{pool}.{caller}.vcf.gz" for pool in matrix_context.row_pools]
    column_vcfs = [vcf_dir / f"{pool}.{caller}.vcf.gz" for pool in matrix_context.col_pools]
    variants = set()

    for dim in (row_vcfs,column_vcfs):
        for vcf in dim:
            variants |= collect_variant_ids(vcf)

    print(f"Found {len(variants)} unique variants.")        

    with open(output_dir / "sites.tsv", "w") as fout:
        for varid in variants:
            chrom, pos, ref, alt = varid.split(":")
            if ref == '*' or alt == '*':
                continue
            print(
                varid,
                chrom,
                pos,
                ref,
                alt,
                sep="\t",
                file=fout,
            )
    return variants