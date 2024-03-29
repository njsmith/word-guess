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

total_responses = 0
bad_worker_count = 0
bad_language_count = 0

text_count = {}

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

# Initialize the text_count
r = csv.reader(open("data.csv"))
for id, worker_id, text_index, start_position, gap, main_data in r:
    text_count[ text_index ] = 0

# Load all input data to list "input"
r = csv.reader(open("data.csv"))
input = []
for id, worker_id, text_index, start_position, gap, main_data in r:
    total_responses += 1
    # filter bad workers
    if worker_id not in bad_workers:
        # do not json.loads first line of csv file
        if id != "id":
            data = json.loads(main_data)
            # filter non native English speaker
            language = data["language"].lower().strip()
            if ("english" in language
                or language in ["engish", "englisb", "englilsh"]):
                input.append( data["input_word"]  )
                text_count[ text_index ] += 1
            else:
                print data["language"]
                bad_language_count += 1
    else:
        bad_worker_count += 1

print "Total responses:", total_responses
print "Bad workers:", bad_worker_count
print "Bad language:", bad_language_count

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
    probability[key] = (correct[key] +1.0)  / (total[key]+1.0)

probability = sorted(probability.items(), key=lambda d:d[0])

# Load N-Gram Probs
rn = csv.reader(open("brown-ngram-probs.csv"))
n_gram = {}
for code, probs in rn:
    n_gram[code] = probs

# Write to CSV file
w = csv.writer(file('cloze.csv','wb'))
 
w.writerow( ["code", "ClozeProb", "NGramProb"])
for code, prob in probability:
    n_gram_prob = n_gram.get(str(code), "NA")
    # if str(code) in n_gram.keys():
    #     n_gram_prob = n_gram[ str(code) ]
    # else:
    #     n_gram_prob = 'no data'
    w.writerow([code, prob, n_gram_prob ])
    
# 'row' is a Python list, where each entry in the list is one
#entry from the csv file
    # The first row has the column names; the ones after that have data from one
    # database entry.

# Print the number for each text
text_count = sorted(text_count.items(), key=lambda d:d[1])
for text in text_count:
    print 'The text' + str(text[0]) + ': ' + str(text[1])
