import pandas as pd
from pathlib import Path
from tqdm import tqdm
from typing import Set, Dict
from .matrix_context import MatrixContext

def create_dataset(matrix_context: MatrixContext, rescue_combinations:dict[str, set[str]], pool_variants:Set, pileup_data:Dict[str, Dict[str, int]], output_dir:Path):
    """More efficient version that pre-processes pool categorization."""
    
    row_pools = set(matrix_context.row_pools)
    col_pools = set(matrix_context.col_pools)
    
    all_combinations = set().union(*rescue_combinations.values())
    data_rows = []
    for combination in tqdm(all_combinations):
        row_pool_id, col_pool_id, varid = combination.split(':', 2)
        cell = matrix_context.cell(row_pool_id, col_pool_id)
            
        sample_id = cell.get('sample_id') if cell.get('sample_id') else cell['alias']
        alias = cell['alias']
        row_label = cell['row_label']
        column_label = cell['col_label']
        uvarid = f"{alias}:{varid}"
        
        # Determine combination type
        is_pool_pin = int(combination in rescue_combinations.get('pool_pinpoint'))
        is_single_multi = int(combination in rescue_combinations.get('single_multi'))
        is_two_by_two = int(combination in rescue_combinations.get('two_by_two'))
        is_single = int(combination in rescue_combinations.get('singleton'))
        is_row_call = 1 if f"{row_pool_id}:{varid}" in pool_variants else 0
        is_column_call = 1 if f"{col_pool_id}:{varid}" in pool_variants else 0
        
        # Process pools efficiently
        candidate_indices = [None, None]
        row_indices = []
        column_indices = []
        variant_depths = []
        total_depths = []
        all_pool_ids = []
        
        for n, pool_id in enumerate(pileup_data.keys()):
            if pool_id in row_pools:
                if pool_id == row_pool_id:
                    candidate_indices[0] = n
                else:
                    row_indices.append(n)
            elif pool_id in col_pools:
                if pool_id == col_pool_id:
                    candidate_indices[1] = n
                else:
                    column_indices.append(n)
            
            pile = pileup_data[pool_id][varid]
            variant_depths.append(pile.var_depth)
            total_depths.append(pile.total_depth)
            all_pool_ids.append(pool_id)

        data_row = {
            'uvarid': uvarid,
            'varid': varid,
            'row_id': row_pool_id,
            'column_id': col_pool_id,
            'row_label': row_label,
            'column_label': column_label,
            'sample_id': sample_id,
            'sample_alias': alias,
            'is_pool_pin': is_pool_pin,
            'is_single_multi': is_single_multi,
            'is_two_by_two': is_two_by_two,
            'is_single': is_single,
            'row_call': is_row_call,
            'column_call': is_column_call
        }
    
        data_row['row_candidate_variant_depth'] = variant_depths[candidate_indices[0]]
        data_row['row_candidate_total_depth'] = total_depths[candidate_indices[0]]
    
        data_row['column_candidate_variant_depth'] = variant_depths[candidate_indices[1]]
        data_row['column_candidate_total_depth'] = total_depths[candidate_indices[1]]

        
        for i, idx in enumerate(row_indices):
            data_row[f'row{i+1}_variant_depth'] = variant_depths[idx]
            data_row[f'row{i+1}_total_depth'] = total_depths[idx]
            data_row[f'row{i+1}_id'] = all_pool_ids[idx]
        
        for i, idx in enumerate(column_indices):
            data_row[f'col{i+1}_variant_depth'] = variant_depths[idx]
            data_row[f'col{i+1}_total_depth'] = total_depths[idx]
            data_row[f'col{i+1}_id'] = all_pool_ids[idx]
        
        data_rows.append(data_row)
    
    df = pd.DataFrame(data_rows)
    df.to_csv(output_dir / 'dataset.tsv', sep='\t', index=False)
    
    return df