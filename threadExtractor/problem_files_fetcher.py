'''
 * Created by filip on 27/09/2019
'''

import os, json, re, traceback

starting_directory = "/GW/D5data-11/eterolli/Forums_Text/Ehealthforums"
# starting_directory = "D:/Downloads/json/ehealthforum/annotated"


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

    with open("index-errors.txt", "r", encoding="utf8") as index_er_f:
        for line in index_er_f:
            index_error_files.append(str(line).replace('\n', ''))

    print(missing_files)
    print()
    print(index_error_files)

    output_file_missing = open("missing_details.txt", "w+", encoding="utf8")
    output_file_index = open("index_details.txt", "w+", encoding="utf8")

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
                        json.dump(thread, output_file_missing)

                    if thread_id in index_error_files:
                        json.dump(thread, output_file_index)

                processed_files += 1

                if processed_files % 100 == 0:
                    print("Processed files: " + str(processed_files) + ", error files: " + str(error_files))

            except Exception as e:
                print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
                traceback.print_exc()
                error_files += 1

    output_file_missing.close()
    output_file_index.close()


loop_through()
