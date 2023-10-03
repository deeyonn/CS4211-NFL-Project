import pandas as pd

TEAM = 'KC'

# Import the .csv file
df = pd.read_csv('./datasets/reg_pbp_2018.csv')

# Print the first 5 rows of the DataFrame
print(df.head())

# Print the shape of the DataFrame
print("Rows: " + str(df.shape[0]), "Columns: " + str(df.shape[1]))

# Import the cols_to_drop list from cols_to_drop.py
from cols_to_drop import cols_to_drop

# Count the number of columns to drop
print("Number of columns to drop: " + str(len(cols_to_drop)))

# Drop the columns from the DataFrame
df = df.drop(cols_to_drop, axis=1)

# Print the shape of the DataFrame (again)
print("Rows: " + str(df.shape[0]), "Columns: " + str(df.shape[1]))

# Filter home_team and away_team
df = df[(df['home_team'] == TEAM) | (df['away_team'] == TEAM)]

# Print the shape of the DataFrame (again)
print("Rows: " + str(df.shape[0]), "Columns: " + str(df.shape[1]))