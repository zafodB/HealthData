'''
 * Created by filip on 17/10/2019
'''

import os, json, traceback

starting_directory = "d:/downloads/json/ehealthforum/json-annotated/"
output_file = "d:/downloads/json/ehealthforum/json-annotated/maps4_0.txt"


# starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated2/"
# output_file = "/scratch/GW/pool0/fadamik/ehealthforum/trac/json/maps/maps4_0.txt/"

documents_by_category = {}
queries_by_category = {}

processed_files = 0

for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            with open(os.path.join(root, file_name), "r", encoding="utf8") as file:
                contents = json.loads(file.read())

                thread_id = str(contents['threadId'])

                common_category = contents['commonCategory']
                if common_category not in queries_by_category:
                    queries_by_category[common_category] = []

                if common_category not in documents_by_category:
                    documents_by_category[common_category] = []

                for index, reply in enumerate(contents['replies']):
                    if index == 0:
                        queries_by_category[common_category].append(thread_id)
                        continue

                    if (reply["postThankYouCount"] > 0 or reply["postHelpfulCount"] > 0
                            or reply["postSupportCount"] > 0):
                        document_id = "EF" + thread_id + "r" + str(index)
                        documents_by_category[common_category] = documents_by_category[common_category].append(document_id)

            processed_files += 1

            # mylist = ["apple.", "bannanana"]
            #
            # mylist.

            if processed_files % 1000 == 0:
                print("Processed files: " + str(processed_files))

        except Exception as e:
            traceback.print_exc()

print("READ ALL FILES")

with open(output_file, "w+", encoding="utf8") as output:
    for category in queries_by_category:
        for query in queries_by_category[category]:
            output.write(query)

            for docid in documents_by_category[category]:
                output.write("\t" + docid)

            output.write("\n")
