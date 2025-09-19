from pysam import VariantFile
from typing import Set, Optional

def collect_variant_ids(vcf_path: str, sample_id: Optional[str] = None) -> Set[str]:
    """
    Read VCF and return set of variant IDs for a single sample in format 'chrom:pos:ref:alt'.
    """
    with VariantFile(vcf_path) as vcf:
        if sample_id is not None:
            if sample_id not in vcf.header.samples:
                raise ValueError(f"Sample '{sample_id}' not found in VCF header.")
            chosen_sample = sample_id
        else:
            if len(vcf.header.samples) == 0:
                raise ValueError("No samples found in VCF header.")
            elif len(vcf.header.samples) > 1:
                raise ValueError(
                    f"Multi-sample VCF ({len(vcf.header.samples)} samples) "
                    f"requires specifying sample_id. Available: {list(vcf.header.samples)}"
                )
            chosen_sample = next(iter(vcf.header.samples))
        
        variant_ids: Set[str] = set()
        
        for rec in vcf.fetch():
            if not rec.alts or len(rec.alts) != 1:
                raise ValueError(
                    f"Non-biallelic record at {rec.chrom}:{rec.pos} "
                    f"(REF={rec.ref}, ALTS={rec.alts}). Expected exactly one ALT."
                )

            sample = rec.samples[chosen_sample]
            if sample.alleles and None not in sample.alleles:
                variant_id = f"{rec.chrom}:{rec.pos}:{rec.ref}:{rec.alts[0]}"
                variant_ids.add(variant_id)
                    
        return variant_ids