import csv, sys, string
import json
from texts import text_dict

bad_workers = [ "A3EVMHAEXZE4WE",
                "AQE1530F9RI0Q",
                "A1DARMCWVOLTJ6",
                "A7T2BQ927EXO9",
                "ACFBUSLSNUGRU",
                "A2AT0G92TP7HCG",
                "A3LIEITJ1JLBY1",
                "A2VDDES6LFZOFW" ]

csv.field_size_limit(sys.maxint)

total = {}
correct = {}

# Try get all correct index/word in a list first
origin = {}
for text_index in text_dict:
    for para in text_dict[text_index]:
        for word in para:
            # lower case
            temp =  word[1].lower()
            # remove punctuation
            temp2 = temp.translate(string.maketrans("",""), string.punctuation)
            origin[ word[0] ] = temp2

r = csv.reader(open("data.csv"))
i = 0

# Load all input data to list "input"
input = []
for id, worker_id, text_index, start_position, gap, main_data in r:
    # filter bad workers
    if worker_id not in bad_workers:
        # do not json.loads first line of csv file
        if id != "id":
            data = json.loads(main_data)
            # filter non native English speaker
            if "english" in (data["language"].lower() ):
                input.append( data["input_word"]  )
            else:
                print data["language"]
for hit in input:
    for word in hit:
        # Initialize the dicts
        word_index = int(word[0])
        total[ word_index ] = 0
        correct[ word_index ] = 0

for hit in input:
    for word in hit:
        # Pick first word
        temp = word[1].split(" ")[0]
        # lower case
        temp2 =  str ( temp.lower() )
        # remove punctuation
        extracted_word = temp2.translate(string.maketrans("",""), string.punctuation)
        
        word_index = int(word[0])
        if extracted_word == origin[ word_index ]:
            correct[ word_index ] += 1
        # The total count for this position word +1
        total[ word_index ] += 1

#total = sorted(total.items(), key=lambda d:d[0])
#correct = sorted(correct.items(), key=lambda d:d[0])
#for key in correct:
#    print key

# Get probability
probability = {}
for key in total:
   #print "Correct: " + str(key) + ": " + str( correct[key])
   #print "Total: " + str( key ) + ": " + str ( total[key] )
   probability[key] = correct[key] / (total[key] * 1.0)

probability = sorted(probability.items(), key=lambda d:d[0])

# Write to CSV file
w = csv.writer(file('cloze.csv','wb'))
 
w.writerow( ["code", "probability"])
for row in probability:
    w.writerow(row)
    
# 'row' is a Python list, where each entry in the list is one
#entry from the csv file
    # The first row has the column names; the ones after that have data from one
    # database entry.
