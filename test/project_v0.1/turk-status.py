import sys

from turkutil import connect, get_our_HITs, get_all

mtc = connect(sandbox=False)

if len(sys.argv) > 1 and sys.argv[1] == "--expire-all":
    print("Expiring all outstanding HITs...")
    for HIT in get_our_HITs(mtc):
        mtc.expire_hit(HIT.HITId)
    print("...done")
# Re-fetch after expiring, so as to make sure we have up-to-date information.
HITs = get_our_HITs(mtc)
live = 0
bad_workers = {}
need_reviewed = set()
total_cost = 0
pending_cost = 0
max_future_cost = 0
for HIT in HITs:
    assignments = get_all(mtc.get_assignments, HIT.HITId)
    approved = 0
    pending = 0
    for assignment in assignments:
        if assignment.AssignmentStatus == u"Approved":
            approved += 1
        elif assignment.AssignmentStatus == u"Submitted":
            need_reviewed.add(HIT.HITId)
            pending += 1
        elif assignment.AssignmentStatus == u"Rejected":
            bad_workers.setdefault(assignment.WorkerId, []).append(HIT.HITId)
        else:
            raise ValueError, assignment.AssignmentStatus
    reward = float(HIT.Amount)
    hit_cost_so_far = approved * reward
    hit_cost_pending = pending * reward
    total_cost += hit_cost_so_far
    pending_cost += hit_cost_pending
    # I *think* you add these together to get the maximum number of
    # assignments that might be submitted, but I'm not 100% sure.
    max_future_assignments = (int(HIT.NumberOfAssignmentsAvailable) +
                              int(HIT.NumberOfAssignmentsPending))
    if not HIT.expired and max_future_assignments > 0:
        live += 1
        max_future_cost += max_future_assignments * reward
    sys.stdout.write("%s: %s @ %0.2f = $%0.2f"
                     % (HIT.HITId, approved, reward, hit_cost_so_far))
    if pending:
        sys.stdout.write(" (+ %s @ %0.2f = $%0.2f)"
                         % (pending, reward, hit_cost_pending))
    sys.stdout.write("\n")
# 10% Amazon commission. NB: this assumes that all our rewards are >= $0.05,
# and that we aren't using "master" workers:
print("Total paid: %0.2f + 10%% = $%0.3f" % (total_cost, total_cost * 1.10))
print("Total paid + pending: %0.2f + 10%% = $%0.3f"
      % (total_cost + pending_cost, 1.10 * (total_cost + pending_cost)))
print("Maximum future cost: %0.2f + 10%% = $%0.3f"
      % (total_cost + pending_cost + max_future_cost,
         1.10 * (total_cost + pending_cost + max_future_cost)))
print("")
print("Bad workers:")
for worker, hits in bad_workers.iteritems():
    print("  %s (in: %s)" % (worker, hits))
print("")
if need_reviewed:
    print("HITs needing review:")
    for hit_id in need_reviewed:
        print("  https://requester.mturk.com/mturk/manageHIT?HITId=%s&viewableEditPane="
              % (hit_id,))

print("")
if live:
    print("HITs that are live: %s" % (live,))
    print("  (Use --expire-all to mark them expired now)")
else:
    print("No HITs are currently live.")
