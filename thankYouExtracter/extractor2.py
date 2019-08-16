'''
 * Created by filip on 15/08/2019
'''

from bs4 import BeautifulSoup

print("Hello there!")

starting_directory = "D:/Downloads/json/html/44.html"

soup = BeautifulSoup(open(starting_directory), "html.parser")
posts = soup.find_all("div", {"class": "threadpost"})

for post in posts:
    post_id = post.get("id")[4:]
    post_text = post.find("div", {"id": "post_message_"+post_id}).text
    print(post)

    post_hugs = post.find("div", {"id": "post_hugs_box_"+post_id}).text
    post_thanks = post.find("div", {"id": "post_thanks_box_"+post_id}).text
    if len(post_thanks) > 0: #if the thanks div is not empty it means that this post has received at least one thanks.
        print(post_thanks)

print("hello there")
