'''
 * Created by filip on 09/10/2019
'''
import os

docids = set()
duplicate_ids = []

for root, dir, files in os.walk("/scratch/GW/pool0/fadamik/ehealthforum/trac/data"):
# for root, dir, files in os.walk("d:/downloads/json/ehealthforum/trac/data"):
    for filename in files:
        with open(os.path.join(root, filename)) as file:
            for line in file.readlines():
                if line[0:7] == "<DOCNO>":
                    docid = line[7:-9]
                    if docid in docids:
                        # print("Found a duplicate: " + str(docid))
                        duplicate_ids.append(docid)
                    else:
                        docids.add(docid)


