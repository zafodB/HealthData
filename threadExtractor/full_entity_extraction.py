'''
 * Created by filip on 15/11/2019
'''

import os
import platform
import json
import re
import traceback

on_server = platform.system() == "Linux"

# Determine file location for running on server and runnning locally
if on_server:
    starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated"

else:
    starting_directory = "d:/downloads/json/ehealthforum/json-annotated"

processed_files = 0

for root, dir, files in os.walk(starting_directory):
    for filename in files:
        try:
            with open(os.path.join(root, filename), "r", encoding="utf8") as file:
                contents = json.load(file)

            updated_file = False

            for reply in contents['replies']:
                pattern = re.compile("\[\[C[0-9]+\|[\w\s]{1,}\]\]")
                if 'annotatedText' in reply:
                    annotations = re.findall(pattern, reply['annotatedText'])

                    for annotation in annotations:
                        if annotation not in reply['annotationsFull']:
                            reply['annotationsFull'].append(annotation)
                            updated_file = True

            if updated_file:
                with open(os.path.join(root, filename), "w+", encoding="utf8") as file:
                    json.dump(contents, file)

                print("Updated file: " + os.path.join(root, filename))

            processed_files += 1

            if processed_files % 10000 == 0:
                print("Processed files: " + str(processed_files))

        except Exception as e:
            traceback.print_exc()
            print("In file: " + os.path.join(root, filename))
