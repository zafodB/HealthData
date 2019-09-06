'''
 * Created by filip on 29/08/2019
'''

import os
from bs4 import BeautifulSoup
import re

starting_directory = "D:/Downloads/json/html/"

posts_with_votes = 0
votes_total = 0

for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            ## Extract thanks and supports from healthboards
            soup = BeautifulSoup(open(os.path.join(root, file_name)), "html.parser")
            posts = soup.find_all("div", {"id": re.compile("edit*")})

            is_first_post = True

            for post in posts:
                if is_first_post:
                    is_first_post = False
                    continue

                post_id = post.get("id")[4:]
                post_menu = soup.find("div", {"id": "postmenu_"+post_id})
                username = post_menu.findChildren()[0].text
                post_message = soup.find("div", {"id": "post_message_"+post_id})
                supports = soup.find("div", {"id": "post_hugs_box_"+post_id})

                has_votes = False

                if len(supports.text) > 0:
                    # print("+1 support")
                    text = supports.text.split("The following ")[-1][0:4]
                    if text == "user":
                        votes_total += 1
                        has_votes = True
                    elif text[0].isdigit():
                        votes_total += int(text[0],10)
                        has_votes = True
                    # print(text)

                # thanks = soup.find("div", {"id": "post_thanks_box_"+post_id})

                # if len(thanks.text) > 0:
                    # print(str(thanks.text))
                    # print("+1 thanks")



        except Exception as e:
            print("Error processing file: " + file_name + ": " + str(e))

print(votes_total)
