import pandas as pd


def data_preparation(team):
    # read in the season specific csv files
    nfl20 = pd.read_csv("../datasets/play_by_play_2020.csv", low_memory=False)
    nfl21 = pd.read_csv("../datasets/play_by_play_2021.csv", low_memory=False)
    nfl22 = pd.read_csv("../datasets/play_by_play_2022.csv", low_memory=False)

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


def bucket_column(data):
    # create a new column that specifies in which bucket the drive is at the moment (currently only two buckets)
    # TODO: make it more versatile for multiple buckets for future modifications
    def assign_value(row):
        if row['yardline_100'] <= 25.0:
            return '0'
        elif row['yardline_100'] > 25.0 and row['yardline_100'] <= 50.0:
            return '1'
        elif row['yardline_100'] > 50.0 and row['yardline_100'] <= 75.0:
            return '2'
        else:
            return '3'

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
    # TODO: check if that is correct
    condition = ((data['interception'] == 1) | (data['fumble'] == 1)) & (data['fixed_drive_result'] == 'Turnover')

    # Update the 'actions' column for rows that meet the condition
    data.loc[condition, 'actions'] = 'turnover'

    # add missed fieldgoal entry as turnover to the actions column
    # Create a condition to identify rows that meet the criteria
    condition = data['actions'] == 'missed_field_goal'

    # Replace the values in the "actions" column
    data.loc[condition, 'actions'] = 'turnover'

    # add touchdown entry to actions column
    # Create a condition to identify rows where 'touchdown' is 1
    # condition = data['touchdown'] == 1

    # Update the 'actions' column for rows that meet the condition
    # data.loc[condition, 'actions'] = 'touchdown'

    return data


def data_manipulation(data):
    ############ removing all unwanted play types ###########
    # define the play types to keep
    valid_play_types = ['run', 'pass', 'punt', 'field_goal']

    # filter the DataFrame to keep rows with valid play types
    data = data[data['play_type'].isin(valid_play_types)]

    # drop more columns
    data = data.drop(columns=['home_team', 'away_team', 'posteam', 'defteam'])
    data = data.drop(['drive', 'fumble_forced', 'fumble_not_forced'], axis=1)
    # data = data.drop(['yardline_100'], axis=1)

    # create the actions column
    data = actions_column(data)

    # create the buckets
    data = bucket_column(data)

    return data


def play_type_frequency(data, num_sides):
    ############ only keep relevant columns ##############
    # define the columns to keep
    columns_to_keep = ['down', 'ydstogo', 'actions', 'side']

    # Keep only the specified columns
    team_nfl = data.loc[:, columns_to_keep]

    ######### rename the downs column entries ############
    # define the mapping for 'down' column
    down_mapping = {1.0: '1st', 2.0: '2nd', 3.0: '3rd', 4.0: '4th'}
    # replace values in 'down' column
    team_nfl['down'] = team_nfl['down'].replace(down_mapping)

    sides = []
    for i in range(0, num_sides):
        sides.append(str(i))

    downs = ['1st', '2nd', '3rd', '4th']
    types = ["run", "pass", "punt", "field_goal", "turnover"]  # kicked out touchdown

    # types:
    # 0_2nd_pass
    # 3_3rd_pass
    # 2_4th_punt

    # 0_2nd_pass_0  -> 0 -> 0 yards
    # 0_2nd_pass_3  -> 1-4 -> 4 yards
    # 0_2nd_pass_6  -> 5-8 -> 8 yards

    results_df = pd.DataFrame(columns=['Value', 'Count'])

    for side in sides:

        filtered = team_nfl[team_nfl['side'] == side]

        count = len(filtered)
        value = str(side)

        # print(value + " = " + str(count))

        # results_df.loc[len(results_df)] = {'Value': value, 'Count': count}

        for down in downs:

            filtered_downs = filtered[filtered['down'] == down]
            count = len(filtered_downs)
            value = str(side) + "_" + str(down)

            # print(value + " = " + str(count))

            # results_df.loc[len(results_df)] = {'Value': value, 'Count': count}

            for play_type in types:
                filtered_types = filtered_downs[filtered_downs['actions'] == play_type]
                count = len(filtered_types)
                value = str(side) + "_" + str(down) + "_" + play_type

                # print(value + " = " + str(count))

                results_df.loc[len(results_df)] = {'Value': value, 'Count': count}

    return results_df


def yards_gained_arrays(data, num_sides):
    ############ only keep relevant columns ##############
    # define the columns to keep
    columns_to_keep = ['down', 'yards_gained', 'actions', 'side']

    # Keep only the specified columns
    team_nfl = data.loc[:, columns_to_keep]

    ######### rename the downs column entries ############
    # define the mapping for 'down' column
    down_mapping = {1.0: '1st', 2.0: '2nd', 3.0: '3rd', 4.0: '4th'}
    # replace values in 'down' column
    team_nfl['down'] = team_nfl['down'].replace(down_mapping)

    sides = []
    for i in range(0, num_sides):
        sides.append(str(i))

    downs = ['1st', '2nd', '3rd', '4th']
    types = ["run", "pass", "punt", "field_goal", "turnover"]

    result_dict = {}

    for side in sides:

        filtered = team_nfl[team_nfl['side'] == side]

        for down in downs:

            filtered_downs = filtered[filtered['down'] == down]

            for play_type in types:
                filtered_types = filtered_downs[filtered_downs['actions'] == play_type]

                value = str(side) + "_" + str(down) + "_" + play_type

                yards_gained_list = []

                # Iterate through the DataFrame rows
                for row in filtered_types.iterrows():
                    # Get the yards_gained value for this row
                    yards_gained = row[1]['yards_gained']

                    #print(yards_gained)

                    # Add yards_gained to the list
                    yards_gained_list.append(yards_gained)

                result_dict[value] = yards_gained_list

    return result_dict


def yardage(team):
    data = data_manipulation(data_preparation(team))
    result = yards_gained_arrays(data, 4)

    return result


def type(team):
    data = data_manipulation(data_preparation(team))
    result = play_type_frequency(data, 4)

    return result


if __name__ == "__main__":
    data = data_manipulation(data_preparation('KC'))
    #print(data)

    play_type_frequency(data, 4)
    result = yards_gained_arrays(data, 4)

    first = result["0_1st_pass"]

