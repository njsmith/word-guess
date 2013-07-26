import sys
import re
from boto.mturk.connection import MTurkConnection

#HOST = "mechanicalturk.sandbox.amazonaws.com"
HOST = "mechanicalturk.amazonaws.com"

title_re = re.compile("uess words in text.*for SCIENCE")

secrets = []
for line in open("secrets.txt"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    secrets.append(line)
aws_access_key_id, aws_secret_access_key = secrets
mtc = MTurkConnection(aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key,
                      host=HOST)

HITs = []
for HIT in mtc.get_all_hits():
    if title_re.search(HIT.Title):
        HITs.append(HIT)
unexpired = 0
bad_workers = set()
need_reviewed = set()
total_cost = 0
pending_cost = 0
for HIT in HITs:
    if not HIT.expired:
        unexpired += 1
    assignments = mtc.get_assignments(HIT.HITId, page_size=50)
    approved = 0
    pending = 0
    for assignment in assignments:
        if assignment.AssignmentStatus == u"Approved":
            approved += 1
        elif assignment.AssignmentStatus == u"Submitted":
            need_reviewed.add(HIT.HITId)
            pending += 1
        elif assignment.AssignmentStatus == u"Rejected":
            bad_workers.add(assignment.WorkerId)
        else:
            raise ValueError, assignment.AssignmentStatus
    reward = float(HIT.Amount)
    hit_cost_so_far = approved * reward
    hit_cost_pending = pending * reward
    total_cost += hit_cost_so_far
    pending_cost += hit_cost_pending
    sys.stdout.write("%s: %s @ %0.2f = $%0.2f"
                     % (HIT.HITId, approved, reward, hit_cost_so_far))
    if pending:
        sys.stdout.write(" (+ %s @ %0.2f = $%0.2f)"
                         % (pending, reward, hit_cost_pending))
    sys.stdout.write("\n")
print("Total nominal cost: %0.2f" % (total_cost,))
# 10% Amazon commission. NB: this assumes that all our rewards are >= $0.05,
# and that we aren't using "master" workers:
print("Total actual cost: %0.3f" % (total_cost * 1.10))
print("Total nominal cost, with pending: %0.2f" % (total_cost + pending_cost,))
print("Total actual cost, with pending: %0.3f" % (1.10 * (total_cost + pending_cost),))
print("")
print("Bad workers:")
for worker in bad_workers:
    print("  " + worker)
print("")
if need_reviewed:
    print("HITs needing review:")
    for hit_id in need_reviewed:
        print("  https://requester.mturk.com/mturk/manageHIT?HITId=%s&viewableEditPane="
              % (hit_id,))

print("")
print("HITs that are not expired: %s" % (unexpired,))
if len(sys.argv) > 1 and sys.argv[1] == "--expire-all":
    for HIT in HITs:
        mtc.expire_hit(HIT.HITId)
    print("  ...but I just expired them, so never mind!")
else:
    print("  (Use --expire-all to mark them expired now)")
