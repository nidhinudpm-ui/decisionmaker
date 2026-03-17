def normalize_scores(criteria_configs, options_data):
    """
    Normalizes raw values for each criterion across all options to a 0-10 scale.
    criteria_configs: List of dicts with {id, direction ('higher_better' or 'lower_better')}
    options_data: Dict mapping option_id to a dict of {criterion_id: raw_value}
    """
    normalized_results = {} # {option_id: {criterion_id: normalized_score}}
    
    # Initialize results
    for opt_id in options_data:
        normalized_results[opt_id] = {}

    for crit in criteria_configs:
        crit_id = crit['id']
        direction = crit['direction']
        
        # Collect all raw values for this criterion
        values = []
        for opt_id in options_data:
            val = options_data[opt_id].get(crit_id)
            if val is not None:
                values.append(val)
        
        if not values:
            continue
            
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val
        
        for opt_id in options_data:
            raw_val = options_data[opt_id].get(crit_id)
            if raw_val is None:
                normalized_results[opt_id][crit_id] = 0
                continue
                
            if range_val == 0:
                # All values are the same
                normalized_results[opt_id][crit_id] = 10.0
                continue
                
            if direction == 'higher_better':
                # (x - min) / (max - min) * 10
                score = ((raw_val - min_val) / range_val) * 10
            else:
                # (max - x) / (max - min) * 10
                score = ((max_val - raw_val) / range_val) * 10
                
            normalized_results[opt_id][crit_id] = round(score, 2)
            
    return normalized_results

def calculate_weighted_totals(criteria_weights, normalized_scores):
    """
    Computes final weighted scores for each option.
    criteria_weights: Dict of {criterion_id: weight_value}
    normalized_scores: Dict of {option_id: {criterion_id: score}}
    """
    final_rankings = []
    
    # Normalize weights so they sum to 1.0 (internal normalization)
    total_weight = sum(criteria_weights.values())
    if total_weight == 0:
        return []
        
    for opt_id, scores in normalized_scores.items():
        total_score = 0
        for crit_id, score in scores.items():
            weight = criteria_weights.get(crit_id, 0)
            normalized_weight = weight / total_weight
            total_score += score * normalized_weight
            
        final_rankings.append({
            'option_id': opt_id,
            'total_score': round(total_score, 2),
            'breakdown': scores
        })
        
    # Sort by total score descending
    final_rankings.sort(key=lambda x: x['total_score'], reverse=True)
    return final_rankings
