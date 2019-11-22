"""
 * Created by filip on 15/08/2019

 Scrapes HTML files of eHealthForum and saves the relevant information into JSON files. One thread in the forum is
 represented by one JSON file. The name of the JSON file represents the thread ID extracted from the HTML. If the
 thread ID could not be extracted, hash value of the post title is used.
"""

import hashlib
import json
import os
import re
import traceback

from bs4 import BeautifulSoup
from dateutil.parser import *

forum = "ehealthforum"

# category_map_location = "D:/OneDrive/Documents/AB Germany/health_data/ehealthforum_map.json"
# starting_directory = "D:/Downloads/json/ehealthforums/html2/"
# output_directory = "D:/Downloads/json/ehealthforums/html-sorted/"

category_map_location = "ehealthforum_map.json"
starting_directory = "/GW/D5data-1/BioYago/ehealthforum/health/"
output_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-sorted2/"


# Load the file that maps forum-specific categories to unified list of categories across forums.
def load_category_map(location):
    category_map_file = open(location, "r", encoding="utf8")
    contents = category_map_file.read()
    category_map_file.close()
    return json.loads(contents)


# Extract all features of interest from the given file
def extract_all_items(file_name, file_location):
    # Extract thread ID of the thread. This ID should be forum unique. Sometimes this ID could not be extracted,
    # in which case hash of name would be used`
    def extract_thread_id(soup, name):
        id_container = soup.find("input", {"name": "reply_to_topic_id"})
        if id_container:
            return id_container['value']
        else:
            name_hash = hashlib.md5(name.encode('utf-8'))
            return str(int.from_bytes(name_hash.digest()[:3], byteorder='big'))

    # Extract original category of the post.
    def extract_origin_category(soup):
        category = soup.find("div", {"class": "vt_h2"}).findChild().findChildren()[-1].getText().replace(" Forum", "")

        return category

    # Extract the thread name (title of the thread)
    def extract_thread_name(soup):
        name = soup.find("h1", {"class": "caps", "id": "page_h1"}).getText()
        name = re.sub(" \(Page [0-9]+\)", "", name)

        return name

    # Lookup the original category in the category map
    def map_common_category(origin_category):
        category = category_map[origin_category]
        return category

    # Extract ID of the post. Post ID may not be unique for all forum posts.
    def extract_post_id(post_body_html, is_first_post):
        post_id = None

        if not is_first_post and post_body_html.find("div", {"class": "vt_first_message_body"}):
            is_first_post = True

        if is_first_post:
            post_container = post_body_html.find("div", {"class": "vt_usefull_post_form_holder"})
            if post_container:
                post_id = post_container.find()['id'].split("_")[-1]
        else:
            try:
                post_id = post_body_html.find("div", {"class": "vt_bottom_post_links"}).find_next_sibling()
                post_id = post_id['id'].split("_")[-1]
            except AttributeError as ae:
                return None
        return post_id

    # Extract the main text of the post, filtering out quotes and removing entries that have been either deleted or
    # are being deleted by the forum administrators
    def extract_post_text(post_body_html):
        has_quotes = candidate.find("td", {"class": "quote"})

        if not has_quotes:
            has_quotes = False
            post_text = candidate.find("div", {"class": "vt_post_body"}).getText().strip().replace("\n", "")

            if post_text:
                post_text = re.sub(" +", " ", post_text)

                if post_text.find("This post has been removed because") != -1:
                    return None, None
                elif post_text.find("This post is being reviewed") != -1:
                    return None, None

        else:
            has_quotes = True
            post_text = candidate.find("div", {"class": "KonaBody"}).findAll(recursive=False)[-1]
            post_text = post_text.getText().strip().replace("\n", "")
            post_text = re.sub(" +", " ", post_text)

        return post_text, has_quotes

    # Extract the author of the post and related info, like username and status.
    def extract_created_by(post_html, is_first_post):
        if is_first_post:
            username = post_html.find("span", {"class": "vt_asked_by_user"}).getText().strip()
        else:
            username = post_html.find("div", {"class": "vt_asked_by_user"}).getText().strip()

        if post_html.find("span", {"class": "postfix-md"}) and not is_first_post:
            status = "md"
        else:
            status = post_html.find("span", {"class": "vt_user_rank"})
            if status:
                status = status.getText().strip()

            if len(status) == 0:
                status = None

        return {
            "username": username,
            "status": status,
            "gender": None,
            "location": None,
            "totalPosts": None,
            "joinDate": None
        }

    # Extract the date of the when comment was added.
    def extract_post_date(post_html, is_first_post):
        if is_first_post:
            date_text = post_html.find("span", {"class": "vt_first_timestamp"}).getText().strip()
        else:
            date_text = post_html.find("div", {"class": "vt_reply_timestamp"}).getText().strip()
            date_text = re.sub("replied ", "", date_text)

        return parse(date_text).isoformat()

    # Extract votes casted on this post ('helpful' votes in this forum)
    def extract_helpful_marks(post_html):
        helpful_marks = []

        thank_you_box = post_html.find("span", {"class": "gensmall"})
        if thank_you_box:
            children = thank_you_box.findChildren()
            for child in children:
                username = child.getText()

                helpful_marks.append({
                    "name": username,
                    "date": None
                })

        return helpful_marks

    thread_html = BeautifulSoup(open(file_location, "rb"), "html.parser")

    thread_name = extract_thread_name(thread_html)
    thread_id = extract_thread_id(thread_html, thread_name)
    source = forum
    orininal_file = file_name
    origin_category = extract_origin_category(thread_html)
    common_category = map_common_category(origin_category)
    thread_helpful_count = 0
    unique_users = set()
    md_reply_count = 0
    replies = []
    post_ids = set()

    post_candidates = thread_html.find_all("div", {"class": "vt_post_holder"})

    # Loop through all structures that could possibly be posts
    for index, candidate in enumerate(post_candidates):
        # print(index)
        is_first_post = index == 0

        post_id = extract_post_id(candidate, is_first_post)
        if not is_first_post and post_id is None:
            post_id = thread_id + "0" + index
            post_ids.add(post_id)
        elif (is_first_post and post_id is None) or post_id in post_ids:
            continue
        else:
            post_ids.add(post_id)

        post_text, has_quotes = extract_post_text(candidate)
        if not post_text:
            continue

        post_order = index

        created_by = extract_created_by(candidate, is_first_post)
        if created_by['status'] == "md":
            md_reply = True
            md_reply_count += 1
        else:
            md_reply = False

        unique_users.add(created_by['username'])
        post_date = extract_post_date(candidate, is_first_post)

        helpful = extract_helpful_marks(candidate)
        post_helpful_count = len(helpful)

        replies.append({
            "postId": post_id,
            "createdBy": created_by,
            "mdReply": md_reply,
            "postOrder": post_order,
            "postDate": post_date,
            "postText": post_text,
            "hasQuotes": has_quotes,
            "postSupportCount": 0,
            "postThankYouCount": 0,
            "postHelpfulCount": post_helpful_count,
            "thankYous": [],
            "supportHugs": [],
            "helpful": helpful
        })

    reply_count = len(replies)
    unique_user_count = len(unique_users)

    output = {
        "threadId": thread_id,
        "title": thread_name,
        "mdReplyCount": md_reply_count,
        "replyCount": reply_count,
        "threadThankYouCount": 0,
        "threadSupportCount": 0,
        "threadHelpfulCount": thread_helpful_count,
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

    for reply in new_json['replies']:
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
        print("File already exists: " + full_path)

    if contents:
        thread_file = open(full_path, "w", encoding="utf8")
        json.dump(contents, thread_file)
        thread_file.close()
    else:
        print("No update needed for file")


file_count = 0
successful_files = 0
error_files = 0
OKBLUE = '\033[94m'
ENDC = '\033[0m'

category_map = load_category_map(category_map_location)
unprocessed_files = []
unprocessed_total = 0

# Walk over HTML files in the starting directory.
for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            pattern = re.compile("topic[0-9]*_[0-9]*")
            pattern2 = re.compile("_medical_questions_")

            if pattern.match(file_name) or pattern2.match(file_name):
                unprocessed_files.append(os.path.join(root, file_name))
                unprocessed_total += 1
            else:
                output_name, output_contents = extract_all_items(file_name, os.path.join(root, file_name))
                write_out_file(output_name, output_contents)

            successful_files += 1
            file_count += 1
            if file_count % 100 == 0:
                unprocessed_list = open("unprocessed.txt", "a+")
                json.dump(unprocessed_files, unprocessed_list)
                unprocessed_list.close()
                unprocessed_files = []

                # Write out current progress
                print("Unprocessed files: " + str(unprocessed_total) + ". Processed files: " + str(file_count))
                print(OKBLUE + "Error-free ratio: " + str((error_files / successful_files) * 100) + "%   E: " + str(
                    error_files) + ENDC)

        # If an exception occurs during processing the HTML file, skip it and move to the next one.
        except Exception as e:
            print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
            traceback.print_exc()
            error_files += 1
