import sys

from datetime import timedelta
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import (LocaleRequirement,
                                      PercentAssignmentsApprovedRequirement,
                                      Qualifications)

ASSIGNMENTS_PER_HIT = 14
REWARD = 0.30

#HOST = "mechanicalturk.sandbox.amazonaws.com"
HOST = "mechanicalturk.amazonaws.com"

TITLE = "Guess words in text -- for SCIENCE! (15 minutes)"
KEYWORDS = ["experiment", "research", "academic", "psychology",
            "survey", "questionnaire", "easy", "fun", "simple"]
DESCRIPTION = """Participate in a UC San Diego research study. Everyone who
    makes an honest attempt at this HIT will receive payment. You can
    participate up to 15 times."""
LIFETIME_HOURS = 24
DURATION_HOURS = 1

NUM_HITS = 15

URL = "http://vorpus.org/bwg/FirstForm"
HEIGHT = 600

QUALS = Qualifications()
QUALS.add(LocaleRequirement("EqualTo", "US"))
QUALS.add(PercentAssignmentsApprovedRequirement(
        "GreaterThanOrEqualTo",
        80))

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
balance = mtc.get_account_balance()[0].amount

print "%s: balance is %s" % (HOST, balance)

question = ExternalQuestion(URL, HEIGHT)

for i in xrange(NUM_HITS):
    hit_obj = mtc.create_hit(
        hit_type=None,
        question=question,
        lifetime=timedelta(hours=LIFETIME_HOURS),
        max_assignments=ASSIGNMENTS_PER_HIT,
        title=TITLE,
        description=DESCRIPTION,
        keywords=", ".join(KEYWORDS),
        reward=REWARD,
        duration=timedelta(hours=DURATION_HOURS),
        approval_delay=None,
        questions=None,
        qualifications=QUALS,
        )[0]
    hit_id = hit_obj.HITId
    print "%s: posted %s" % (HOST, hit_id)
