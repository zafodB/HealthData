'''
 * Created by filip on 16/08/2019
'''
import json
import os

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

'''
Recursively loops through all the files in the starting directory and counts the number of doctor
replies (answers with user status 'md').

Displays (or saves) the histogram of the counted replies.
'''
# starting_directory = "D:/Downloads/json/doctorQuestions/"
starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/sorted/"
# starting_directory = "/GW/D5data-1/BioYago/ehealthforum/json/impact/2015-12-09/ehealthforum/1"
# starting_directory = "D:/Downloads/json/healthboards/" + "1/"
# output_directory

histogram = {}
file_count = 0

# walk through the files in the starting directory
for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            # Open file
            file = open(os.path.join(root, file_name), "r", encoding="utf8")
            # file = open(starting_directory + file_name, "r", encoding="utf8")
            contents = file.read()
            file.close()
            file_as_json = json.loads(contents)

            doctor_answers = 0

            # Search for a Doctor reply
            for answer in file_as_json["answers"]:
                if answer["createdBy"]["status"] == "md":
                    doctor_answers += 1

            # Append number of doctor replies to the file
            if 'mdRepliesCount' not in file_as_json or file_as_json['mdRepliesCount'] != doctor_answers:
                reply_number = {'mdRepliesCount': doctor_answers}
                file_as_json.update(reply_number)

                file = open(os.path.join(root, file_name), "w", encoding="utf8")
                json.dump(file_as_json, file)
                file.close()

            # Update the histogram counter
            if histogram.get(doctor_answers) is None:
                histogram[doctor_answers] = 1
            else:
                histogram[doctor_answers] += 1

            # print(str(file_name) + " has " + str(doctor_answers) + " doctor answers")
            file_count += 1
            if file_count % 10000 == 0:
                print("Processed files: " + str(file_count))

        except Exception as e:
            print("Error processing file: " + file_name + ": " + str(e))

print(histogram)
plt.bar(list(histogram.keys()), histogram.values(), width=1.0, color='g')
# plt.show()
# plt.savefig(fname=("figure"))
