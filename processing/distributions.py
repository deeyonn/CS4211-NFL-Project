import random
from scipy.stats import nbinom
import statsmodels.api as sm
import numpy as np
import warnings
import csv

def generate_nfl_like_dummy_data():
    ZONES = [0, 1, 2, 3]
    DOWNS = ["1st", "2nd", "3rd", "4th"]
    PLAYS = ["run", "pass"]

    data = {}

    for zone in ZONES:
        for down in DOWNS:
            for play in PLAYS:
                key = f"{zone}_{down}_{play}"
                
                yardages = []
                for _ in range(20):
                    r = random.random()
                    if r < 0.15:
                        gain = random.randint(-3, 0)  # Negative gains (losses) 
                    elif r < 0.6:
                        gain = random.randint(0, 4)  # Small gains are the most common
                    elif r < 0.8:
                        gain = random.randint(5, 10)  # Medium gains
                    elif r < 0.95:
                        gain = random.randint(11, 20)  # Large gains
                    else:
                        gain = random.randint(21, 40)  # Breakaway plays, more rare
                    yardages.append(gain)
                    
                data[key] = yardages

    return data

def fit_negative_binomial_mle(data):
    probabilities_dict = {}

    # Adjusted Buckets for yardage gains where the 17-20 bucket now represents 17-infinity
    BUCKETS = [(0, 0), (1, 4), (5, 8), (9, 12), (13, 16), (17, float('inf'))]

    # Corresponding names for the buckets
    BUCKET_NAMES = ['0', '4', '8', '12', '16', '20']

    # Suppress warnings within the context of this function
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        for key, yardages in data.items():
            # Positive yardage data for fitting
            positive_yardages = [y for y in yardages if y > 0]

            # Fit Negative Binomial using MLE
            model = sm.GLM(np.array(positive_yardages), np.ones_like(positive_yardages), 
                           family=sm.families.NegativeBinomial())
            result = model.fit()

            # Extract parameters
            r = result.params[0]
            p = result.scale / (result.scale + r)

            # Calculating probabilities for each bucket
            for bucket_range, bucket_name in zip(BUCKETS, BUCKET_NAMES):
                lower, upper = bucket_range
                if upper == float('inf'):
                    prob = 1 - nbinom.cdf(lower-1, r, p)  # Probability for 17 and above
                else:
                    prob = nbinom.cdf(upper, r, p) - nbinom.cdf(lower-1, r, p)
                
                # Form the new key and assign the probability
                new_key = f"{key}_{bucket_name}"
                probabilities_dict[new_key] = prob

    return probabilities_dict

def save_probabilities_to_csv(probabilities, csv_filename):
    with open(csv_filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        
        # Write the header row
        header = ['Key', 'Probability']
        writer.writerow(header)
        
        # Write the data rows
        for key, prob in probabilities.items():
            writer.writerow([key, prob])

data = generate_nfl_like_dummy_data()
probabilities = fit_negative_binomial_mle(data)
# print(probabilities)
# print(len(probabilities))

csv_filename = 'probabilities.csv'
save_probabilities_to_csv(probabilities, csv_filename)


