"""
 * Created by filip on 15/08/2019

 Scrapes HTML files of HealthBoards and saves the relevant information into JSON files. One thread in the forum is
 represented by one JSON file.

 Creates pairs file with first-post:reply structure, writing out all replies that received at least one vote and their
 corresponding first post (used for query:document pairs)
"""

import json
import os
import re
import traceback

from bs4 import BeautifulSoup
from dateutil.parser import *

forum = "healthboards"

# category_map_location = "D:/OneDrive/Documents/AB Germany/health_data/healthboards_map2.json"
# starting_directory = "D:/Downloads/json/healthboards/cerebral-palsy/"
# output_directory = "D:/Downloads/json/healthboards/html-sorted/"

category_map_location = "healthboards_map.json"
starting_directory = "/GW/D5data-1/BioYago/healthboards/boards/"
output_directory = "/scratch/GW/pool0/fadamik/healthboards/json-sorted4/"
pairs_directory = "pairs/"


# Load the file that maps forum-specific categories to unified list of categories across forums.
def load_category_map(location):
    category_map_file = open(location, "r", encoding="utf8")
    contents = category_map_file.read()
    category_map_file.close()
    return json.loads(contents)


# Extract all features of interest from the given file
def extract_all_items(file_name, file_location, pairs_file):
    # Extract original category of the post.
    def extract_origin_category(soup):
        navbars = soup.find_all("span", {"class": "navbar"})
        category = navbars[-1].getText()[2:]
        return category

    # Extract thread ID of the thread. This ID should be forum unique.
    def extract_thread_id(soup):
        id_class = soup.find("td", {"id": "linkbacktools"}).findChildren()[0]
        thread_id = id_class.attrs['href'][3:].split("-")[0]
        return thread_id

    # Extract the thread name (title of the thread)
    def extract_thread_name(soup):
        strong = soup.find("div", {"class": "navbar"}).findChildren()[-1]
        name = strong.getText()
        return name

    # Lookup the original category in the category map
    def map_common_category(origin_category):
        category = category_map[origin_category]
        return category

    # Extract the author of the post and related info, like username, status, location, gender, join date,
    # total number of posts (if provided by the user)
    def extract_created_by(post_id):
        gender = None
        location = None
        join_date = None
        total_posts = None

        current_tag = thread_html.find("div", {"id": "postmenu_" + post_id})
        if current_tag.findChildren():
            username = current_tag.findChildren()[0].getText()
        else:
            username = current_tag.getText().strip().replace('/n', '')

        current_tag = current_tag.find_next_sibling()
        status = current_tag.getText().strip()

        if status != "Guest":
            current_tag = current_tag.find_next_sibling()
            gender_text = current_tag.getText().strip().replace('/n', '')
            if gender_text:
                gender = gender_text[1:-1]
                if gender == "male" or gender == "female":
                    if current_tag.find_next_sibling():
                        current_tag = current_tag.find_next_sibling()
                    else:
                        current_tag = current_tag.findChild()
                else:
                    gender = None

            if current_tag.find("a"):
                has_image = current_tag.find("a").find("img")
                if has_image:
                    current_tag = current_tag.find_next_sibling()

            for child in current_tag.findChildren():

                element_text = child.getText()

                if element_text:
                    element_text = element_text.strip().replace('/n', '')

                    if element_text[0:5] == "Join ":
                        date_as_text = "01 " + element_text[11:]
                        join_date = parse(date_as_text).isoformat()
                    elif element_text[0:5] == "Posts":
                        number_posts = element_text[7:].replace(',', '').replace(' ', '')

                        try:
                            total_posts = int(number_posts)
                        except ValueError as ve:
                            continue

                    elif element_text[0:8] == "Location":
                        location = element_text[10:]

        return {
            "username": username,
            "status": status,
            "gender": gender,
            "location": location,
            "totalPosts": total_posts,
            "joinDate": join_date
        }

    # Extract the main text of the post, removing quotes from the text.
    def extract_post_message(post_html, post_id):
        children = post_html.find("div", {"id": "post_message_" + post_id}).findChildren()

        found_quote = False

        if children:
            for child in children:
                if child.name == "div":
                    found_quote = True
                    break

        if found_quote:
            message = ' '.join(
                t.strip() for t in post_html.find("div", {"id": "post_message_" + post_id})(text=True, recursive=False))

        else:
            message = post_html.find("div", {"id": "post_message_" + post_id}).getText().strip()

        message = re.sub(' +', ' ', message).replace('\n', '')
        return message, found_quote

    # Extract the date of the when comment was added.
    def extract_post_date(post_html):
        date_as_text = post_html.find("td", {"class": "thead"}).getText().strip()
        post_date = parse(date_as_text)
        return post_date.isoformat()

    # Extract the thank-you votes casted on this post
    def extract_thank_yous(post_html, post_id):
        thanks_box = post_html.find("div", {"id": "post_thanks_box_" + post_id}).find("td", {"class": "alt1"})

        thank_you_list = []

        if thanks_box:
            for thank_you_html in thanks_box.find("div").find_all("a"):
                thank_user = thank_you_html.getText()
                thank_date_text = thank_you_html.next_sibling.strip().replace('(', '').replace(')', '').replace(',', '')
                thank_date = parse(thank_date_text, dayfirst=False)

                thank_you = {"name": thank_user, "date": thank_date.isoformat()}
                thank_you_list.append(thank_you)
        return thank_you_list

    # Extract the 'support' votes casted on this post
    def extract_support_hugs(post_html, post_id):
        support_hugs_box = post_html.find("div", {"id": "post_hugs_box_" + post_id})

        if support_hugs_box:
            support_hugs_box = support_hugs_box.find("td", {"class": "alt1"})

        support_hugs_list = []

        if support_hugs_box:
            for hug_html in support_hugs_box.find("div").find_all("a"):
                hug_user = hug_html.getText()
                hug_date_text = hug_html.next_sibling.strip().replace('(', '').replace(')', '').replace(',', '')
                hug_date = parse(hug_date_text, dayfirst=False)

                thank_you = {"name": hug_user, "date": hug_date.isoformat()}
                support_hugs_list.append(thank_you)
        return support_hugs_list

    thread_html = BeautifulSoup(open(file_location, "rb"), "html.parser")

    thread_id = extract_thread_id(thread_html)
    thread_name = extract_thread_name(thread_html)
    source = forum
    orininal_file = file_name
    origin_category = extract_origin_category(thread_html)
    common_category = map_common_category(origin_category)
    thread_thank_you_count = 0
    thread_support_count = 0
    thread_helpful_count = 0
    unique_users = set()

    posts = thread_html.find_all("div", {"id": re.compile("edit*")})
    reply_count = max(index for index, post in enumerate(posts)) + 1
    replies = []

    # Loop through all structures that could possibly be posts
    for index, post in enumerate(posts):
        post_order = index
        post_id = post.get("id")[4:]

        created_by = extract_created_by(post_id)
        post_text, has_quotes = extract_post_message(post, post_id)
        post_date = extract_post_date(post)
        unique_users.add(created_by['username'])
        thank_yous = extract_thank_yous(post, post_id)
        post_thank_you_count = len(thank_yous)
        thread_thank_you_count += post_thank_you_count
        support_hugs = extract_support_hugs(post, post_id)
        post_hugs_count = len(support_hugs)
        thread_support_count += post_hugs_count

        md_reply = False
        helpful = []
        post_helpful_count = 0

        replies.append({
            "postId": post_id,
            "createdBy": created_by,
            "mdReply": md_reply,
            "postOrder": post_order,
            "postDate": post_date,
            "postText": post_text,
            "hasQuotes": has_quotes,
            "postSupportCount": post_hugs_count,
            "postThankYouCount": post_thank_you_count,
            "postHelpfulCount": post_helpful_count,
            "thankYous": thank_yous,
            "supportHugs": support_hugs,
            "helpful": helpful
        })

        # Write out data to a special file the reply has at least one vote.
        # (This is a side feature and not part of extracting elements to the JSON files)
        tab_char = "\t"
        if (post_thank_you_count > 0 or post_hugs_count > 0) and index > 0:
            pairs_file.write(
                replies[0]["postText"] + tab_char +
                replies[0]["createdBy"]["username"] + tab_char +
                replies[0]["createdBy"]["status"] + tab_char +
                common_category + tab_char +
                post_text + tab_char +
                str(has_quotes) + tab_char +
                created_by["username"] + tab_char +
                created_by["status"] + tab_char +
                common_category + tab_char +
                str(post_thank_you_count) + tab_char +
                str(post_hugs_count) + tab_char +
                str(post_helpful_count) + tab_char +
                "votes" + tab_char +
                str(True) + "\n"
            )

    md_reply_count = 0
    unique_user_count = len(unique_users)

    output = {
        "threadId": thread_id,
        "title": thread_name,
        "mdReplyCount": md_reply_count,
        "replyCount": reply_count,
        "threadThankYouCount": thread_thank_you_count,
        "threadHelpfulCount": thread_helpful_count,
        "threadSupportCount": thread_support_count,
        "commonCategory": common_category,
        "originCategory": origin_category,
        "source": source,
        "originalFile": [orininal_file],
        "uniqueUsers": unique_user_count,
        "replies": replies
    }

    return thread_id, output

# Some threads could be spanning multiple files. If this is the case and a JSON file for particular thread has already
# been created, then update this JSON file instead of writing over it.
def update_content(old_json, new_json):
    if new_json['originalFile'][0] in old_json['originalFile']:
        return None

    reply_ids = set()
    for reply in old_json['replies']:
        reply_ids.add(reply['postId'])

    for reply in new_json['replies']:
        if reply['postId'] in reply_ids:
            continue
        else:
            old_json['replies'].append(reply)

    unique_users = set()
    for reply in old_json['replies']:
        unique_users.add(reply['createdBy']['username'])

    old_json['uniqueUsers'] = len(unique_users)

    old_json['replyCount'] = len(old_json['replies'])
    old_json['threadThankYouCount'] += new_json['threadThankYouCount']
    old_json['threadSupportCount'] += new_json['threadSupportCount']

    old_json['originalFile'].append(new_json['originalFile'][0])
    return old_json


# Write out the extracted information onto an JSON file
def write_out_file(file_name, contents):
    folder_name = str(int(file_name) // 1000)

    if not os.path.isdir(os.path.join(output_directory, folder_name)):
        os.mkdir(os.path.join(output_directory, folder_name))

    full_path = os.path.join(output_directory, folder_name, str(file_name) + ".json")

    if os.path.exists(full_path):
        existing_file = open(full_path, "r", encoding="utf8")
        existing_json = json.loads(existing_file.read())
        existing_file.close()

        contents = update_content(existing_json, contents)

    if contents:
        thread_file = open(full_path, "w", encoding="utf8")
        json.dump(contents, thread_file)
        thread_file.close()


file_count = 0
successful_files = 0
error_files = 0
OKBLUE = '\033[94m'
ENDC = '\033[0m'

category_map = load_category_map(category_map_location)

pairs_file = open(os.path.join(pairs_directory, "pairs0.txt"), "a+", encoding="utf8")

# Walk over HTML files in the starting directory.
for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            pattern = re.compile("index")
            if not pattern.match(file_name):
                output_name, output_contents = extract_all_items(file_name, os.path.join(root, file_name), pairs_file)

                write_out_file(output_name, output_contents)

            successful_files += 1
            file_count += 1

            # Write out current progress
            if file_count % 100 == 0:
                print("Processed files: " + str(file_count))
                print(OKBLUE + "Error-free ratio: " + str((error_files / successful_files) * 100) + "%   E: " + str(
                    error_files) + ENDC)

            # Write out current progress
            if file_count % 10000 == 0:
                pairs_file.close()
                pairs_file = open(os.path.join(pairs_directory, "pairs" + str(file_count / 10000) + ".txt"), "a+",
                                  encoding="utf8")

        # If an exception occurs during processing the HTML file, skip it and move to the next one.
        except Exception as e:
            print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
            traceback.print_exc()
            error_files += 1
