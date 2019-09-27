'''
 * Created by filip on 27/09/2019
'''
import os, json, re, traceback, hashlib

starting_directory = "/GW/D5data-11/eterolli/Forums_Text/Ehealthforums"
# starting_directory = "D:/Downloads/json/ehealthforum/annotated"
data_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-sorted3/"
# data_directory = "D:/Downloads/json/ehealthforum/json-sorted2"


def extract_thread_id(link: str) -> str:
    pattern0 = re.compile("t[0-9]+-a[0-9]\.html")
    pattern1 = re.compile("t[0-9]+\.html")
    pattern2 = re.compile("topic[0-9]+\.html")

    last_part_url = link.split('/')[-1]
    thread_id = pattern0.search(last_part_url)

    if thread_id:
        thread_id = thread_id.group(0)[1:-8]
    else:
        thread_id = pattern1.search(last_part_url)
        if thread_id:
            thread_id = thread_id.group(0)[1:-5]
        else:
            thread_id = pattern2.search(last_part_url)
            if thread_id:
                thread_id = thread_id.group(0)[5:-5]
            else:
                raise ValueError("Thread ID could not be extracted from link: " + link)

    # print(str(thread_id) + " from: " + link)
    return thread_id


def loop_through():
    processed_files = 0
    error_files = 0

    missing_files = []
    index_error_files = []

    with open("missing-files.txt", "r", encoding="utf8") as missing_f:
        for line in missing_f:
            missing_files.append(str(line).replace('\n', ''))

            exists = 0
            not_exists = 0
            existing = []

    for root, dirs, files in os.walk(starting_directory):
        for file_name in files:
            try:
                file = open(os.path.join(root, file_name), "r", encoding="utf8")
                contents = json.loads(file.read())
                file.close()

                for thread in contents['hits']['hits']:
                    source_link = thread['_source']['Link']
                    thread_id = extract_thread_id(source_link)

                    if thread_id in missing_files:
                        thread_name = thread['_source']['Title']
                        name_hash = hashlib.md5(thread_name.encode('utf-8'))

                        thread_id_hashed = str(int.from_bytes(name_hash.digest()[:3], byteorder='big'))

                        folder_name = str(int(thread_id_hashed) // 1000)

                        if os.path.exists(os.path.join(data_directory, folder_name, thread_id_hashed + ".json")):
                            exists += 1
                            existing.append(thread_id)
                        else:
                            not_exists +=1

                processed_files += 1

                if processed_files % 100 == 0:
                    print("Processed files: " + str(processed_files) + ", error files: " + str(error_files))

            except Exception as e:
                print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
                traceback.print_exc()
                error_files += 1

    print("Exists: " + str(exists))
    print("Doesn't: " + str(not_exists))
    print(json.dumps(existing))


loop_through()
