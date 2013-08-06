import csv, sys, string
from texts import text_dict

csv.field_size_limit(sys.maxint)

r = csv.reader(open("cloze.csv"))

position_probs_total = {}
position_count = {}

# Load probability from extracted data
probability = {}
for code, c_probs, n_probs in r:
    if code != 'code':
        probability[code] = c_probs

# Get each word position
position = {}
for text_index in text_dict:
    for para in text_dict[text_index]:
        for word in para:
            position[ word[0] ] = word[0] - text_dict[text_index][0][0][0]
            # initialize 
            position_probs_total[ position[ word[0] ] ] = 0.0
            position_count[ position[ word[0] ] ] = 0

# sum probability with same position up
# count their number
for code in probability:
    position_probs_total[ (position[ int(code) ]) ] += float(probability[code])
    position_count[ (position[ int(code) ]) ]  += 1

# get average probability
position_probability = {}
for code in position_probs_total:
    if position_count[ code ] != 0:
        position_probability[ code ] = position_probs_total[ code ] / position_count[ code ] 


position_probability = sorted(position_probability.items(), key=lambda d:d[0])

# Write to CSV file
w = csv.writer(file('position_vs_probs.csv','wb'))
 
w.writerow( ["position", "Average Probability"])
for row in position_probability:
    w.writerow(row)
