'''
Open the saved data from the files and analyze them
Check if numbers are repeated and how many times there are overlap
'''
from settings import *
from copy import deepcopy
from collections import Counter
import matplotlib.pyplot as plt

def process_files(files=[ws_save_loc, w_save_loc, bs_save_loc, b_save_loc]):
	to_return = []
	for name in files:
		f = open(name, "r")
		dist_data = []
		for line in f:
			data = line.split()
			dist_data.append((data[0], list(map(int,data[1:]))))
		f.close()
		to_return.append(dist_data)
	return to_return

def normalize(d):
	total = sum(d.values())
	d = {i:(d[i]/total) for i in d}
	return d

def make_distributions(data, data_type, normalized=False):
	# normalized can be True, False, or "both"
	# data = [w_s, w, b_s, b]
	# dists = [split, dense, partial, d-p, d-s, p-s]	
	key = {"split": 0, "dense": 1, "partial": 2, 
			"dense-partial": 3, "dense-split": 4, "partial-split": 5}
	dists = [{i:0 for i in range(hidden_size)} for i in range(6)]
	if data_type == "weights":
		x = data[0] + data[1]
	elif data_type == "biases":
		x = data[2] + data[3]
	for data_sample in x:
		name, vals = key[data_sample[0]], data_sample[1]
		for i in vals:
			dists[name][i] += 1
	if normalized == "both":
		dists_norm =[normalize(dists[i]) for i in range(6)]
		return dists, dists_norm
	
	if normalized:
		dists = [normalize(dists[i]) for i in range(6)]
		
	return dists

# Three types of data: dense, split, partial
def draw_graph(dists, title, save_location="diagrams/distribution.pdf"):
	# dists = [split, dense, partial, d-p, d-s, p-s]i
	names = ["Split Model", "Dense Model", "Zero-weights Model", 
			"Dense-Zero Overlap", "Dense-Split Overlap", "Zero-Split Overlap"]
	colors = ["r", "g", "b", "tab:grey", "tab:brown", "tab:purple"]
	
	fig, axs = plt.subplots(3, 2, sharey=True) #,sharex=True, sharey=True)
	axs = axs.tolist()
	axs_list = [i for j in axs for i in j]
	fig.suptitle("Distribution of " + title + " " + modded.capitalize())
	fig.subplots_adjust(hspace=0.5)
	plt.rcParams['xtick.labelsize'] = 4

	for index, ax in enumerate(axs_list):
		ax.bar(list(dists[index].keys()), list(dists[index].values()), color=colors[index], align='center')
		ax.set_title(names[index])
		ax.set_xticklabels(labels=list(dists[index].keys()), minor=True, rotation='vertical')
	
	plt.savefig(save_location)

def draw_graphs(which="both"):
	# which can be one of {'both', 'weights', biases'}
	processed_data = process_files()
	key = {"weights":["weights"], "biases":["biases"], "both": ["weights", "biases"]}
	configs = ["_unnormalized_dist_2", "normalized_dist_2"] 
	for data in key[which]:
		unnorm, norm = make_distributions(processed_data, i, normalized="both")
		for config in configs:
			draw_graph(unnorm,  "Top 5 " + data.capitalize(), save_location=image_path + data + config + modded + ".pdf")

def biggest_weights(n, pretty_print=False):
	# Necessary stuff to be able to get info from any file
	processed_data = process_files()
	dists = make_distributions(processed_data, "weights", normalized=False)
	
	# returning top five biggest weights
	top = []
	for dist in dists:
		top.append(dict(Counter(dist).most_common(n)))
	for i, item in enumerate(top):
		x = sorted(item.items(), key=lambda x: x[1], reverse=True)
		output = "{"
		for pair in x:
			output += "{:02}".format(pair[0]) + ": " + "{:02}".format(pair[1]) + ", "
		output += "\b\b}"
		if pretty_print:
			print(output)
		top[i] = x
	# top = [split, dense, zerow, dz, ds, zs] dicts 
	return top[:n]

def closeness():
	processed_dists = biggest_weights(50)
	split, zerow = processed_dists[0], processed_dists[2]	
	same, close = [], []

	for i, (key, value) in enumerate(split):
		try:
			if key == zerow[i - 1][0]:
				close.append((key, value, zerow[i - 1][1]))
			elif key == zerow[i + 1][0]:
				close.append((key, value, zerow[i + 1][1]))
		except:
			continue
		if key == zerow[i][0]:
			same.append((key, value, zerow[i][1]))
	print("If the split and the zero-weights models had", 
			"the same weights at the same index\n", same)
	print("If the split and the zero-weights models have",
			"a similar weight index\n", close)
	print("How many times the two models overlapped during",
			"the same session\n", processed_dist[5][:5])

def print_percentages():
	f = open(percent_save_loc, "r")
	# info with list of [sensitivity, specificity, correctness]
	names = ["Zerow", "Dense", "Split"]
	percents = [[0]*3, [0]*3, [0]*3] #zerow, dense, split
	key = {"Zero-weights": 0, "Dense": 1, "Split": 2}
	total = 0
	for line in f:
		total += 1
		data = line.split()
		name = key[data[0]]
		data = list(map(float, data[1:]))
		percents[name] = [percents[name][i] + data[i] for i in range(3)]
	f.close()
	total = total / 3
	for index, model_perc in enumerate(percents):
		percents[index] = ["{0:.4f}".format(model_perc[i] / total) for i in range(3)]
		print(names[index], *percents[index], sep=", ")	

def verify_removed_weights():
	if test_behavior: 
		processed_data = process_files()
		# only interested in the main files, not overlap
		# that data is at first and third index
		data = [processed_data[1], processed_data[3]]
		name = ["weights", "biases"]
		# check if any of the weights_to_test are in there
		count = 0
		for i, dataset in enumerate(data):
			for ii, line in enumerate(dataset):
				model_name, big_weights = line
				error = name[i] + " " + model_name + " " + str(ii) + "\n"
				mistakes = [weight for weight in weights_to_test if weight in big_weights and model_name != "dense"]
				if len(mistakes) != 0:	
					print(error.join([str(x) for x in mistakes]))
				count += len(mistakes)
		if count == 0:
			print("Weights were properly removed")
	else:
		print("No need to test important weights. Make sure this is intentional.")

# Once unedited data, and modified weight data has been collected, this function can be run to show difference in plots
def show_differences():
	modded_dists = make_distributions(process_files(), "weights", normalized=True)
	files = [ws_save_loc, w_save_loc, bs_save_loc, b_save_loc]
	files = [i.replace(modded, "") for i in files]
	unmodded_dists = make_distributions(process_files(files), "weights", normalized=True)
	
	# each distribution is a list of dicts[split, dense, partial, d-p, d-s, p-s]
	# calculate difference with modded being subtracted from the normal data
	difference_dists = []
	for i in range(6):
		diff = {key:unmodded_dists[i][key] - modded_dists[i][key] for key in unmodded_dists[i].keys()}
		difference_dists.append(diff)

	draw_graph(difference_dists, "Difference of Normal Data and Weight-Removed Data", save_location="diagrams/difference.pdf")	

# collect information on the heaviest weights that were removed
def heavy_weight_info():
	f = open(text_gene_groups, "r")
	info = [] # tuple (index, gene group name, number of genes in group)
	for index, line in enumerate(f):
		if index in weights_to_test:
			line = line.split()
			info.append((index, line[0], len(line[2:])))
	for i in info:
		print(i)

def gene_groups_info():
	f = open(text_gene_groups, "r")
	info = []
	for line in f:
		info.append(len(line.split()[2:]))
	counts = {i:info.count(i) for i in set(info)}
	x = list(counts.keys())
	x.sort()
	for i in list(x):
		print(i, counts[i])

if __name__ == "__main__":
	#draw_graphs(which="both")
	#closeness()
	#verify_removed_weights()
	#print_percentages()
	#show_differences()
	heavy_weight_info()
	#gene_groups_info()