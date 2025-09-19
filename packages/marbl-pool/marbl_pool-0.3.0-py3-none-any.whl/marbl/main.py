import logging
from pathlib import Path
from .matrix_context import get_context
from .variant_sites import collect_variant_sites
from .pileup import get_pileup_info
from .combinations import get_pool_combinations
from .dataset import create_dataset
from .predict import run_model

logger = logging.getLogger(__name__)

def process_variants(
    sampletable: Path,
    decodetable: Path,
    vcf_dir: Path,
    mpileup_dir: Path, 
    output_dir: Path,
    use_fallback: bool,
    use_custom_cand_strength:bool,
    use_custom_other_strength:bool,
    prior_odds:int,
    cand_strength:int,
    other_strength:int,
    bg_strength:int,
    theta_cand_max:float,
    theta_bg_max:float,
    posterior_estimator_prior:int,
    max_threads:int
) -> None:
    """ Main processing function """
    
    logger.info("Starting analysis")
    
    mc = get_context(sampletable=sampletable,decodetable=decodetable,output_dir=output_dir)

    """ Collect all sites of genetic variation """
    logger.info("Step 1: Collecting unique variant sites")
    sites = collect_variant_sites(matrix_context=mc, vcf_dir=vcf_dir, output_dir=output_dir)
    logger.debug(f"Found {len(sites)} unique sites")

    """ Collect pileup information for all sites """
    logger.info("Step 2: Collecting pileup data")
    pileup = get_pileup_info(variant_sites=sites, matrix_context=mc, mpileup_dir=mpileup_dir, output_dir=output_dir, max_threads=max_threads)
    logger.debug(f"Done collecting pileup data for {len(pileup)} samples.")

    """ Collect possible pool combinations """
    logger.info("Step 3: Collecting pool combinations")
    combinations, pool_variants = get_pool_combinations(pileup_data=pileup, vcf_dir=vcf_dir, matrix_context=mc, output_dir=output_dir)
    logger.debug(f"Found {len(set().union(*combinations.values()))} pool combinations.")

    """ Create dataset """
    logger.info("Step 4: Create dataset for predictions")
    dataset = create_dataset(rescue_combinations=combinations, pool_variants=pool_variants, pileup_data=pileup, matrix_context=mc, output_dir=output_dir)
    logger.debug(f"Created dataset of shape (n samples, n columns): {dataset.shape}")

    """ Run prediction model """
    logger.info("Step 5: Run prediction model on dataset")
    predictions = run_model(dataset=dataset,
                            matrix_context=mc,
                            output_dir=output_dir,
                            use_fallback=use_fallback,
                            use_custom_cand_strength=use_custom_cand_strength,
                            use_custom_other_strength=use_custom_other_strength,
                            prior_odds=prior_odds,
                            cand_strength=cand_strength,
                            other_strength=other_strength,
                            bg_strength=bg_strength,
                            theta_cand_max=theta_cand_max,
                            theta_bg_max=theta_bg_max,
                            posterior_estimator_prior=posterior_estimator_prior,
                            max_threads=max_threads)
    logger.debug(f"Assigned {len(predictions[(predictions['probability'] > 0.5) & (predictions['is_pool_pin'] == 0)])} additional variants.")
