'''
 * Created by filip on 02/10/2019
'''

import os

# input_dir = "d:/downloads/json/ehealthforum/index/queries"
# output_dir = "d:/downloads/json/ehealthforum/index"

# output_file = open(os.path.join(output_dir, "output_topics.txt"), "w+", encoding="utf8")
# for root, dirs, files in os.walk(input_dir):
#     for file_name in files:
#         with open(os.path.join(root, file_name), "r", encoding="utf8") as file:
#             output_file.write("\n")
#             output_file.write(file.read())
#
# output_file.close()

with open("/scratch/GW/pool0/fadamik/ehealthforum/trac/maps/topic-map1.txt", "r", encoding="utf8") as input_file:
    with open("/scratch/GW/pool0/fadamik/ehealthforum/trac/maps/qrels.txt", "w+", encoding="utf8") as output_file:
        for line in input_file.readlines():
            contents = line.split('\t')

            if len(contents) < 2:
                continue
            else:
                for index, relevant_id in enumerate(contents):
                    if index == 0:
                        continue
                    else:
                        # output_file.write(QUERY ID + 0 (run number, unused)  + DOCID + 1 (relevance) + newline)
                        output_file.write(str(contents[0]) + ' 0 ' + str(relevant_id.replace('\n', '')) + " 1\n")


# output_file.readlines()
