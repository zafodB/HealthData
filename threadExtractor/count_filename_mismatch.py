'''
 * Created by filip on 17/12/2019
'''


import os
import platform
import json
import traceback
import re

on_server = platform.system() == "Linux"

# Determine file location for running on server and runnning locally
if on_server:
    starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated/"
    output_directory = "/home/fadamik/Documents/"


else:
    starting_directory = "D:/Downloads/json/ehealthforum/json-annotated"
    output_directory = "D:/Downloads/json/ehealthforum/"

mismatch_count = 0
with open('/home/fadamik/Documents/renamed_threads_ehf.txt', 'w+', encoding='utf8') as rename_list:

    rename_list.write('oldname\tnewname\n')

    for root, dirs, files in os.walk(starting_directory):
        for file_name in files:
            with open(os.path.join(root, file_name), 'r', encoding='utf8') as file:
                contents = json.load(file)

            name_number = file_name.replace('.json', '')
            if contents['threadId'] != name_number:
                # print("ThreadId: " + contents['threadId'] + ", filename: " + name_number)
                rename_list.write(contents['threadId'] + '\t' + name_number + '\n')
                contents['threadId'] = name_number

                with open(os.path.join(root, file_name), 'w', encoding='utf8') as file:
                    json.dump(contents, file)

                    print("ThreadId: " + contents['threadId'] + ", filename: " + name_number)

                mismatch_count += 1

print('Total mismatch files: ' + str(mismatch_count))
