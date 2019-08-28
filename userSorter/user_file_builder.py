'''
Structure:

{
   "username":"someone",
   "url":"123465",
   "status":"very eHealthy"
   "weburl": "http://..."

   "posts":{
      "342823":{
         "date":"23-11-2011",
         "title":"pregnancy problem",
         "text":"this is a sample post",
         "category":"pregnancy",
         "status":"newPost"
      },
      "342887":{
         "date":"24-11-2011",
         "title":"my child is sick",
         "text":"this is another post",
         "category":"child health",
         "status":"reply"
      }
   },

}
'''

import json, os
import datetime
from dateutil.parser import *

starting_directories = []

starting_directories.append("/scratch/GW/pool0/fadamik/healthboards/sorted/2/")
starting_directories.append("/scratch/GW/pool0/fadamik/healthboards/sorted/3/")
starting_directories.append("/scratch/GW/pool0/fadamik/healthboards/sorted/4/")
starting_directories.append("/scratch/GW/pool0/fadamik/healthboards/sorted/5/")
# starting_directory = "D:/Downloads/json/healthboards/" + "6/"
# output_directory = "D:/Downloads/json/healthboards/" + "6-sorted/"
output_directory = "/scratch/GW/pool0/fadamik/healthboards/users/"

# if not os.path.isdir(output_directory):
#     os.mkdir(output_directory)


def write_out_users(users):
    for user in users:
        user_folder_name = str(user // 100)

        if not os.path.isdir(os.path.join(output_directory, user_folder_name)):
            os.mkdir(os.path.join(output_directory, user_folder_name))

        full_path = os.path.join(output_directory, user_folder_name, str(user) + ".json")

        user_file_json = {}

        if os.path.exists(full_path):
            user_file = open(full_path, "r", encoding="utf8")
            user_contents = user_file.read()
            user_file_json = json.loads(user_contents)
            user_file.close()

        user_file_json.update(users[user])
        user_file = open(full_path, "w", encoding="utf8")
        json.dump(user_file_json, user_file)
        user_file.close()

    return None


def process_files(starting_directory):

    processed_files = 0
    users = {}

    for root, dirs, files in os.walk(starting_directory):
        for file_name in files:
            try:
                file = open(os.path.join(root, file_name), "r", encoding="utf8")
                contents = file.read()
                file_as_json = json.loads(contents)
                file.close()

                document_id = file_as_json['docid'] * 10
                category = file_as_json['commonCategory']
                title = file_as_json['title']

                original_poster_id = file_as_json['createdBy']['url']

                users[original_poster_id] = {'name': file_as_json['createdBy']['name'],
                                             'status': file_as_json['createdBy']['status']}

                answer_nr = 1

                for answer in file_as_json['answers']:
                    activity_nr = document_id + answer_nr

                    if 'description' not in answer:
                        continue

                    if answer_nr == 1:
                        users[original_poster_id]['activity'] = {activity_nr: {}}

                        users[original_poster_id]['activity'][activity_nr]['title'] = title
                        users[original_poster_id]['activity'][activity_nr]['description'] = answer['description']
                        users[original_poster_id]['activity'][activity_nr]['pubDate'] = parse(answer['pubDate']).isoformat()
                        users[original_poster_id]['activity'][activity_nr]['category'] = category
                        users[original_poster_id]['activity'][activity_nr]['newPost'] = True

                    else:
                        user_id = answer['createdBy']['url']

                        if user_id not in users:
                            users[user_id] = {'name': answer['createdBy']['name'], 'status': answer['createdBy']['status'],
                                              'activity': {activity_nr: {}}}
                        else:
                            users[user_id]['activity'][activity_nr] = {}

                        users[user_id]['activity'][activity_nr]['title'] = title
                        users[user_id]['activity'][activity_nr]['description'] = answer['description']
                        users[user_id]['activity'][activity_nr]['pubDate'] = None
                        users[user_id]['activity'][activity_nr]['category'] = category
                        users[user_id]['activity'][activity_nr]['newPost'] = False

                    answer_nr += 1

                processed_files += 1

                if processed_files % 1000 == 0:
                    print("Processed files: " + str(processed_files))
                    write_out_users(users)
                    users = {}
                # print(users)

            except Exception as e:
                print("Error processing file: " + file_name + ": " + str(e))

    if users:
        write_out_users(users)


for directory in starting_directories:
    process_files(directory)
