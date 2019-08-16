'''
 * Created by filip on 16/08/2019
'''
import json
import os
import matplotlib.pyplot as plt

starting_directory = "D:/Downloads/json/doctorQuestions/"
# starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/sorted/D/DoctorQuestion"
# starting_directory = "/GW/D5data-1/BioYago/ehealthforum/json/impact/2015-12-09/ehealthforum/1"
# starting_directory = "D:/Downloads/json/healthboards/" + "1/"
# output_directory

histogram = {}

# walk through the files in the starting directory
for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            # Open file
            file = open(starting_directory + file_name, "r", encoding="utf8")
            contents = file.read()
            file_as_json = json.loads(contents)

            doctor_answers = 0

            for answer in file_as_json["answers"]:
                if answer["createdBy"]["status"] == "md":
                    doctor_answers += 1

            if histogram.get(doctor_answers) is None:
                histogram[doctor_answers] = 1
            else:
                histogram[doctor_answers] += 1

            # print(str(file_name) + " has " + str(doctor_answers) + " doctor answers")

        except Exception as e:
            # e.
            print("Error processing file: " + file_name + ": " + str(e))

print(histogram)
plt.bar(list(histogram.keys()), histogram.values(), width=1.0, color='g')
# plt.show()
plt.savefig(fname=("~/" + "figure"))
