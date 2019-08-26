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

# starting_directory = "/GW/D5data-1/BioYago/healthboards/json/healthboards/5/"
starting_directory = "D:/Downloads/json/healthboards/" + "1/"
# output_directory = "D:/Downloads/json/healthboards/" + "1-sorted/"
# output_directory = "/scratch/GW/pool0/fadamik/ehealthforum/sorted/"

# if not os.path.isdir(output_directory):
#     os.mkdir(output_directory)

for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            file = open(starting_directory + file_name, "r", encoding="utf8")
            contents = file.read()
            file_as_json = json.loads(contents)
            file.close()

            users = {}

            original_poster = {}

            document_id = file_as_json['docid'] * 10
            category = file_as_json['commonCategory']
            title = file_as_json['title']

            original_poster['name'] = file_as_json['createdBy']['name']
            original_poster['status'] = file_as_json['createdBy']['status']
            original_poster['url'] = file_as_json['createdBy']['url']

            answer_nr = 1

            for answer in file_as_json['answers']:
                activity_nr = document_id + answer_nr

                if answer_nr == 1:
                    original_poster['activity'] = {activity_nr: {}}

                    original_poster['activity'][activity_nr]['title'] = title
                    original_poster['activity'][activity_nr]['description'] = answer['description']
                    original_poster['activity'][activity_nr]['pubDate'] = parse(answer['pubDate']).isoformat()
                    original_poster['activity'][activity_nr]['category'] = category
                    original_poster['activity'][activity_nr]['newPost'] = True

                else:
                    if 'description' not in answer:
                        continue

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

            print(original_poster)
            print(users)


        except Exception as e:
            print("Error processing file: " + file_name + ": " + str(e))
