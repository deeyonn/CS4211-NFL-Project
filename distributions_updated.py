import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gamma
from data_processing_advanced import yardage
import pandas as pd

def get_elo_ratings(team_name):
    df = pd.read_csv('nfl_elo_ratings.csv')
    team_rating = df[df['team'] == team_name]['rating'].values[0]
    return team_rating

def fit_and_estimate_probabilities(dummy_data, off_team, def_team):
    off_elo = get_elo_ratings(off_team)
    def_elo = get_elo_ratings(def_team)
    elo_diff = off_elo - def_elo
    SCALE_COEFF = 0.0005
    scaling_factor = 1 + (elo_diff * SCALE_COEFF)

    filtered_data = {k: dummy_data[k] for k in dummy_data if k.endswith('_run') or k.endswith('_pass')}
    probabilities_dict = {}

    for key, yardages in filtered_data.items():
        yardages = [y for y in yardages if y > 0]
        
        if len(yardages) < 2:
            probabilities_dict[f"{key}_0"] = 1.0
            for bucket_key in ['4', '8', '12', '16', '20']:
                probabilities_dict[f"{key}_{bucket_key}"] = 0.0
            continue

        yardages = np.array(yardages) * scaling_factor

        shape, loc, scale = gamma.fit(yardages, floc=0)

        gamma_dist = gamma(shape, loc=loc, scale=scale)
        
        buckets = [(0,), (1, 4), (5, 8), (9, 12), (13, 16), (17, np.inf)]
        bucket_keys = ['0', '4', '8', '12', '16', '20']
        
        for bucket, bucket_key in zip(buckets, bucket_keys):
            bucket_key_full = f"{key}_{bucket_key}"
            if len(bucket) == 1:
                prob = gamma_dist.pdf(bucket[0])
            elif np.isinf(bucket[1]):
                prob = 1 - gamma_dist.cdf(bucket[0]-1)
            else:
                prob = gamma_dist.cdf(bucket[1]) - gamma_dist.cdf(bucket[0]-1)
            probabilities_dict[bucket_key_full] = prob
        
        # plt.figure(figsize=(10, 6))
        # max_yardage = max(yardages) if yardages.size > 0 else 0
        # bins = np.arange(max_yardage + 2)
        # plt.hist(yardages, bins=bins, density=True, alpha=0.5, label='Raw Data')
        # x = np.linspace(0, max_yardage + 1, 100)
        # plt.plot(x, gamma_dist.pdf(x), color='red', label='Gamma PDF')
        # plt.title(f'Distribution for {key}')
        # plt.xlabel('Yardage Gain')
        # plt.ylabel('Probability Density')
        # plt.legend()
        # plt.show()
        
    return probabilities_dict

data = yardage('KC')
probabilities_dict = fit_and_estimate_probabilities(data, 'KC', 'NYJ')
print(len(probabilities_dict))
