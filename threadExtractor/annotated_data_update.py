'''
 * Created by filip on 26/09/2019
'''
import os, json, traceback, re

starting_directory = "/GW/D5data-11/eterolli/Forums_Text/Ehealthforums"
# starting_directory = "D:/Downloads/json/ehealthforum/annotated"
data_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-sorted3/"
# data_directory = "D:/Downloads/json/ehealthforum/json-sorted2"
output_directory = "/scratch/GW/pool0/fadamik/ehealthforum/json-annotated/"
# output_directory = "D:/Downloads/json/ehealthforum/json-annotated"


# Extract ID of the thread from the given link
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


# Locate and open existing JSON file and return contents as dict
def open_file(file_id: str) -> dict:
    folder = str(int(file_id, base=10) // 1000)

    full_path = os.path.join(data_directory, folder, file_id + ".json")
    if os.path.exists(full_path):
        json_file = open(full_path, "r", encoding="utf8")
        json_contents = json.loads(json_file.read())
        json_file.close()

        return json_contents
    else:
        raise FileNotFoundError("File with id: " + file_id + " not found")


# Update the existing dictionary with the annotated text and other data
def update_content(existing_content: dict, new_content: dict) -> dict:
    existing_content['title'] = new_content['_source']['Title']
    annotated_text = new_content['_source']['aida']['annotatedText'].split('\n\n')
    for index, text in enumerate(annotated_text):
        if index == 0:
            existing_content['annotatedTitle'] = text
        elif index == 1:
            existing_content['annotatedOriginCategory'] = text.split('\n')[-1][1:]
        elif index == len(annotated_text) - 1:
            continue
        else:
            pattern = re.compile("\[\[C[0-9]+\|\S*\]\]")
            annotations = re.findall(pattern, text)

            existing_content['replies'][index - 2]['annotatedText'] = text
            existing_content['replies'][index - 2]['annotationsFull'] = annotations

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
    processed_files = 0
    error_files = 0

    for root, dirs, files in os.walk(starting_directory):
        for file_name in files:
            try:
                file = open(os.path.join(root, file_name), "r", encoding="utf8")
                contents = json.loads(file.read())
                file.close()

                for thread in contents['hits']['hits']:
                    source_link = thread['_source']['Link']
                    thread_id = extract_thread_id(source_link)

                    try:
                        json_file_contents = open_file(thread_id)
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
                        print("Index error in file: " + thread_id)

                processed_files += 1

                if processed_files % 100 == 0:
                    print("Processed files: " + str(processed_files) + ", error files: " + str(error_files))

            except Exception as e:
                print("Error processing file: " + os.path.join(root, file_name) + ": " + str(e))
                traceback.print_exc()
                error_files += 1

loop_through()
