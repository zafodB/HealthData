'''
 * Created by filip on 18/09/2019
'''

import json, os
import traceback

starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-sorted3/"
# starting_directory = "D:/Downloads/json/ehealthforums/json-sorted/"
pairs_directory = "pairs/ehealthforum/"
# pairs_directory = "D:/downloads/json/ehealthforums/pairs/"


def extract_items(data_dictionary, pairs_file):
    common_category = data_dictionary['commonCategory']
    post_text = data_dictionary['replies'][0]['postText']
    username = data_dictionary['replies'][0]['createdBy']['username']
    status = data_dictionary['replies'][0]['createdBy']['status']

    for reply in data_dictionary['replies']:
        post_thank_you_count = 0
        post_hugs_count = 0
        post_helpful_count = reply['postHelpfulCount']
        mdReply = reply['mdReply']
        reply_order = reply['postOrder']
        reply_text = reply['postText']
        has_quotes = reply['hasQuotes']
        reply_user = reply['createdBy']['username']
        reply_status = reply['createdBy']['status']

        form = None

        tab_char = "\t"

        if post_helpful_count > 0 and reply_order > 0:
            form = "votes"

        if mdReply and reply_order > 0:
            form = "mdReply"

        if form is not None:
            pairs_file.write(
                post_text + tab_char +
                username + tab_char +
                str(status) + tab_char +
                common_category + tab_char +


                reply_text + tab_char +
                str(has_quotes) + tab_char +
                reply_user + tab_char +
                str(reply_status) + tab_char +
                common_category + tab_char +
                str(post_thank_you_count) + tab_char +
                str(post_hugs_count) + tab_char +
                str(post_helpful_count) + tab_char +
                form + tab_char +
                str(True) + "\n"
            )


file_count = 0
successful_files = 0
error_files = 0
OKBLUE = '\033[94m'
ENDC = '\033[0m'

pairs_file = open(os.path.join(pairs_directory, "pairs1.txt"), "a+", encoding="utf8")

for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            # file_name = "156584.json"
            # root = "D:/Downloads/json/ehealthforums/html-sorted/156"

            json_file = open(os.path.join(root, file_name),encoding="utf8")
            json_contents = json.loads(json_file.read())
            json_file.close()

            extract_items(json_contents, pairs_file)

            successful_files += 1
            file_count += 1

            if file_count % 100 == 0:
                print("Processed files: " + str(file_count))
                print(OKBLUE + "Error-free ratio: " + str((error_files / successful_files) * 100) + "%   E: " + str(
                    error_files) + ENDC)

            if file_count % 10000 == 0:
                pairs_file.close()
                pairs_file = open(os.path.join(pairs_directory, "pairs" + str(file_count / 10000) + ".txt"), "a+",
                                  encoding="utf8")


        except Exception as e:
            print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
            traceback.print_exc()
            error_files += 1
