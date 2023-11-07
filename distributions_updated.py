import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gamma
from data_processing import yardage

def fit_and_estimate_probabilities(dummy_data):
    filtered_data = {k: dummy_data[k] for k in dummy_data if k.endswith('_run') or k.endswith('_pass')}
    probabilities_dict = {}

    for key, yardages in filtered_data.items():
        yardages = [y for y in yardages if y > 0]
        
        if len(yardages) < 2:
            probabilities_dict[f"{key}_0"] = 1.0
            for bucket_key in ['4', '8', '12', '16', '20']:
                probabilities_dict[f"{key}_{bucket_key}"] = 0.0
            continue

        yardages = np.array(yardages)

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
probabilities_dict = fit_and_estimate_probabilities(data)
# print(probabilities_dict)

# data = yardage('KC')
# probabilities_dict = fit_and_estimate_probabilities(data)
# print(probabilities_dict)
