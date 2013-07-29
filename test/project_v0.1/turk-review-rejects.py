import sys
import json
from turkutil import connect, get_our_HITs, get_all

mtc = connect(sandbox=False)
HITs = get_our_HITs(mtc)
for HIT in HITs:
    for assignment in get_all(mtc.get_assignments, HIT.HITId):
        if assignment.AssignmentStatus == u"Rejected":
            sys.stdout.write("Assignment id: %s\n" % (assignment.AssignmentId,))
            sys.stdout.write("Worker id: %s\n" % (assignment.WorkerId,))
            response = json.loads(assignment.answers[0][0].fields[0])
            words = [(int(c), str(w)) for (c, w) in response["input_word"]]
            sys.stdout.write("Response: %r\n" % (words,))
            sys.stdout.write("\n\n")
