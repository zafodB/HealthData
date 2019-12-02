'''
 * Created by filip on 19/08/2019
'''

import os
import json

# starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/sorted/"
starting_directory = "d:/downloads/json/ehealthforums/1/"


category_posts_overview = {}
processed_files = 0

category_map_location = "D:/OneDrive/Documents/AB Germany/ehealthforum_map.json"

category_map_file = open(category_map_location, "r", encoding="utf8")
contents = category_map_file.read()
category_map_file.close()
category_map = json.loads(contents)

for category in category_map:
    category_posts_overview[category_map[category]] = {'n': 0, 'r': 0}

aswers_no_text = 0

for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            file = open(os.path.join(root, file_name), "r", encoding="utf8")
            contents = file.read()
            file.close()
            file_as_json = json.loads(contents)

            category = file_as_json['commonCategory']
            # print(category)

            is_first_answer = True  # First answer in the thread is the original post, which was already counted in.

            for answer in file_as_json['answers']:
                if is_first_answer:
                    category_posts_overview[category]['n'] += 1
                    is_first_answer = False
                    continue
                else:
                    if 'description' in answer:
                        category_posts_overview[category]['r'] += 1
                    else:
                        aswers_no_text += 1

            processed_files += 1
            if processed_files % 10000 == 0:
                print("Processed files: " + str(processed_files))
#
        except Exception as e:
            print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))


print(category_posts_overview)
print("Answers without text: " + str(aswers_no_text))

output_file = open("categories_counts_ehealthforum.json", "w+", encoding="utf8")
json.dump(category_posts_overview, output_file)


# print(user_posts_overview)
