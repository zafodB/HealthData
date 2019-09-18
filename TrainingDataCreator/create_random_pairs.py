'''
 * Created by filip on 18/09/2019
'''

import os, random, json, traceback

# starting_directory = "D:/Downloads/json/healthboards/html-sorted/"
starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-sorted3/"
# starting_directory = "/scratch/GW/pool0/fadamik/healthboards/json-sorted2/"
# output_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-sorted2/"
output_directory = "/scratch/GW/pool0/fadamik/pairs/ehealthboards/random"

path_list = []

# Construct a list of all files in the starting folder. We will pop files from this list as we generate documents and queries
for root, dirs, files in os.walk(starting_directory):
    for file in files:
        path_list.append(os.path.join(root, file))

print("Path set constructed")

random.seed(a=180919)


# Picks a random reply from the dictionary
def pick_reply(file: dict) -> dict:
    reply = random.choice(file['replies'])
    file['replies'].remove(reply)
    return reply


document_list = []

# Generate documents by randomly picking a file from the list and randomly picking a reply from that file. Files with
# fewer than two replies are removed from the list, but not processed further. If a file has <2 replies, a new file is
# picked.
while len(document_list) < 40000:

    file_path = random.choice(path_list)
    path_list.remove(file_path)

    # file_path = "d:/downloads/json/test.txt"

    file = open(file_path, "r", encoding="utf8")
    contents = file.read()
    file.close()
    file_as_dict = json.loads(contents)

    if file_as_dict['replyCount'] < 2:
        continue

    del file_as_dict['replies'][0]

    random_reply = pick_reply(file_as_dict)
    reply_text = random_reply['postText']

    while reply_text is None or len(reply_text) < 3:
        if len(file_as_dict['replies']) == 0:
            reply_text = None
            break
        else:
            random_reply = pick_reply(file_as_dict)
            reply_text = random_reply['postText']

    if reply_text is None:
        continue

    document_list.append(
        {'reply_text': reply_text,
         'has_quotes': random_reply['hasQuotes'],
         'reply_username': random_reply['createdBy']['username'],
         'reply_status': random_reply['createdBy']['status'],
         'common_category': file_as_dict['commonCategory'],
         'post_helpful_count': random_reply['postHelpfulCount'],
         'post_hugs_count': random_reply['postSupportCount'],
         'post_thank_you_count': random_reply['postThankYouCount']
         }
    )

    if len(document_list) % 100 == 0:
        print("Documents processed: " + str(len(document_list)))



fake_pairs = open(os.path.join(output_directory, "fake-pairs0.txt"), "a+", encoding="utf8")

# Generates queries by randomly going through the files. When a file is picked, its first reply (original post)
# is extracted and used as a query. A random document is popped from the document list and attached to the query.
# The pair is written into a file
lines_written = 0
while lines_written < 40000:
    try:
        file_path = random.choice(path_list)

        path_list.remove(file_path)

        file = open(file_path, "r", encoding="utf8")
        contents = file.read()
        file.close()
        file_as_dict = json.loads(contents)

        if len(contents) == 0:
            continue
        if file_as_dict['replies'] is None or len(file_as_dict['replies']) == 0:
            continue

        # print(file_path)
        file_as_dict = json.loads(contents)

        post_text = file_as_dict['replies'][0]['postText']
        username = file_as_dict['replies'][0]['createdBy']['username']
        status = file_as_dict['replies'][0]['createdBy']['status']
        common_category = file_as_dict['commonCategory']

        reply = random.choice(document_list)

        stop_counter = 0
        while reply['common_category'] == common_category and stop_counter < 10:
            reply = random.choice(document_list)
            stop_counter += 1

        if stop_counter >= 10:
            continue

        document_list.remove(reply)

        tab_char = '\t'

        fake_pairs.write(
            post_text + tab_char +
            username + tab_char +
            str(status) + tab_char +
            common_category + tab_char +

            reply['reply_text'] + tab_char +
            str(reply['has_quotes']) + tab_char +
            reply['reply_username'] + tab_char +
            str(reply['reply_status']) + tab_char +
            reply['common_category'] + tab_char +
            str(reply['post_helpful_count']) + tab_char +
            str(reply['post_hugs_count']) + tab_char +
            str(reply['post_thank_you_count']) + tab_char +
            str(4) + tab_char +
            str(False) + "\n"
        )

        lines_written += 1

        if lines_written % 100 == 0:
            print("Lines written: " + str(lines_written))

        if lines_written % 1000 == 0:
            fake_pairs.close()
            fake_pairs = open(os.path.join(output_directory, "fake-pairs" + str(lines_written // 1000) + ".txt"), "a+",
                              encoding="utf8")

            print("Written out to file.")

    except Exception as e:
        traceback.print_exc()

# print(json.dumps(document_list))
