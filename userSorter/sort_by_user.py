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

# starting_directory = "/GW/D5data-1/BioYago/healthboards/json/healthboards/5/"
starting_directory = "D:/Downloads/json/healthboards/" + "1/"
output_directory = "D:/Downloads/json/healthboards/" + "1-sorted/"
# output_directory = "/scratch/GW/pool0/fadamik/ehealthforum/sorted/"

if not os.path.isdir(output_directory):
    os.mkdir(output_directory)

file_list = []
users_set = set()
user_status = set()

# walk through the files in the starting directory
for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            # Open file
            file_list.append(file_name)
            file = open(starting_directory + file_name, "r", encoding="utf8")
            contents = file.read()
            file_as_json = json.loads(contents)

            # Extract the OP (original poster) and filter for unusable characters
            # (characters which cannot be in filepath)
            username = file_as_json["createdBy"]["name"].replace('?', 'q')\
                .replace('*', 'x')\
                .replace(':', 'c')\
                .replace('/', 'f',)\
                .replace('\\', 'b')
            user_status.add(file_as_json["createdBy"]["status"])

            # Extract posting date
            date_as_text = file_as_json["pubDate"]
            date = parse(date_as_text)

            # Create directory with the first letter of the username (directory 'A', 'B', 'C' ...)
            first_letter = username[0].upper()
            if not os.path.isdir(output_directory + first_letter):
                os.mkdir(output_directory + first_letter)

            folder_path = output_directory + first_letter + "/" + username

            # Add user to set of users
            if username not in users_set:
                if not os.path.isdir(folder_path):
                    os.mkdir(folder_path)
                users_set.add(username)

            # Determine the filename
            new_filename = (datetime.datetime.strftime(date, "%Y%m%d") + ".json")
            new_path = folder_path + "/" + new_filename

            # Copy the file to the new location under the new filename
            if not os.path.isfile(new_path):
                shutil.copyfile(starting_directory + file_name, new_path)
            # If the user made two posts on the same date, differentiate them by adding a single letter to the filename
            else:
                counter = 97  # ASCII code for letter "a"
                while os.path.isfile(new_path):
                    counter += counter

                    new_filename = (datetime.datetime.strftime(date, "%Y%m%d") + chr(counter) + ".json")
                    new_path = folder_path + "/" + new_filename

                    if not os.path.isfile(new_path):
                        shutil.copyfile(starting_directory + file_name, new_path)
                        break

            if len(file_list) % 10000 == 0:
                print("Processed files: " + str(len(file_list)))

        except Exception as e:
            print("Error processing file: " + file_name + ": " + str(e))

# print(users_set)
print("Unique users: " + str(len(users_set)))

# print(file_list)
print("Files: " + str(len(file_list)))

print(user_status)
