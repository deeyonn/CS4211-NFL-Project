import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from processing.distributions import probabilities as yard_probabilities_dict
from processing.data_processing_advanced import type as get_data_for_team

# Convenience constants for line breaks and indentation.
BR = "\n"
BR_TAB = "\n\t"
BR_2TAB = "\n\t\t"
BR_3TAB = "\n\t\t\t"
BR_4TAB = "\n\t\t\t\t"

# These constants can be adjusted to accommodate various requirements.
TEAM = "KC"
ZONE = 4
DOWN = ['1st', '2nd', '3rd', '4th'] 
PLAYS = ['run', 'pass', 'punt', 'fieldgoal', 'turnover']
YARDAGE_INCREMENT = 4
MAX_YARDAGE = 20

# Use to generate probabilities for a play advancing YARDAGE_INCREMENT
YARDAGE_INCREASE = list(range(0, MAX_YARDAGE + 1, YARDAGE_INCREMENT))

def generate_model_string(ZONE, DOWN, PLAYS, YARDAGE_INCREASE):
    model_string = "GuardedDown = [!GAME_OVER]Go->ExecuteDown;\n\n" + "// Guarded process that only runs the next down if the attacking team has not completed all 4.\n" + "NextPlay = GuardedDown[][GAME_OVER] Skip;\n\n" + "// Function to simulate a single down. Only executes if the attacking team has not used all 4 downs.\n"

    model_string += "ExecuteDown = case {"

    for down in DOWN:
        model_string += f"{BR_TAB}down == {down[:-2]}: case {{"

        for zone in range(1, ZONE + 1):
            model_string += f"{BR_2TAB}zone == {zone}: pcase {{"

            for play in PLAYS:
                model_string += f"{BR_3TAB}{zone}_{down}_{play}: "

                if play == "run" or play == "pass":
                    model_string += "pcase {"

                    for yardage in YARDAGE_INCREASE:
                        model_string += f"{BR_4TAB}{zone}_{down}_{play}_{yardage}: "

                        if yardage <= 10:
                            model_string += f"{play}{{ down++; pos = pos + {yardage} }} -> NextPlay"
                        else:
                            model_string += f"{play}{{ down = 1; pos = pos + {yardage} }} -> NextPlay"

                    model_string += f"{BR_3TAB}}}"

                elif play == "punt" or play == "turnover" or play == "field_goal":
                    model_string += f"{play}{{down = 5;}} -> NextPlay // Game over"

            model_string += f"{BR_2TAB}}}"
        model_string += f"{BR_TAB}}}"
    model_string += f"{BR}}}"
    return model_string

# generate pcsp file
def generate_pcsp():
    SETUP = 'scripts_pcsp/model_setup.txt'
    ASSERTIONS = 'scripts_pcsp/assertions.txt'

    model_string = generate_model_string(ZONE, DOWN, PLAYS, YARDAGE_INCREASE)
    play_probabilities_df = get_data_for_team(TEAM)
    print(play_probabilities_df)
    
    # file_name = '%s_%s_%s.pcsp' % (date, team1_name.replace(' ', '-'), team2_name.replace(' ', '-'))
    file_name = 'output/test.pcsp'

    setup_string = []
    with open(SETUP) as f:
        setup_string = f.readlines()
        
    play_probabilities_string = "\n"
    for index, row in play_probabilities_df.iterrows():
        play_probabilities_string += '#define %s %d;\n' % (row["Value"], row["Count"])

    yard_probabilities_string = "\n"
    for p_name, p in yard_probabilities_dict.items():
        yard_probabilities_string += '#define %s %f;\n' % (p_name, p)
    yard_probabilities_string += "\n//---- End Probabilities Setup ----//\n\n"

    assertions_string = []
    with open(ASSERTIONS) as f:
        assertions_string = f.readlines()
    
    lines = setup_string + [play_probabilities_string] + [yard_probabilities_string] + [model_string] + assertions_string

    # write to file
    with open(file_name, 'w') as f:
        for line in lines:
            f.write(line)

generate_pcsp()


