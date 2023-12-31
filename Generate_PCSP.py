import math
from distributions import yardage, fit_and_estimate_probabilities
from data_processing import type as get_data_for_team

# These can be adjusted to accommodate various requirements.
TEAM = "KC"
OPP_TEAM = "NYJ"

# Convenience constants for line breaks and indentation.
BR = "\n"
BR_TAB = "\n\t"
BR_2TAB = "\n\t\t"
BR_3TAB = "\n\t\t\t"
BR_4TAB = "\n\t\t\t\t"

ZONE = 4
DOWN = ['1st', '2nd', '3rd', '4th'] 
PLAYS = ['run', 'pass','pass_incomp', 'punt', 'field_goal', 'turnover']

# Use to generate probabilities for a play advancing YARDAGE_INCREMENT
YARDAGE_INCREMENT = 4
MAX_YARDAGE = 20
YARDAGE_INCREASE = list(range(0, MAX_YARDAGE + 1, YARDAGE_INCREMENT))

# Generate model logic strings
def generate_model_string(ZONE, DOWN, PLAYS, YARDAGE_INCREASE):
    model_string = "GuardedDown = [!GAME_OVER]Go->ExecuteDown;\n\n" + "// Guarded process that only runs the next down if the attacking team has not completed all 4.\n" + "NextPlay = GuardedDown[][GAME_OVER] Skip;\n\n" + "// Function to simulate a single down. Only executes if the attacking team has not used all 4 downs.\n"

    model_string += "ExecuteDown = case {"

    for down in DOWN:
        model_string += f"{BR_TAB}down == {down[:-2]}: case {{"

        for zone in range(1, ZONE + 1):
            model_string += f"{BR_2TAB}zone == {zone}: pcase {{"

            for play in PLAYS:
                model_string += f"{BR_3TAB}_{zone}_{down}_{play}: "

                if play == "run" or play == "pass":
                    model_string += "pcase {"

                    for yardage in YARDAGE_INCREASE:
                        play_upp_case = play.upper()
                        model_string += f"{BR_4TAB}_{zone}_{down}_{play}_{yardage}: UpdatePos({yardage}, {play_upp_case})"

                    model_string += f"{BR_3TAB}}}"

                elif play == "pass_incomp":
                    play_upp_case = play.upper()
                    model_string += f"UpdatePos(0, {play_upp_case})"
                elif play == "punt" or play == "turnover":
                    model_string += f"{play}{{down = 5}} -> NextPlay // Game over"
                elif play == "field_goal":
                    model_string += f"{play}{{score_field_goal = 1}} -> NextPlay // Game over"

            model_string += f"{BR_2TAB}}}"
        model_string += f"{BR_TAB}}}"
    model_string += f"{BR}}};"
    return model_string

# Generate pcsp file
def generate_pcsp():
    SETUP = 'script_model_setup.txt'
    HELPER_FUNC = 'script_helper_function.txt'
    ASSERTIONS = 'script_assertions.txt'

    model_string = generate_model_string(ZONE, DOWN, PLAYS, YARDAGE_INCREASE)
    play_probabilities_df = get_data_for_team(TEAM) # from data_processing.py
    data = yardage(TEAM)
    yard_probabilities_dict = fit_and_estimate_probabilities(data, TEAM, OPP_TEAM) # from distributions.py
    
    file_name = '%s_%s.pcsp' % (TEAM, OPP_TEAM)
    file_path = 'output/' + file_name

    setup_string = []
    with open(SETUP) as f:
        setup_string = f.readlines()
    
    # Probabilities for play selection
    play_probabilities_string = "\n"
    for index, row in play_probabilities_df.iterrows():
        play_probabilities_string += '#define _%s %d;\n' % (row["Value"], row["Count"])

    # Probabilities for yardage gained
    yard_probabilities_string = "\n"
    for p_name, p in yard_probabilities_dict.items():
        p = int(math.floor(p * 1000))
        yard_probabilities_string += '#define _%s %d;\n' % (p_name, p)
    yard_probabilities_string += "\n//---- End Probabilities Setup ----//\n\n"

    helper_func_string = []
    with open(HELPER_FUNC) as f:
        helper_func_string = f.readlines()

    assertions_string = []
    with open(ASSERTIONS) as f:
        assertions_string = f.readlines()
    
    lines = setup_string + [play_probabilities_string] + [yard_probabilities_string] + [model_string] + helper_func_string + assertions_string

    # write to file
    with open(file_path, 'w') as f:
        for line in lines:
            f.write(line)

generate_pcsp()


