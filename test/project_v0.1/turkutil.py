import re
from boto.mturk.connection import MTurkConnection

SANDBOX_HOST = "mechanicalturk.sandbox.amazonaws.com"
HOST = "mechanicalturk.amazonaws.com"

secrets = []
for line in open("secrets.txt"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    secrets.append(line)
aws_access_key_id, aws_secret_access_key = secrets

title_re = re.compile("uess words in text.*for SCIENCE")

def connect(sandbox=True):
    if sandbox:
        host = SANDBOX_HOST
    else:
        host = HOST
    return MTurkConnection(aws_access_key_id=aws_access_key_id,
                           aws_secret_access_key=aws_secret_access_key,
                           host=host)

# XX next time use the RequestorAnnotation field to CreateHit so as to create
# a unique identifier grouping these hits together.
def get_our_HITs(mtc):
    HITs = []
    for HIT in mtc.get_all_hits():
        if title_re.search(HIT.Title):
            HITs.append(HIT)
    return HITs

def HIT_url(hit_id, sandbox=False):
    return "https://requester.mturk.com/mturk/manageHIT?HITId=%s" % (hit_id,)

# This can be used to fetch all results for any pagination-based call that
# uses boto's standard "page_number" kwarg. E.g.:
#   connection.get_assignment(hit_id)
# will return the first 10 assignments by default, but
#   get_all(connection.get_assignment, hit_id)
# will return *all* assignments, regardless of how many there are.
def get_all(fn, *args, **kwargs):
    results = []
    # We'll fetch them all regardless, but no reason to waste round trips on
    # small batches if we know we're indeed fetching them all.
    kwargs.setdefault("page_size", 100)
    assert "page_number" not in kwargs
    first_page = fn(*args, **kwargs)
    total_results = int(first_page.TotalNumResults)
    page_size = len(first_page)
    # integer division, rounding up:
    needed_pages = (total_results + page_size - 1) // page_size
    results.extend(first_page)
    for i in xrange(needed_pages - 1):
        # 1-based indexing, and skipping the first page:
        kwargs["page_number"] = 1 + 1 + i
        page = fn(*args, **kwargs)
        results.extend(page)
    assert len(results) == total_results
    return results
