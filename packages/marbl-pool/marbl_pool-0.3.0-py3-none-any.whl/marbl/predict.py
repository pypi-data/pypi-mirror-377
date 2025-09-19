from pandas import DataFrame
from .matrix_context import MatrixContext
from multiprocessing import Pool, cpu_count
import numpy as np
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from .model import marbl, estimate_posteriors, estimate_background_posteriors

_model = None

def _init_model(m_kwargs):
    """Initializer runs once per worker; build model in the worker."""
    global _model
    _model = marbl(**m_kwargs)

def _predict_chunk(df_chunk: pd.DataFrame) -> np.ndarray:
    """Predict for one chunk using the worker's model."""
    return _model.predict_proba(df_chunk)

def run_model(dataset:DataFrame,
              matrix_context:MatrixContext,
              output_dir:Path,
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
              max_threads:int):

    matrix_size = matrix_context.n_rows

    if max_threads == 0:
        n_jobs = max(1, cpu_count() - 1)
    else:
        n_jobs = min(max_threads, cpu_count() - 1)
    chunks = n_jobs * 4

    row_post, col_post = estimate_posteriors(dataset, matrix_size, prior_strength=posterior_estimator_prior, theta_max=theta_cand_max)
    bg_a, bg_b = estimate_background_posteriors(dataset, matrix_size, theta_max=theta_bg_max)

    m_kwargs = dict(
        p_m1_d_p_m0=prior_odds,
        matrix_size=matrix_size,
        use_fallback=use_fallback,
        use_custom_cand_strength=use_custom_cand_strength,
        use_custom_other_strength=use_custom_other_strength,
        theta_carrier_row=row_post,
        theta_carrier_col=col_post,
        cand_strength=cand_strength,
        o_strength=other_strength,
        bg_strength=bg_strength,
        bg_theta=bg_a/(bg_a+bg_b) if bg_a+bg_b > 0 else 1e-10
    )

    df_chunks = np.array_split(dataset, chunks)

    with Pool(processes=n_jobs, initializer=_init_model, initargs=(m_kwargs,)) as pool:
        results = list(tqdm(pool.imap(_predict_chunk, df_chunks), total=len(df_chunks)))

    probs = np.concatenate(results)
    dataset['probability'] = probs

    dataset.to_csv(output_dir / 'predictions.tsv', sep='\t', encoding='utf-8', index=False, header=True)
    return dataset