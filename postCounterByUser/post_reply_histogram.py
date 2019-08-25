'''
 * Created by filip on 19/08/2019
'''

# import matplotlib
# matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
import os
import json

def map_to_bins(data_as_dictionary):
    # bar_data = {'1': 0, '2': 0, '3': 0, '4': 0, '5-10': 0, '11-50': 0, '51-\n100': 0, '>100': 0}
    bar_data = {'1': 0, '2': 0, '3': 0, '4': 0, '5-10': 0, '11-50': 0, '51-\n100': 0, '101-\n1000': 0, '>1000': 0}
    for key in data_as_dictionary.keys():
        if 1 <= key <= 4:
            bar_data[str(key)] = data_as_dictionary[key]
        elif 4 < key <= 10:
            bar_data['5-10'] += data_as_dictionary[key]
        elif 10 < key <= 50:
            bar_data['11-50'] += data_as_dictionary[key]
        elif 50 < key <= 100:
            bar_data['51-\n100'] += data_as_dictionary[key]
        elif 100 < key <= 1000:
            bar_data['101-\n1000'] += data_as_dictionary[key]
        else:
            bar_data['>1000'] += data_as_dictionary[key]

    print(bar_data)
    return bar_data


file = open("d:/downloads/json/post_replies_healthboards.json", "r", encoding="utf8")
contents = file.read()
file.close()
file_as_json = json.loads(contents)

total_new_posts = 0
total_replies = 0
total_users = 0
histogram_posts = {}
histogram_replies = {}

print("Total users: " + str(len(file_as_json)))

for username in file_as_json:
    user_data = file_as_json[username]

    new_posts = user_data['n']
    replies = user_data['r']

    total_new_posts += new_posts
    total_replies += replies

    if replies > 5000:
        print(username + " " + str(replies))

    if new_posts not in histogram_posts:
        histogram_posts[new_posts] = 1
    else:
        histogram_posts[new_posts] += 1

    if replies not in histogram_replies:
        histogram_replies[replies] = 1
    else:
        histogram_replies[replies] += 1

    # print("New posts: " + str(usr['n']))
    # print("Replies: " + str(usr['r']))

print("Total new posts: " + str(total_new_posts))
print("Total replies: " + str(total_replies))

histogram_posts.pop(0)
histogram_replies.pop(0)
print(histogram_replies)

bar_data_posts = map_to_bins(histogram_replies)

fig = plt.figure()
fig.suptitle("Number of replies per user in Healthboards.")

plt.bar(list(bar_data_posts.keys()), bar_data_posts.values(), width=0.9, color='g')

for x, y in zip(list(bar_data_posts.keys()),bar_data_posts.values()):

    label = "{:.0f}".format(y)

    plt.annotate(label, # this is the text
                 (x,y), # this is the point to label
                 textcoords="offset points", # how to position the text
                 xytext=(0,15), # distance from text to points (x,y)
                 ha='center')

plt.show()
fig.savefig("d:/downloads/json/user_replies_healthboards.png")
