'''
 * Created by filip on 18/10/2019
'''

import os

starting_directory = "d:/downloads/json/healthboards/trac/"
output_location = "d:/downloads/json/healthboards/trac/combined.txt"

# starting_directory = "/scratch/GW/pool0/fadamik/healthboards/trac/json/queries"
# output_location = "/scratch/GW/pool0/fadamik/healthboards/trac/json/queries/combined_queries.txt"

with open(output_location, "w+", encoding="utf8") as output:
    for root, dirs, files in os.walk(starting_directory):
        for file_name in files:
            with open(os.path.join(root, file_name), "r", encoding="utf8") as file:

                next_comes_text = False

                for line in file:

                    # print(line[0:5])
                    # print(line[0:7])
                    # print()

                    if line[0:5] == "<num>":

                        # print(line[10:])
                        number = line[14:-1]
                        output.write(number + "\t")
                    elif line[0:7] == "<title>":
                        next_comes_text = True
                    elif next_comes_text:
                        output.write(line)
                        next_comes_text = False
