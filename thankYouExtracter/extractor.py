'''
 * Created by filip on 15/08/2019
'''

from bs4 import BeautifulSoup
import json
import re
import datetime
from dateutil.parser import *

category_map_location = "D:/OneDrive/Documents/AB Germany/health_data/healthboards_map2.json"
file_location = "51.html"
# file_location = "d:/downloads/json/html/64T.html"

forum = "healthboards"


# forum = "ehealthforum"


def extract_origin_category(soup):
    navbars = soup.find_all("span", {"class": "navbar"})
    category = navbars[-1].getText()[2:]

    return category


def extract_thread_id(soup):
    id_class = soup.find("td", {"class": "vbmenu_control"}).findChildren()[0]
    thread_id = id_class.attrs['href'][3:].split("-")[0]
    return thread_id


def extract_thread_name(soup):
    strong = soup.find("div", {"class": "navbar"}).findChildren()[-1]
    name = strong.getText()
    return name


def map_common_category(origin_category):
    category_map_file = open(category_map_location, "r", encoding="utf8")
    contents = category_map_file.read()
    category_map_file.close()
    category_map = json.loads(contents)
    category = category_map[origin_category]

    return category


def extract_created_by(post_id):
    gender = None
    location = None
    join_date = None
    total_posts = None

    current_tag = thread_html.find("div", {"id": "postmenu_" + post_id})
    username = current_tag.findChildren()[0].text

    current_tag = current_tag.find_next_sibling()
    status = current_tag.getText().strip()

    current_tag = current_tag.find_next_sibling()
    gender_text = current_tag.getText().strip().replace('/n', '')
    if gender_text:
        gender = gender_text[1:-1]

    current_tag = current_tag.find_next_sibling()

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


def extract_post_message(post_html, post_id):
    message = post_html.find("div", {"id": "post_message_" + post_id}).getText().strip().replace('\n', '')
    message = re.sub(' +', ' ', message)
    return message


def extract_post_date(post_html):
    date_as_text = post_html.find("td", {"class": "thead"}).getText().strip()
    post_date = parse(date_as_text)
    return post_date.isoformat()


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


def extract_helpful_marks(post_html, post_id):
    print("stuff")


thread_html = BeautifulSoup(open(file_location), "html.parser")

thread_id = extract_thread_id(thread_html)
thread_name = extract_thread_name(thread_html)
source = forum

origin_category = extract_origin_category(thread_html)
common_category = map_common_category(origin_category)

posts = thread_html.find_all("div", {"id": re.compile("edit*")})

reply_count = max(index for index, post in enumerate(posts)) + 1

unique_users = set()

thread_thank_you_count = 0
thread_support_count = 0
thread_helpful_count = 0

replies = []

for index, post in enumerate(posts):
    post_order = index
    post_id = post.get("id")[4:]

    created_by = extract_created_by(post_id)
    post_text = extract_post_message(post, post_id)
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

    reply = {
        "createdBy": created_by,
        "mdReply": md_reply,
        "postOrder": post_order,
        "postDate": post_date,
        "postText": post_text,
        "postSupportCount": post_hugs_count,
        "postThankYouCount": post_thank_you_count,
        "postHelpfulCount": post_helpful_count,
        "thankYous": thank_yous,
        "supportHugs": support_hugs,
        "helpful": helpful
    }

    replies.append(reply)

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
    "source": forum,
    "uniqueUsers": unique_user_count,
    "replies": replies
}

print(json.dumps(output))
