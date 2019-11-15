'''
 * Created by filip on 26/09/2019

Reads through a directory of json files containing annotated text and other data. Identifies a corresponding JSON
file based on the thread ID and updates the replies in this file with the annotated text. Saves the JSON file in a
new directory.
'''


import os, json, traceback, re, hashlib

starting_directory = "/GW/D5data-11/eterolli/Forums_Text/HealthBoards"
# starting_directory = "/home/fadamik/annotated"
# starting_directory = "D:/Downloads/json/healthboards/annotated"
data_directory = "/scratch/GW/pool0/fadamik/healthboards/json-sorted4/"
# data_directory = "D:/Downloads/json/ehealthforum/json-sorted2"
output_directory = "/scratch/GW/pool0/fadamik/healthboards/json-annotated/"
# output_directory = "D:/Downloads/json/ehealthforum/json-annotated"

healthboards = True


# Extract ID of the thread from the given link
def extract_thread_id(link: str) -> str:
    last_part_url = link.split('/')[-1]

    if healthboards:
        pattern0 = re.compile("[0-9]+-")
        thread_id = pattern0.search(last_part_url)

        if thread_id:
            thread_id = thread_id.group(0)[:-1]
        else:
            raise ValueError("Thread ID could not be extracted from link: " + link)

    else:
        pattern0 = re.compile("t[0-9]+-a[0-9]\.html")
        pattern1 = re.compile("t[0-9]+\.html")
        pattern2 = re.compile("topic[0-9]+\.html")

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


# Locate and open existing JSON file and return contents as dict
def open_file(file_id: str, name: str) -> dict:
    folder = str(int(file_id, base=10) // 1000)

    full_path = os.path.join(data_directory, folder, file_id + ".json")
    if not os.path.exists(full_path):
        name_hash = hashlib.md5(name.encode('utf-8'))

        hashed_id = str(int.from_bytes(name_hash.digest()[:3], byteorder='big'))
        folder = str(int(hashed_id, base=10) // 1000)
        full_path = os.path.join(data_directory, folder, hashed_id + ".json")

        if not os.path.exists(full_path):
            raise FileNotFoundError("File with id: " + file_id + " not found")

    json_file = open(full_path, "r", encoding="utf8")
    json_contents = json.loads(json_file.read())
    json_file.close()

    return json_contents


# Update the existing dictionary with the annotated text and other data
def update_content(existing_content: dict, new_content: dict) -> dict:
    existing_content['title'] = new_content['_source']['Title']
    try:
        annotated_text = new_content['_source']['aida']['annotatedText'].split('\n\n')
        original_text = new_content['_source']['aida']['originalText'].split('\n\n')
    except KeyError:
        raise KeyError("Could not find 'aida' key.")

    for index, text in enumerate(annotated_text):
        if index == 0:
            existing_content['annotatedTitle'] = text
        elif index == 1:
            existing_content['annotatedOriginCategory'] = text.split('\n')[-1][1:]
        elif index == len(annotated_text) - 1:
            continue
        else:
            for reply_index, existing_reply in enumerate(existing_content['replies']):
                existing = existing_reply['postText'].replace(' ', '').replace(',', '').replace('.', '')
                original = original_text[index].replace(' ', '').replace(',', '').replace('.', '')
                if existing == original:
                    pattern = re.compile("\[\[C[0-9]+\|[\w*\s*]{1,}\]\]")
                    annotations = re.findall(pattern, text)

                    existing_content['replies'][reply_index]['annotatedText'] = text
                    existing_content['replies'][reply_index]['annotationsFull'] = annotations
                    break

                # print(json.dumps(annotated_text))
                # print(json.dumps(existing_content['replies']))

    return existing_content


# Write the updated dictionary as JSON to the original file
def output_to_file(content_to_write: dict, file_id: str):
    folder = str(int(file_id, base=10) // 1000)
    if not os.path.exists(os.path.join(output_directory, folder)):
        os.mkdir(os.path.join(output_directory, folder))

    with open(os.path.join(output_directory, folder, file_id + ".json"), "w+", encoding="utf8") as json_file:
        json.dump(content_to_write, json_file)


# Loop through files with the annotated text
def loop_through():
    processed_threads = 0
    error_files = 0

    duplicate_count = 0

    for root, dirs, files in os.walk(starting_directory):
        for file_name in files:
            try:
                file = open(os.path.join(root, file_name), "r", encoding="utf8")
                contents = json.loads(file.read())
                file.close()

                # Loop through replies in the selected JSON file
                for thread in contents['hits']['hits']:
                    source_link = thread['_source']['Link']
                    thread_id = extract_thread_id(source_link)
                    thread_name = thread['_source']['Title']

                    try:
                        pass
                        json_file_contents = open_file(thread_id, thread_name)
                        updated_content = update_content(json_file_contents, thread)
                        output_to_file(updated_content, thread_id)

                    except FileNotFoundError:
                        print("File could not be found " + str(thread_id))
                        continue
                    except ValueError as verr:
                        print("ERROR: " + source_link)
                        traceback.print_exc()
                        continue
                    except IndexError:
                        error_files += 1
                        traceback.print_exc()
                        print("Index error in file: " + thread_id)
                    except KeyError:
                        print("Could not find a key")
                        continue

                    processed_threads += 1

                    if processed_threads % 10000 == 0:
                        print("Processed threads: " + str(processed_threads) + ", duplicate count: " + str(
                            duplicate_count))

            except Exception as e:
                print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
                traceback.print_exc()
                error_files += 1

    print("Processed threads: " + str(processed_threads) + ", duplicate count: " + str(duplicate_count))


loop_through()
