'''
 * Created by filip on 07/08/2019
'''

import json
import os
import shutil
import datetime
from dateutil.parser import *

'''
* Copies the files in the specified directory to a new 'sorted' folder. Each sub-folder is a username. Each file is copied
* and it's name changed to the date of the original post.
'''

starting_directory = "/GW/D5data-1/BioYago/healthboards/json/healthboards/1/"
# starting_directory = "D:/Downloads/json/healthboards/" + "1/"
# output_directory = "D:/Downloads/json/healthboards/" + "1-sorted/"
output_directory = "/GW/D5data-1/BioYago/healthboards/json/healthboards/sorted/"

file_list = []
users_set = set()
user_status = set()

for root, dirs, files in os.walk(starting_directory):
    try:
        for file_name in files:
            file_list.append(file_name)
            file = open(starting_directory + file_name, "r", encoding="utf8")
            contents = file.read()
            file_as_json = json.loads(contents)

            username = file_as_json["createdBy"]["name"].replace('?', 'q').replace('*', 'x')
            user_status.add(file_as_json["createdBy"]["status"])

            date_as_text = file_as_json["pubDate"]
            date = parse(date_as_text)

            if not os.path.isdir(output_directory):
                os.mkdir(output_directory)

            first_letter = username[0].upper()

            if not os.path.isdir(output_directory + first_letter):
                os.mkdir(output_directory + first_letter)

            folder_path = output_directory + first_letter + "/" + username

            if username not in users_set:
                if not os.path.isdir(folder_path):
                    os.mkdir(folder_path)
                users_set.add(username)

            new_filename = (datetime.datetime.strftime(date, "%Y%m%d") + ".json")

            if not os.path.isfile(folder_path + "/" + first_letter + "/" + new_filename):
                shutil.copyfile(starting_directory + file_name, folder_path + "/" + new_filename)

    except Exception as e:
        print(e)

# print(users_set)
print("Unique users: " + str(len(users_set)))

# print(file_list)
print("Files: " + str(len(file_list)))

print(user_status)
