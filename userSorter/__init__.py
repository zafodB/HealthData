'''
 * Created by filip on 07/08/2019
'''

import json
import os
import shutil
import datetime
from dateutil.parser import *

# file = open("D:/Downloads/json/ehealthforums/.json", "r")

file_list = []
users_set = set()
user_status = set()

for root, dirs, files in os.walk("D:/Downloads/json/healthboards/1/"):
    try:
        for file_name in files:
            file_list.append(file_name)
            file = open("D:/Downloads/json/healthboards/1/" + file_name, "r", encoding="utf8")
            contents = file.read()
            file_as_json = json.loads(contents)

            username = file_as_json["createdBy"]["name"].replace('?', 'q').replace('*','x')
            user_status.add(file_as_json["createdBy"]["status"])

            date_as_text = file_as_json["pubDate"]
            date = parse(date_as_text)

            folder_path = "D:/Downloads/json/healthboards/sorted/" + username

            if not username in users_set:
                os.mkdir(folder_path)
                users_set.add(username)

            new_filename = (datetime.datetime.strftime(date, "%Y%m%d") + ".json")

            if not os.path.isfile(folder_path + "/" + new_filename):
                shutil.copyfile("D:/Downloads/json/healthboards/1/" + file_name, folder_path + "/" + new_filename)

    except Exception as e: print(e)

# print(users_set)
print("Unique users: " + str(len(users_set)))

# print(file_list)
print("Files: " + str(len(file_list)))

print(user_status)
