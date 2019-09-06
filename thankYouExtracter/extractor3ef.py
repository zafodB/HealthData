'''
 * Created by filip on 29/08/2019
'''

import os
from bs4 import BeautifulSoup
import re

starting_directory = "D:/Downloads/json/ehealthforums/html/"

for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            soup = BeautifulSoup(open(os.path.join(root, file_name)), "html.parser")
            thanks = soup.find_all("div", {"class": re.compile("row1 vt_ty_holder")})
            for i in thanks:
                id_post = i.find_previous_sibling().find_previous_sibling().get("id").split("_")[-1]
                print("Post with id ", id_post, " received at least one like")

        except Exception as e:
            print("Error processing file: " + file_name + ": " + str(e))
