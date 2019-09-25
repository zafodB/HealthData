'''
 * Created by filip on 23/09/2019
'''

import json, os, traceback, re
import pandas as pd

user_list_location = "d:/downloads/json/List_patients.csv"
# user_list_location = "list_patients.csv"

# data_directory = "d:/downloads/json/ehealthforum/json-sorted"
data_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-sorted3"
# output_directory = "d:/downloads/json/filtered-users"
output_directory = "/scratch/GW/pool0/fadamik/filtered-users"

problem_files = [523678, 521585, 480111, 495723, 519087, 527330, 486202, 523000, 521057, 506168, 517827, 513467, 520300,
                 477176, 491106, 526788, 523929, 479664, 505936, 469969, 442154, 453258, 524114, 436044, 524167, 494199,
                 451680, 437820, 435534, 437419, 525083, 523286, 514058, 525097, 516064, 496424]

problem_users = [
    "nnhood", "sks263", "immz22", "Gobbler01", "bitblockchain", "TWayburn", "undertakerlives", "Lydz90", "don482",
    "Pj1989", "guy1221", "guest60765", "Nurdyguy", "D1gitald0ctor", "Alexandra95", "wifebackpain", "shell189",
    "Worriedmama_77", "tirez", "Yasu_takagi", "Ashemp86", "psyadam", "Achlorhydria7", "Whittington", "mattosx",
    "Suzy123456789", "Suzieqq1234", "Pmalone", "devon191998", "PJfan", "DiabSick", "guest68935", "Dancin649",
    "guest62812", "EFL"
]

user_list = pd.read_csv(user_list_location, sep="\t")


def get_thread_ids() -> list:
    thread_ids = []

    pattern1 = re.compile("topic[0-9]+.html")
    pattern2 = re.compile("t[0-9]+.html")

    for link in user_list['Link'].iteritems():
        last_part_url = link[1].split('/')[-1]
        topic_id = pattern1.search(last_part_url)

        if topic_id:
            topic_id = topic_id.group(0)[5:-5]
            # print(topic_id)
        else:
            topic_id = pattern2.search(last_part_url)
            if topic_id:
                topic_id = topic_id.group(0)[1:-5]
                # print(topic_id)

        thread_ids.append(int(topic_id))
        if int(topic_id) in problem_files:
            print(link[1])

    return thread_ids


def get_usernames(file_ids: list) -> list:
    usernames = []

    for filename in file_ids:
        folder = str(filename // 1000)

        full_path = os.path.join(data_directory, folder, str(filename) + ".json")

        if os.path.exists(full_path):
            file = open(full_path, "r", encoding="utf8")
            contents = json.loads(file.read())
            file.close()

            username = contents['replies'][0]['createdBy']['username']
            print(username)
            usernames.append(username)

        else:
            print("no such file")

    return usernames


def crawl_files(usernames: list):
    user_posts = {}

    for user in usernames:
        user_posts[user] = []

    processed_files = 0

    for root, dirs, files in os.walk(data_directory):
        for file_name in files:
            try:
                found_relevant_reply = []

                file = open(os.path.join(root, file_name), "r", encoding="utf8")
                contents = json.loads(file.read())
                file.close()

                for reply in contents['replies']:
                    username = reply['createdBy']['username']
                    if username in usernames:
                        reply_data = {"threadId": contents['threadId'],
                                      "threadHelpfulCount": contents['threadHelpfulCount'],
                                      "threadSupportCount": contents['threadSupportCount'],
                                      "threadThankYouCount": contents['threadThankYouCount'],
                                      "source": contents['source'],
                                      "replyCount": contents['replyCount'],
                                      "uniqueUsers": contents['uniqueUsers'],
                                      "mdReplyCount": contents['mdReplyCount'],
                                      "commonCategory": contents['commonCategory'],
                                      "originCategory": contents['originCategory'],
                                      "title": contents['title'],
                                      "originalFile": contents['originalFile'],

                                      "replyText": reply['postText'],
                                      "replyId": reply['postId'],
                                      "createdBy": reply['createdBy'],
                                      "replyOrder": reply['postOrder'],
                                      "replySupportCount": reply['postSupportCount'],
                                      "replyHelpfulCount": reply['postHelpfulCount'],
                                      "replyThankYouCount": reply['postThankYouCount'],
                                      "mdReply": reply['mdReply'],
                                      "hasQuotes": reply['hasQuotes'],
                                      "replyDate": reply['postDate']
                                      }

                        user_posts[username].append(reply_data)
                        found_relevant_reply.append(username)

                if found_relevant_reply:
                    for user in found_relevant_reply:
                        file = open(os.path.join(output_directory, user + ".json"), "w+", encoding="utf8")
                        json.dump(user_posts[user], file)
                        file.close()
                        print("Wrote out to user file: " + user + ".json")

                processed_files += 1

                if processed_files % 100 == 0:
                    print("Processed files: " + str(processed_files))


            except Exception as e:
                print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
                traceback.print_exc()


threads = get_thread_ids()
# usernames = get_usernames(threads)
# print(len(usernames))

# crawl_files(usernames)
# crawl_files(problem_users)
