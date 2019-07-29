### instead of bash script, run files here

from models.nn_zerow import *
from models.nn_dense import *
from models.nn_split import *
from models.process_data import set_starting_seed
from preprocessing.make_subset_data import create_train_test_data 
from test_models import *
from train_models import *
from collect_weights import *
from analyze import *
import sys
import time
from datetime import timedelta

def analyze(n):
	presets = [debug, record_data, test_behavior, seed, data]
	message = ["|Settings| Debugging is ", "Data recording is ", "Testing weight environment is ", "Fixed starting seed is ", "Dataset is "]
	status = {True: "on", False: "off", "subset": "subset dataset", "full": "full dataset"}
	settings_message = ["{}{}".format(b, status[a]) for a, b in zip(presets, message)] 
	
	print("Before starting data collection, are these settings correct?")
	print(*settings_message, sep=", ")
	correct = input("[Y, N] ")
	if correct.lower() in ["yes", "y", "ye"]:
		pass	
	else:
		print("Aborting...")
		return
	
	start_time = time.monotonic()
	
	#create_train_test_data()
	training_data = load_data("train")
	testing_data = load_data("test")
	
	
	print(" " * 50, end="\r")
	set_starting_seed()	
	
	print("\nStarting Data Collection")
	for i in range(int(n)):
		# Trains the models
		status = "Currently on iteration " + "{:03}".format(i+1) + ", working on:"
		
		print(status, "Zerow", end="\r")
		train_model(NN_zerow(), training_data)

		print(status, "Dense", end="\r")
		train_model(NN_dense(), training_data)

		print(status, "Split", end="\r")
		train_model(NN_split(), training_data)

		# Records the weights and saves to file
		if record_data:
			collect_weights()

		# Tests the models and saves percentages to file
		test_models([NN_dense(), NN_split(), NN_zerow()], testing_data)
	loop_time = time.monotonic()
	print(" " * 50, end="\r")
	print("\033[F-----Finished", n, "tests in", timedelta(seconds=loop_time - start_time))

	# Analysis Portion
	if test_behavior:
		print("\nChecking if weights were properly removed")
		verify_removed_weights()
	
	print("\nPercentages from session")
	print_percentages()

	#if record_data:
	#	print("\nDrawing distributions and saving to files under", image_path)
	#	draw_graphs(which="both")

	if testing_parameters:
		reset_files()

	end_time = time.monotonic()
	print("\n-----Finished experiment in", timedelta(seconds=end_time - start_time))
	

if __name__ == "__main__":
	analyze(sys.argv[1])
	#reset_files()
