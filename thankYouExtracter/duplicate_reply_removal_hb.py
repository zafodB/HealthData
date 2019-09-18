'''
 * Created by filip on 17/09/2019
'''


import json, os
import traceback

starting_directory = "D:/Downloads/json/healthboards/json-sorted3/"

file_count = 0
successful_files = 0
error_files = 0
OKBLUE = '\033[94m'
ENDC = '\033[0m'

for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            # file_name = "16493.json"
            # root = "D:/Downloads/json/healthboards/json-sorted3/16"

            file = open(os.path.join(root, file_name), "r", encoding="utf8")
            contents = file.read()
            file.close()
            file_as_json = json.loads(contents)

            reply_ids = set()
            replies = []

            for reply in file_as_json['replies']:
                if reply['postId'] in reply_ids:
                    continue
                else:
                    reply_ids.add(reply['postId'])
                    replies.append(reply)

            del file_as_json['replies']

            file_as_json['replies'] = replies

            file = open(os.path.join(root, file_name), "w", encoding="utf8")
            json.dump(file_as_json, file)
            file.close()

            successful_files += 1
            file_count += 1
            if file_count % 100 == 0:
                print("Processed files: " + str(file_count))
                print(OKBLUE + "Error-free ratio: " + str((error_files / successful_files) * 100) + "%   E: " + str(
                    error_files) + ENDC)


        except Exception as e:
            print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
            traceback.print_exc()
            error_files += 1


