'''
 * Created by filip on 16/10/2019
'''

starting_file = "d:/downloads/json/ehealthforum/trac/run.ef-all.bm25.txt"
output_file = "d:/downloads/json/ehealthforum/trac/run.ef-all.bm25.reduced.txt"

counter = 0

with open(output_file, "w+", encoding="utf8") as output:
    with open(starting_file, "r", encoding="utf8") as file:
        previous_line_query = ""
        # previous_line_doc = ""

        hundred_counter = 0
        for line in file:
            counter += 1
            contents = line.split(" ")

            query_id = contents[0]
            # document_id = contents[2]

            if query_id == previous_line_query:
                hundred_counter += 1
            else:
                hundred_counter = 0

            previous_line_query = query_id
            # previous_line_doc = document_id

            if counter % 10000 == 0:
                print("Processed lines: " + str(counter))

            if hundred_counter > 100:
                continue
            else:
                output.write(line)
