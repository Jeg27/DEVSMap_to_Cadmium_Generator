import os

// locate experiment json and store path
// Two ways....

//1. ask the user to provide the exact name of the experiment.json (if they have it)

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_ROOT = os.path.join(REPO_ROOT, "input")
INIT_ROOT = os.path.join(INPUT_ROOT, "init")
EXPERIMENT_ROOT =  os.path.join(INPUT_ROOT, "experiment")
MODEL_ROOT = os.path.join(INPUT_ROOT, "models")

def user_provide_experiment_json_filename():

    experiment_json_filename = input("Please provide the exact filename of the experiment.json: ")
    if experiment_json_filename is not in os.listdir(EXPERIMENT_ROOT):
        print("The provided filename does not exist in the experiment directory.\n Ensure the experiment.json file is located in inputs/experiments/ and try again.")
        return None

def obtain_experiment_data_from_gui

//2. use the stored experiment.json obtained from the gui. 

 
// locate mut and store path
// locate ef and store path
// locate mut init and store path
// locate ef init and store path

// 


