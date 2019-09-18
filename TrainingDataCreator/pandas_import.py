'''
 * Created by filip on 18/09/2019
'''

import json, os
import pandas as pd
import numpy as np
import traceback

# starting_directory = "D:/Downloads/json/healthboards/html-sorted/"
starting_directory = "D:/Downloads/json/ehealthforums/pairs/"

file_count = 0
successful_files = 0
error_files = 0
OKBLUE = '\033[94m'
ENDC = '\033[0m'

df = pd.read_csv("D:/Downloads/json/ehealthforums/pairs/pairs-all.txt", sep='\t')
# df = pd.DataFrame()

# for root, dirs, files in os.walk(starting_directory):
#     for file_name in files:
#         try:
#
#             to_be_appended = pd.read_csv(os.path.join(root, file_name), sep='\t')
#
#             df = df.append(to_be_appended, sort=False)
#
#             successful_files += 1
#             file_count += 1
#             if file_count % 1 == 0:
#                 print("Processed files: " + str(file_count))
#                 print(OKBLUE + "Error-free ratio: " + str((error_files / successful_files) * 100) + "%   E: " + str(
#                     error_files) + ENDC)
#
#         except Exception as e:
#             print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
#             traceback.print_exc()
#             error_files += 1

df.to_csv("D:/Downloads/json/healthboards/pairs/df-expport.txt", sep='\t')
print(df)
