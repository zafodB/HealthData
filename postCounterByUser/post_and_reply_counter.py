'''
 * Created by filip on 19/08/2019
'''

import os
import json

'''
Counts all new posts and replies for all files in the starting directory. Maps this data to a dictionary in a form
    {'user-name':
        {
        'new-posts': 123,
        'replies'  : 456
        }
    }
    
Saves this dictionary as a JSON file.
'''

# starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/sorted/"
starting_directory = "d:/downloads/json/Doctorquestions/d/user/"

user_posts_overview = {}
processed_files = 0

for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            file = open(os.path.join(root, file_name), "r", encoding="utf8")
            contents = file.read()
            file.close()
            file_as_json = json.loads(contents)

            poster_name = file_as_json['createdBy']['name']
            if poster_name not in user_posts_overview:
                user_posts_overview[poster_name] = {"n": 1, "r": 0}
            else:
                user_posts_overview[poster_name]['n'] += 1

            is_first_answer = True # First answer in the thread is the original post, which was already counted in.

            for answer in file_as_json['answers']:
                if is_first_answer:
                    is_first_answer = False
                    continue

                poster_name = answer['createdBy']['name']
                if poster_name not in user_posts_overview:
                    user_posts_overview[poster_name] = {"n": 0, "r": 1}
                else:
                    user_posts_overview[poster_name]['r'] += 1

            processed_files += 1
            if processed_files % 10000 == 0:
                print("Processed files: " + str(processed_files))

        except Exception as e:
            print("Error processing file: " + file_name + ": " + str(e))

output_file = open("post_and_replies_count.json", "w+", encoding="utf8")
json.dump(user_posts_overview, output_file)

print(user_posts_overview)
# print("test")
