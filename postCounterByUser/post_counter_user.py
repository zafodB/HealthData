'''
 * Created by filip on 14/08/2019
'''

import os
import matplotlib.pyplot as plt

starting_directory = "D:/Downloads/json/healthboards/" + "1-sorted/"
# starting_directory = "/scratch/GW/pool0/fadamik/healthboards/sorted/"

histogram = {}

for letter_directory in os.listdir(starting_directory):
    for root, dirs, files in os.walk(starting_directory + letter_directory):
        for directory in dirs:
            file_count = len(os.listdir(starting_directory + letter_directory + "/" + directory))
            # print("Filecount in directory " + str(directory) + " is " + str(file_count))
            if histogram.get(file_count) is None:
                histogram[file_count] = 1
            else:
                histogram[file_count] += 1

            if file_count > 100:
                print(directory)

print(histogram)
plt.bar(list(histogram.keys()), histogram.values(), width=1.0, color='g')
# plt.show()
plt.savefig(fname=(starting_directory + "figure"))
