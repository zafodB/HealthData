'''
 * Created by filip on 25/08/2019
'''
import os, json

starting_directory = "D:/Downloads/json/healthboards/5/"
# starting_directory = "/scratch/GW/pool0/fadamik/ehealthforum/sorted/"
# starting_directory = "/GW/D5data-1/BioYago/ehealthforum/json/impact/2015-12-09/ehealthforum/1"
# starting_directory = "D:/Downloads/json/healthboards/" + "1/"

category_map_location = "D:/OneDrive/Documents/AB Germany/healthboards_map.json"

category_map_file = open(category_map_location, "r", encoding="utf8")
contents = category_map_file.read()
category_map_file.close()
category_map = json.loads(contents)

file_count = 0
missing_categories = {}

# walk through the files in the starting directory
for root, dirs, files in os.walk(starting_directory):
    for file_name in files:
        try:
            # Open file
            file = open(os.path.join(root, file_name), "r", encoding="utf8")
            contents = file.read()
            file.close()
            file_as_json = json.loads(contents)

            old_category = file_as_json['topics'][1]
            if old_category not in category_map:
                missing_categories[old_category] = 0
            else:
                new_category = {'commonCategory': category_map[old_category]}
                file_as_json.update(new_category)
                file = open(os.path.join(root, file_name), "w", encoding="utf8")
                json.dump(file_as_json, file)
                file.close()

            file_count += 1
            if file_count % 10000 == 0:
                print("Processed files: " + str(file_count))

        except Exception as e:
            print("Error processing file: " + file_name + ": " + str(e))

print(missing_categories)
