import sys
import json
from turkutil import connect, get_our_HITs, get_all

mtc = connect(sandbox=False)
HITs = get_our_HITs(mtc)
for HIT in HITs:
    for assignment in get_all(mtc.get_assignments, HIT.HITId):
        if assignment.AssignmentStatus == u"Rejected":
            sys.stdout.write("Assignment id: %s\n" % (assignment.AssignmentId,))
            sys.stdout.write("HIT: %s\n" % (assignment.HITId,))
            sys.stdout.write("Worker id: %s\n" % (assignment.WorkerId,))
            response = json.loads(assignment.answers[0][0].fields[0])
            words = [(int(c), str(w)) for (c, w) in response["input_word"]]
            sys.stdout.write("Response: %r\n" % (words,))
            word_dict = {}
            for code, word in words:
                word_dict[code] = word
            keypresses = {}
            for event in response["event_log"]:
                if event[1] == "keydown":
                    _, _, code_str, key = event
                    if key == 13:
                        continue
                    code = int(code_str)
                    keypresses.setdefault(code, []).append(key)
            for code, word in sorted(word_dict.items()):
                keys = keypresses.get(code, [])
                if len(keys) < len(word):
                    sys.stdout.write(
                        "SUSPICIOUS: %s: typed %r with %s keypresses: %r\n"
                        % (code, word, len(keys), keys))
            sys.stdout.write("\n\n")
