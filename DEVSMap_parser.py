# refactor to put the helper functions in a different file, and have only json_parser.py???

'''

'''

from parser_reading_files import *
from generate_main_cpp import *
from generate_coupled_model_hpp import *
from generate_atomic_model_hpp import *
from generate_simple_statements import *

############################################################################
# To use this parser, we must only set the input and output directories.

# Set the input directory containing the DEVSMap json files
# These are the files that will be parsed and converted to Cadmium code.
directory_json_input = './input/'

# Set the desired output directory
# This should be the "main" directory in a Cadmium project, because
# the parser will place the main.cpp files into the "main" directory,
# and the atomic/coupled model files into the "main/include" directory.
directory_code_main_output = './output/main/'

############################################################################
# The remaining instructions are to run the parser, and no changes are 
# required by the user

# First, we construct  the output filepath for the atomic/coupled models
directory_code_include_output = directory_code_main_output + 'include/'

# Next, we check that we have a valid set of input files.  This will check 
# that we have exactly one init_state.json file, exactly one experiment.json 
# file, at least one coupled.json file, and at least one atomic.json file.
if check_file_counts(directory_json_input):

    # If the json input files are a valid set of DEVSMap files, we will clean 
    # the main and main/include directory of the previously generated files.
    # This deletes the existing main.cpp file from the main directory, and 
    # deletes all of the atomic and coupled model .hpp files from the 
    # main/include directory.
    clean_output_directory(directory_code_main_output)

    # Next, we read the JSON files, and parse them into a Python dictionary 
    # that contains a list for each type of file. For example, 
    # "data['atomic_models']" will contain a list where each index holds 
    # the data for one atomic model).
    raw_data = read_json_files(directory_json_input)
    data = sort_json_files(raw_data) 

    # Then, we obtain some key information such as the number of seconds
    # the simulation will run for, and obtain the name and data of the 
    # top model.
    simulation_time = get_simulation_time_in_seconds(data['experiment'])
    top_model_name = get_top_model_name(data['experiment'])
    top_model = get_top_model(data, top_model_name)

    # Finally, we can generate the code for the main.cpp file, and each of 
    # the atomic and coupled models.
    generate_main_cpp(directory_code_main_output, top_model_name, simulation_time)
    generate_coupled_models(directory_code_include_output, data)
    generate_atomic_models(directory_code_include_output, data)


############################################################################
# The following are suggested print statements for debugging

#print(data)
#print(data['atomic_models'])
#print(data['coupled_models'])
#print(data['experiment'])
#print(data['definition'])
#print(data['init_states'])
#print(data['param'])
#print(data['metadata'])

#print(data['atomic_models'][1]) 
#print(top_model)
