import warnings
import numpy as np
import pandas as pd
from scipy.special import betaln, gammaln, expit
from collections import defaultdict, namedtuple

Posterior = namedtuple('Posterior', ['alpha', 'beta'])

def softplus(x):
    # stable: log(1 + exp(x))
    return np.logaddexp(0.0, x)

def log_sigmoid(logit):
    # log σ(x) = -softplus(-x)
    return -softplus(-logit)

def log1m_sigmoid(logit):
    # log(1 - σ(x)) = -softplus(logit)
    return -softplus(logit)

class marbl:
    """
    Hybrid Bayesian model that switches between symmetric and asymmetric scoring
    based on is_row_call and is_column_call indicators in the DataFrame.
    """
    def __init__(
        self,
        p_m1_d_p_m0 = 1,
        matrix_size=10,
        use_fallback=False,
        use_custom_cand_strength=False,
        use_custom_other_strength=False,
        theta_carrier_row=None,
        theta_carrier_col=None,
        cand_strength=200,
        o_strength=200,
        bg_strength=200,
        bg_theta=0.0003):
        self.P_M1_over_P_M0 = p_m1_d_p_m0
        self.matrix_size = matrix_size
        self.use_fallback = use_fallback
        self.use_custom_cand_strength = use_custom_cand_strength
        self.use_custom_other_strength = use_custom_other_strength
        self.theta_carrier_row = theta_carrier_row or {}
        self.theta_carrier_col = theta_carrier_col or {}
        self.cand_strength = cand_strength
        self.o_strength = o_strength
        self.bg_strength = bg_strength
        self.bg_theta = bg_theta

    def _beta_binomial_log_pmf(self, k, n, alpha, beta):
        if k < 0 or k > n:
            return -np.inf  # log(0), invalid cases
        log_coef = gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1)
        log_beta_part = betaln(k + alpha, n - k + beta) - betaln(alpha, beta)
        return log_coef + log_beta_part
    
    def _get_candidate_beta_params(self, row_id, col_id, called_dimension, fallback_strength):
        """
        Dynamically calculate alpha/beta from theta if available.
        Otherwise fallback to fixed two-carrier priors.
        """
        row_id, col_id = str(row_id), str(col_id)
        theta_matrix = self.theta_carrier_row if called_dimension == 'column' else self.theta_carrier_col
        theta = theta_matrix.get(row_id, {}).get(col_id)

        if theta is not None:
            alpha = theta.alpha
            beta = theta.beta
            return alpha, beta
        else:
            warnings.warn(f"No theta found for ({row_id}, {col_id}) in {called_dimension} lookup")
            fallback_theta = 1 / (2 * self.matrix_size)
            alpha = fallback_theta * fallback_strength
            beta = (1 - fallback_theta) * fallback_strength
            return alpha, beta

    def _calculate_logit_prob(self, k, n, var_alpha, var_beta, bg_alpha, bg_beta, prior_odds):
        """Calculate likelihoods for both models"""
        # Model M0: Background (no variant)
        ln_L_M0 = self._beta_binomial_log_pmf(k, n, bg_alpha, bg_beta)
        
        # Model M1: Variant present
        ln_L_M1 = self._beta_binomial_log_pmf(k, n, var_alpha, var_beta)

        logit = (ln_L_M1 - ln_L_M0) + np.log(prior_odds)

        return logit, expit(logit)

    def _score_candidate(self, row_id=None, col_id=None, called_dim=None, row=None):
        
        prior_odds = float(self.P_M1_over_P_M0)
        if prior_odds <= 0:
            raise ValueError("P_M1_over_P_M0 must be > 0")

        bg_alpha = self.bg_theta * self.bg_strength
        bg_beta = (1 - self.bg_theta) * self.bg_strength

        # --- Row candidate:
        
        alpha_cand, beta_cand = self._get_candidate_beta_params(row_id, col_id, 'column', self.cand_strength)
        if self.use_custom_cand_strength:
            s = alpha_cand + beta_cand
            if s <= 0: 
                raise ValueError("Invalid candidate alpha+beta <= 0")
            theta_cand = alpha_cand / s
            alpha_cand = theta_cand * self.cand_strength
            beta_cand = (1 - theta_cand) * self.cand_strength
        k = row['row_candidate_variant_depth']
        n = row['row_candidate_total_depth']

        row_logit, posterior_candidate_row = self._calculate_logit_prob(k, n, alpha_cand, beta_cand, bg_alpha, bg_beta, prior_odds)
        
        # --- Column candidate:
        alpha_cand, beta_cand = self._get_candidate_beta_params(row_id, col_id, 'row', self.cand_strength)
        if self.use_custom_cand_strength:
            s = alpha_cand + beta_cand
            if s <= 0:
                raise ValueError("Invalid candidate alpha+beta <= 0")
            theta_cand = alpha_cand / s
            alpha_cand = theta_cand * self.cand_strength
            beta_cand = (1 - theta_cand) * self.cand_strength
        k = row['column_candidate_variant_depth']
        n = row['column_candidate_total_depth']
        
        col_logit, posterior_candidate_column = self._calculate_logit_prob(k, n, alpha_cand, beta_cand, bg_alpha, bg_beta, prior_odds)

        if called_dim == 'both':
            log_p_cand = min(log_sigmoid(row_logit), log_sigmoid(col_logit))
            # log_p_cand = log_sigmoid(row_logit) + log_sigmoid(col_logit)
        elif called_dim == 'row':
            log_p_cand = log_sigmoid(col_logit)
        elif called_dim == 'column':
            log_p_cand = log_sigmoid(row_logit)
        else:
            raise ValueError("Invalid called dimension")

        lods = []
        posterior_probs = []

        for dim in ['row','col']:
            for i in range(1, self.matrix_size):
                key_v = f'{dim}{i}_variant_depth'
                key_t = f'{dim}{i}_total_depth'
                if dim == 'col':
                    col_id = row[f'{dim}{i}_id']
                    row_id = row['row_id']
                else:
                    col_id = row['column_id']
                    row_id = row[f'{dim}{i}_id']

                k = int(row[key_v])
                n = int(row[key_t])

                if n == 0:
                    continue
                if self.use_fallback:
                    alpha_cand = 1 / (2 * self.matrix_size) * self.o_strength
                    beta_cand = (1 - 1 / (2 * self.matrix_size)) * self.o_strength
                elif self.use_custom_other_strength:
                    alpha_cand, beta_cand = self._get_candidate_beta_params(row_id, col_id, 'row' if dim == 'col' else 'col', self.o_strength)
                    s = alpha_cand + beta_cand
                    if s <= 0:
                        raise ValueError("Invalid candidate alpha+beta <= 0")
                    theta_cand = alpha_cand / s
                    alpha_cand = theta_cand * self.o_strength
                    beta_cand = (1 - theta_cand) * self.o_strength
                else:
                    alpha_cand, beta_cand = self._get_candidate_beta_params(row_id, col_id, 'row' if dim == 'col' else 'col', self.o_strength)
                
                lod, posterior_prob = self._calculate_logit_prob(k, n, alpha_cand, beta_cand, bg_alpha, bg_beta, prior_odds)
                lods.append(lod)
                posterior_probs.append(posterior_prob)

        # P(candidate has variant)
        # posterior_prob_cand
        # P(background_i does NOT have variant) = 1 - P(background_i has variant)
        # [1 - p_bg for p_bg in posterior_prob]
        ## Joint probability = P(candidate variant) * ∏P(background_i no variant)
        log_prod_no_bg = np.sum([log1m_sigmoid(L) for L in lods]) if lods else 0.0
        log_joint = log_p_cand + log_prod_no_bg
        return np.exp(log_joint)

    def predict_proba(self, df):
        probs = []

        for _, row in df.iterrows():
            row_call = int(row.get('row_call'))
            col_call = int(row.get('column_call'))
            row_id = row.get('row_id')
            col_id = row.get('column_id')

            if row_call + col_call in (0, 2):
                p = self._score_candidate(row_id=row_id, col_id=col_id, called_dim='both',row=row)
            elif row_call == 1 and col_call == 0:
                p = self._score_candidate(row_id=row_id, col_id=col_id, called_dim='row',row=row)
            elif row_call == 0 and col_call == 1:
                p = self._score_candidate(row_id=row_id, col_id=col_id, called_dim='column',row=row)
            else:
                warnings.warn("Invalid call information")

            probs.append(p)
        return np.array(probs)

def estimate_posteriors(df, matrix_size, prior_strength=10.0, label_col='is_pool_pin', theta_max=1.0):
    """
    Estimate posterior Beta parameters for each cell-dimension using Bayesian updating.
    
    Args:
        df: DataFrame with variant calling data
        matrix_size: Size of the matrix
        prior_strength: Strength of the prior (higher = more regularization toward theoretical frequency)
        label_col: Column indicating positive samples
    
    Returns:
        tuple: (row_posteriors, col_posteriors)
            - row_posteriors: dict[row_id][col_id] -> Posterior(alpha, beta)
            - col_posteriors: dict[row_id][col_id] -> Posterior(alpha, beta)
    """
    # Calculate prior parameters
    theoretical_freq = 1 / (2 * matrix_size)
    alpha_prior = theoretical_freq * prior_strength
    beta_prior = (1 - theoretical_freq) * prior_strength
    
    # Collect observations
    observations = dict()
    observations['row'] = defaultdict(lambda: defaultdict(lambda: [0.0,0.0]))
    observations['column'] = defaultdict(lambda: defaultdict(lambda: [0.0,0.0]))
    
    positives = df[df[label_col] == 1]
    
    for _, row in positives.iterrows():
        row_id = str(row['row_id'])
        col_id = str(row['column_id'])
        
        # Collect observations
        for dim in ['row','column']:
            if (pd.notna(row[f'{dim}_candidate_variant_depth']) and 
                pd.notna(row[f'{dim}_candidate_total_depth'])):
                
                k = int(row[f'{dim}_candidate_variant_depth'])
                n = int(row[f'{dim}_candidate_total_depth'])
                
                theta_row = k/n
                if 0 < theta_row < theta_max:
                    observations[dim][row_id][col_id][0] += k
                    observations[dim][row_id][col_id][1] += n
            else:
                print('NAs in pinpoint matrix')
    
    # Compute posteriors for row observations
    posteriors = dict()
    for dim in ['row','column']:
        posteriors[dim] = defaultdict(dict)
        for row_id, col_dict in observations[dim].items():
            for col_id, _ in col_dict.items():
                k, n = observations[dim][row_id][col_id]
                alpha_post = alpha_prior + k
                beta_post = beta_prior + (n - k)
                
                posteriors[dim][row_id][col_id] = Posterior(alpha=alpha_post, beta=beta_post)
    
    return posteriors['row'], posteriors['column']

def estimate_background_posteriors(df, matrix_size, label_col='is_pool_pin', theta_max=1.0):
    """
    Estimate posterior Beta parameters for each cell-dimension using Bayesian updating.
    
    Args:
        df: DataFrame with variant calling data
        matrix_size: Size of the matrix
        prior_strength: Strength of the prior (higher = more regularization toward theoretical frequency)
        label_col: Column indicating positive samples
    
    Returns:
        tuple: (row_posteriors, col_posteriors)
            - row_posteriors: dict[row_id][col_id] -> Posterior(alpha, beta)
            - col_posteriors: dict[row_id][col_id] -> Posterior(alpha, beta)
    """
    
    positives = df[df[label_col] == 1]
    
    # Two versions, one common background alpha and one pool specific.
    # Go through each positive pool pin, add all none-candidates to one giant alpha

    posteriors = defaultdict(lambda: [0,0])
    alpha = 0
    beta = 0

    for _, row in positives.iterrows():
        for dim in ['row','col']:
            for i in range(1, matrix_size):
                key_v = f'{dim}{i}_variant_depth'
                key_t = f'{dim}{i}_total_depth'
                dim_id = row[f'{dim}{i}_id']
                k = int(row[key_v])
                n = int(row[key_t])
                theta = k/n
                if 0 < theta < theta_max:
                    posteriors[dim_id][0] += k
                    posteriors[dim_id][1] += n - k
                    alpha += k
                    beta += n - k
    
    return alpha, beta
