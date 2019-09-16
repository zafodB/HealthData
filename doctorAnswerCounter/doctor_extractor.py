'''
 * Created by filip on 13/09/2019
'''

'''
 * Created by filip on 15/08/2019
'''
import hashlib

from bs4 import BeautifulSoup
import json, os
import re
import datetime
import traceback
from dateutil.parser import *

forum = "ehealthforum"

# starting_directory = "/GW/D5data-1/BioYago/ehealthforum/html/"
starting_directory = "D:/Downloads/json/ehealthforums/html2/"
output_directory = "/scratch/GW/pool0/fadamik/download/"
# output_directory = "D:/Downloads/json/ehealthforums/html-sorted/"

def find_doctor(file_name):

    soup = BeautifulSoup(open(file_name, "rb"), "html.parser")
    doctor_box = soup.find("div", {"class": "vt_container"}).find("div", {"class": "vt_left"}).find("span",{"class": "postfix-md"})
    return doctor_box is not None

file_count = 0
successful_files = 0
error_files = 0
OKBLUE = '\033[94m'
ENDC = '\033[0m'


for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            if find_doctor(os.path.join(root, file_name)):
                print(os.path.join(root, file_name))

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
