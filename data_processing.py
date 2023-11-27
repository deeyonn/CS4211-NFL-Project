import pandas as pd


def data_preparation(team):
    # read in the season specific csv files
    nfl20 = pd.read_csv("datasets/play_by_play_2020.csv", low_memory=False)
    nfl21 = pd.read_csv("datasets/play_by_play_2021.csv", low_memory=False)
    nfl22 = pd.read_csv("datasets/play_by_play_2022.csv", low_memory=False)

    # adding season parameter to each csv file
    nfl20['season'] = 20
    nfl21['season'] = 21
    nfl22['season'] = 22

    # merge all the data frames
    all_data = pd.concat([nfl20, nfl21, nfl22])

    # filter for the specified team
    team_nfl = all_data[(all_data['home_team'] == team) | (all_data['away_team'] == team)]

    # reducing the amount of columns
    columns_to_keep = [
        'play_id', 'game_id', 'home_team', 'away_team', 'posteam', 'defteam',
        'side_of_field', 'yardline_100', 'drive', 'down', 'yrdln', 'ydstogo',
        'desc', 'play_type', 'yards_gained', 'interception', 'fumble_forced',
        'fumble_not_forced', 'touchdown', 'fumble', 'field_goal_attempt',
        'punt_attempt', 'play_type_nfl', 'fixed_drive_result', 'drive_play_count', 'season'
    ]
    # keep only the specified columns
    team_nfl = team_nfl.loc[:, columns_to_keep]

    # filter for only offense plays
    team_nfl = team_nfl[team_nfl['posteam'] == team]

    return team_nfl


def bucket_column(data, given_team):

    # create a new column that specifies in which bucket the drive is at the moment
    def assign_value(row):
        value = row['yrdln']
        value_array = value.split()
        team = value_array[0]
        yards = float(value_array[1])

        if team == given_team:

            if yards <= 25.0:
                return '1'
            else:
                return '2'
        else:
            if team == "MID":
                return '2'
            elif yards >= 25.0:
                return '3'
            else:
                return '4'

    # Apply the function to create the new column
    data['side'] = data.apply(assign_value, axis=1)

    return data


def actions_column(data):
    # add new column
    data['actions'] = data['play_type']

    # add column entry missed_field_goal to the new actions column
    # create the conditions in order to filter for missed fieldgoals
    condition = (data['fixed_drive_result'] == 'Missed field goal') & (data['play_type'] == 'field_goal')

    # Update the 'actions' column for rows that meet the condition
    data.loc[condition, 'actions'] = 'missed_field_goal'

    # add turnover entry to the actions column
    # Create a condition to identify rows that meet the criteria
    condition = ((data['interception'] == 1) | (data['fumble'] == 1)) & (data['fixed_drive_result'] == 'Turnover')

    # Update the 'actions' column for rows that meet the condition
    data.loc[condition, 'actions'] = 'turnover'

    # add missed fieldgoal entry as turnover to the actions column
    # Create a condition to identify rows that meet the criteria
    condition = data['actions'] == 'missed_field_goal'

    # Replace the values in the "actions" column
    data.loc[condition, 'actions'] = 'turnover'

    return data


def data_manipulation(data, given_team):
    # removing all unwanted play types
    # define the play types to keep
    valid_play_types = ['run', 'pass', 'punt', 'field_goal']

    # filter the DataFrame to keep rows with valid play types
    data = data[data['play_type'].isin(valid_play_types)]

    # drop more columns
    data = data.drop(columns=['home_team', 'away_team', 'posteam', 'defteam'])
    data = data.drop(['drive', 'fumble_forced', 'fumble_not_forced'], axis=1)

    # create the actions column
    data = actions_column(data)

    # create the buckets column
    data = bucket_column(data, given_team)

    return data


def play_type_frequency(data, num_sides):
    # only keep relevant columns
    # define the columns to keep
    columns_to_keep = ['down', 'ydstogo', 'actions', 'side', 'yards_gained']

    # Keep only the specified columns
    team_nfl = data.loc[:, columns_to_keep]

    # rename the downs column entries
    # define the mapping for 'down' column
    down_mapping = {1.0: '1st', 2.0: '2nd', 3.0: '3rd', 4.0: '4th'}
    # replace values in 'down' column
    team_nfl['down'] = team_nfl['down'].replace(down_mapping)

    sides = []
    for i in range(1, num_sides + 1):
        sides.append(str(i))

    # specify all possible down values
    downs = ['1st', '2nd', '3rd', '4th']
    # specify all possible type values
    types = ["run", "pass", "punt", "field_goal", "turnover"]

    # create the result dataframe which is returned at the end of the function
    results_df = pd.DataFrame(columns=['Value', 'Count'])

    for side in sides:

        # filter for all entries with the specified side (position on the field)
        filtered = team_nfl[team_nfl['side'] == side]
        count = len(filtered)
        value = str(side)

        for down in downs:

            # filter for all entries with the specified down
            filtered_downs = filtered[filtered['down'] == down]
            count = len(filtered_downs)
            value = str(side) + "_" + str(down)

            for play_type in types:

                # filter for all entries with the specified play_type
                filtered_types = filtered_downs[filtered_downs['actions'] == play_type]

                # if play_type == pass distinguish between complete and incomplete pass
                if play_type == "pass":
                    incomplete = "incomp"

                    incomplete_count = 0
                    complete_count = 0
                    # iterates through the cells of the current row
                    for pass_type in filtered_types.iterrows():

                        yards_gained = pass_type[1]['yards_gained']

                        # if there is no yardage gain then the pass is considered to be an incomplete pass
                        if yards_gained <= 0:
                            incomplete_count = incomplete_count + 1
                        # otherwise it counts towards the complete pass count
                        else:
                            complete_count = complete_count + 1

                    # create the name of the stored value (this variable name is also used for the PAT model)
                    pass_value = str(side) + "_" + str(down) + "_" + play_type
                    incomp_value = str(side) + "_" + str(down) + "_" + play_type + "_" + incomplete
                    # store the data in the result dataframe
                    results_df.loc[len(results_df)] = {'Value': pass_value, 'Count': complete_count}
                    results_df.loc[len(results_df)] = {'Value': incomp_value, 'Count': incomplete_count}

                else:
                    # count all entries for the specified play_type
                    count = len(filtered_types)
                    # create the name of the stored value (this variable name is also used for the PAT model)
                    value = str(side) + "_" + str(down) + "_" + play_type
                    # store the data in the result dataframe
                    results_df.loc[len(results_df)] = {'Value': value, 'Count': count}

    return results_df


def yards_gained_arrays(data, num_sides):
    # only keep relevant columns
    # define the columns to keep
    columns_to_keep = ['down', 'yards_gained', 'actions', 'side']

    # Keep only the specified columns
    team_nfl = data.loc[:, columns_to_keep]

    # rename the downs column entries
    # define the mapping for 'down' column
    down_mapping = {1.0: '1st', 2.0: '2nd', 3.0: '3rd', 4.0: '4th'}
    # replace values in 'down' column
    team_nfl['down'] = team_nfl['down'].replace(down_mapping)

    # specify all possible side values (positions on the field)
    sides = []
    for i in range(1, num_sides + 1):
        sides.append(str(i))

    # specify all possible down values
    downs = ['1st', '2nd', '3rd', '4th']
    # specify all possible type values
    types = ["run", "pass", "punt", "field_goal", "turnover"]

    # create the result dictionary that will be returned at the end of the process
    result_dict = {}


    for side in sides:

        # filter for all entries with the specified side (position on the field)
        filtered = team_nfl[team_nfl['side'] == side]

        for down in downs:

            # filter for all entries with the specified down
            filtered_downs = filtered[filtered['down'] == down]

            for play_type in types:

                # filter for all entries with the specified play_type
                filtered_types = filtered_downs[filtered_downs['actions'] == play_type]

                # create the name of the stored value (this variable name is also used for the PAT model)
                value = str(side) + "_" + str(down) + "_" + play_type

                # create list that stores all integer values of the yards gained for every play
                yards_gained_list = []

                # iterate through the DataFrame rows
                for row in filtered_types.iterrows():
                    # get the yards_gained value for this row
                    yards_gained = row[1]['yards_gained']

                    # add yards_gained to the list
                    yards_gained_list.append(yards_gained)

                # add the result to the result dictionary
                result_dict[value] = yards_gained_list

    return result_dict


def yardage(team):
    # creates the output necessary for the "distributions.py" module
    data = data_manipulation(data_preparation(team), team)
    result = yards_gained_arrays(data, 4)

    return result


def type(team):
    # creates the output necessary for the "Generate_PCSP.py" module
    data = data_manipulation(data_preparation(team), team)
    result = play_type_frequency(data, 4)

    return result


if __name__ == "__main__":
    # main function for testing purposes
    data = data_manipulation(data_preparation('KC'))

    play_type_frequency(data, 4)
    result = yards_gained_arrays(data, 4)

    first = result["1_1st_pass"]


