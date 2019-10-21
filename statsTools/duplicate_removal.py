'''
 * Created by filip on 16/10/2019
'''

starting_file = "/scratch/GW/pool0/fadamik/ehealthforum/trac/json/maps/qrels4_0.txt"
output_file = "/scratch/GW/pool0/fadamik/ehealthforum/trac/json/maps/qrels4_1_0.txt"

counter = 0

with open(output_file, "w+", encoding="utf8") as output:
    with open(starting_file, "r", encoding="utf8") as file:
        previous_line_query = ""
        previous_line_doc = ""

        hundred_counter = 0
        for line in file:
            counter += 1
            contents = line.split(" ")

            query_id = contents[0]
            document_id = contents[2]

            # if query_id == previous_line_query:
            #     hundred_counter += 1
            # else:
            #     hundred_counter = 0

            if query_id == previous_line_query and document_id == previous_line_doc:
                pass
            else:
                output.write(line)

            previous_line_query = query_id
            previous_line_doc = document_id

            if counter % 10000 == 0:
                print("Processed lines: " + str(counter))

            # if hundred_counter > 100:
            #     continue
            # else:
            #     output.write(line)
