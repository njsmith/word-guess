import os.path
from parseparse import parse, reduce_tree_to_words
from munge import all_punct, clitic, strip_double_punct

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

TRUE_NAME = "answer-TRUE"
FALSE_NAME = "answer-FALSE"

TRUE = (TRUE_NAME, FALSE_NAME)
FALSE = (FALSE_NAME, TRUE_NAME)

def parse_paragraphs(path):
    f = open(path)
    paras = {}
    current = None
    for line in f:
        line = line.strip().lower()
        if not line or line.startswith("*"):
            continue
        if line[0].isalpha():
            assert line not in paras
            paras[line] = []
            current = line
        else:
            paras[current].append(int(line))
    return paras

def get_paragraphs(brown_textid, corrected=False):
    if corrected:
        path = "corrected-paragraph-breaks.txt"
    else:
        path = "paragraph-breaks.txt"
    return parse_paragraphs(os.path.join(THIS_DIR, path))[brown_textid]

SYNTACTIC = "syntactic"
class Syn(object):
    def __init__(self, num, wordnum, word, replacement):
        self.type = SYNTACTIC
        self.num = num
        self.wordnum = wordnum
        self.word = word
        self.replacement = replacement

SEMANTIC = "semantic"
class Sem(object):
    def __init__(self, num, wordnum, word,
                 replacement_textnum, replacement_wordnum, replacement):
        self.type = SEMANTIC
        # Code identifying this anomaly
        self.num = num
        # Which word is being replaced
        self.wordnum = wordnum
        self.word = word
        # The replacement
        self.replacement_textnum = replacement_textnum
        self.replacement_wordnum = replacement_wordnum
        self.replacement = replacement

NORMAL = "normal"
PRACTICE = "practice"
MUTILATED = "mutilated"
MUTILATED_AVAILABLE = "mutilated_available"

class Text(object):
    def __init__(self, textid, brown_textid, title, sentence_idxs, questions,
                 fixup=None, mutilations=None, type=NORMAL):
        self.textid = textid
        self.brown_textid = brown_textid
        self.title = title
        self.sentence_idxs = sentence_idxs
        self.questions = questions
        self.fixup = fixup
        self.mutilations = mutilations
        self.type = type
        if self.mutilations:
            assert self.type is MUTILATED
        self.load_paragraphs(False)

    def load_paragraphs(self, corrected):
        self.paragraph_idxs = get_paragraphs(self.brown_textid,
                                             corrected=corrected)

    def trees(self):
        return parse(open("%s/parsed/c%s.mrg" % (THIS_DIR, self.brown_textid)))

    def raw_sentences(self):
        for tree in self.trees():
            yield reduce_tree_to_words(tree)

    def indexed_sentences(self):
        i = 0
        for raw_words in self.raw_sentences():
            if self.fixup is not None:
                fixed_up_sentences = self.fixup(i, raw_words)
            else:
                fixed_up_sentences = [raw_words]
            for sentence in fixed_up_sentences:
                yield (i, sentence)
            i += 1

    def indexed_and_numbered_display_sentences(self):
        word_num = 0
        for (i, raw_sentence) in self.indexed_sentences():
            display = merge_raw_words_for_display(raw_sentence)
            if i in self.sentence_idxs:
                numbers = []
                for _ in display:
                    numbers.append(word_num)
                    word_num += 1
            else:
                numbers = [None] * len(display)
            yield (i, numbers, display)

def f04_fixup(idx, words):
    if idx == 17:
        # Line 17, note capitalized "And":
        # ``To give up these notions required a revolution in thought,''
        # Mr. Clark said in reminiscing about the abrupt changes in ideas he
        # experienced when he began reading ``Organic Gardening'' And ``Modern
        # Nutrition'' in a search for help with his problems.
        assert "And" in words
        words[words.index("And")] = "and"
    return [words]

def n26_fixup(idx, words):
    for i in xrange(len(words)):
        if words[i] == "collosal":
            words[i] = "colossal"
    if idx == 4:
        # Line 4:
        # ``Since when did they allow beardless kids into the saloon bars of this town, boys?'' He asked.
        assert "He" in words
        words[words.index("He")] = "he"
        return [words]
    elif idx == 8:
        # Punctuation and segmentation error
        # ``I don't aim to have minors breathing down my neck when I'm a-drinking:'' The stranger ignored him.
        # ['``', 'I', 'do', "n't", 'aim', 'to', 'have', 'minors', 'breathing', 'down', 'my', 'neck', 'when', 'I', "'m", 'a-drinking', "''", ':', 'The', 'stranger', 'ignored', 'him', '.']
        colon = words.index(":")
        assert words[colon - 1] == "''"
        assert words[colon - 2] == "a-drinking"
        assert words[colon + 1] == "The"
        words[colon] = "."
        s1 = words[:colon + 1]
        s2 = words[colon + 1:]
        assert s2[0] == "The"
        return [s1, s2]
    else:
        return [words]

def p19_fixup(idx, words):
    if idx == 19:
        assert words[-1] == "anyhow"
        words.append("...")
    return [words]

def ww12_fixup_in_place(idx, words):
    for i in xrange(len(words) - 2):
        if (words[i].lower() == "world"
            and words[i + 1].lower() == "war"):
            subs = {"1": "I", "2": "II"}
            if words[i + 2] in subs:
                words[i + 2] = subs[words[i + 2]]

def ww12_fixup(idx, words):
    ww12_fixup_in_place(idx, words)
    return [words]

def n21_fixup(idx, words):
    ww12_fixup_in_place(idx, words)
    if idx == 2:
        assert words[-1] == "."
        assert words[-2] == "do"
        words[-1] = "..."
    if idx == 8:
        assert words[9] == "Max"
        words.insert(10, "...")
    return [words]

def f22_fixup(idx, words):
    if idx == 32:
        assert "A[fj]" in words
        words[words.index("A[fj]")] = "A"
    return [words]

def f05_fixup(idx, words):
    ww12_fixup_in_place(idx, words)
    if idx == 12:
        # "N.", "Y", ".", "." -> "N. Y."
        assert words[-4:] == ["N.", "Y", ".", "."]
        words[-4:] = ["N. Y."]
    if idx == 14:
        # "N.", "H", ".", "." -> "N. H."
        assert words[-4:] == ["N.", "H", ".", "."]
        words[-4:] = ["N. H."]
    if idx in (24, 27):
        # "World War I ," -> "World War I"
        I_idx = words.index("I")
        assert words[I_idx - 2] == "World"
        assert words[I_idx - 1] == "War"
        assert words[I_idx + 1] == ","
        words.pop(I_idx + 1)
    if idx == 24:
        # Weird construction "airports, And the" -- it's there in the
        # original; maybe it should be a sentence break, or a semicolon, but
        # I'm just going to fix the capitalization and leave it at that
        words[words.index("And")] = "and"
    return [words]

def f02_fixup(idx, words):
    ww12_fixup_in_place(idx, words)
    if idx == 6:
        words[words.index("despatched")] = "dispatched"
    return [words]

# Question format:
# (0, # question number (unique within text number)
#  "The school is located in New York State.", # question text
#  TRUE),  # answer -- tuple of (correct, incorrect) code
texts = [
    Text(0, "f22", "The Fighting Seventh", range(0, 34),
         [(0, "'Garryowen!' is an old Irish battle-cry.", FALSE),
          (1, "The 7th U.S. Cavalry Regiment has fought in the South Pacific.", TRUE),
          (2, "Mel Chandler was just a bureaucrat before he became commander of the 7th Regiment.", TRUE),
          (3, "When Mel Chandler joined the 7th Regiment, they were disorganized and had low morale.", FALSE),
          ],
         fixup=f22_fixup),
    Text(1, "f20", "The gangster", range(2, 14),
         [(0, "O'Banion hesitated before killing people.", FALSE),
          (1, "O'Banion was an expert florist.", TRUE),
          (2, "O'Banion's left leg was shorter than his right", FALSE),
          (3, "O'Banion was an alcoholic.", FALSE),
          ]),
    Text(2, "n26", "A Western story", range(0, 41),
         [(0, "Blue Throat is the hero of this passage.", FALSE),
          (1, "Pat Conyers was killed in a gambling brawl.", TRUE),
          (2, "Billy Tilghman and Pat Conyers were enemies.", FALSE),
          (3, "Blue Throat had six henchmen with him in the bar.", TRUE),
          ],
         fixup=n26_fixup),
    Text(3, "f02", "The ship \"John Harvey\"",
         range(0, 28),  # or 6, 22 for a shorter passage
         [(0,
           "Use of poison gas was common in the early part of World War II",
           FALSE),
          (1,
           "Many people knew that poison gas was on board the John Harvey", FALSE),
          (2,
           "President Roosevelt announced that the United States reserved the right to use poison gas pre-emptively if it obtained solid information that the Axis countries were planning poison gas attacks on Allied forces.",
           FALSE),
          (3, "The port at which the U.S. was stocking mustard gas was in southern France, near the Italian border.", FALSE),
          ],
         fixup=f02_fixup),
    Text(4, "f10", "California medicine", range(0, 32),
         [(0,
           "According to Lee, the body requires 120 units of blue light every day",
           FALSE),
          (1, "Claire Shaefer is a fraudulent physician.", FALSE),
          (2, "Over five hundred people bought ozone machines.", TRUE),
          (3, "Lee sold cans of mud for the purpose of removing wrinkles.", TRUE),
          ]),
    Text(5, "f21", "Tsunamis", range(0, 11),
         [(0, "Tsunamis are caused by volcanoes and earthquakes.", TRUE),
          (1, "In 1707 a single tsunami destroyed more than 1,000 boats.", TRUE),
          (2, "Tsunamis have not been recorded in the Atlantic Ocean since the 17th century.", FALSE),
          (3, "The 1883 tsunami launched by the explosion of Krakatoa caused waves over 100 feet high in Java and Sumatra.", TRUE),
          ]),
    Text(6, "k06", "The new town", range(41, 86),
         [(0, "Stephen is woken in the morning by his alarm clock.", FALSE),
          (1, "Stephen's father is a preacher.", TRUE),
          (2, "The story is set on the East coast.", TRUE),
          (3, "Stephen often accompanies his father while working.", TRUE),
          ]),
    Text(7, "n20", "Lost in the wasteland", range(0, 52),
         [(0, "Ben Prime and his wife are on their honeymoon.", TRUE),
          (1, "Ben Prime's wife is named Hattie.", TRUE),
          (2, "Ben Prime and his wife agreed on how to get more water but couldn't find any.", FALSE),
          (3, "Ben Prime and his wife were traveling in a vehicle drawn by horses.", FALSE),
          ]),
    Text(8, "f05",
         "The mail must go through!",
         range(0, 28),
         [(0, "The road was lost in a flood.", TRUE),
          (1, "In 1927, there were no airports in Vermont.", TRUE),
          (2, "The term \"iron compass\" in this text refers to the compass carried in the cockpit of most biplanes flown in the 1920s.", FALSE),
          (3, "The pilots of the York State Guard were unable to deliver the mail on a regular schedule.", TRUE)
          ],
         fixup=f05_fixup),
    Text(9, "p19",
         "My daughter Gladdy",
         range(0, 30),
         [(0, "Gladdy's father is a doctor.", TRUE),
          (1, "Gladdy's sister is named Alice.", FALSE),
          (2, "Alice is alive.", FALSE),
          (3, "Gladdy's father is named Pete Michelson.", FALSE),
          ],
         fixup=p19_fixup),
    Text(10, "n21",
         # This is the real original title.
         # Here's the cover:
         #    http://www.philsp.com/data/images/c/cavalcade_196110.jpg
         "The Beautiful Mankillers of Eromonga",
         range(0, 44),
         [(0, "Their ship was attacked by pirates.", FALSE),
          (1, "There were five survivors from the ship's sinking.", FALSE),
          (2, "According to the narrator, undergraduate anthropology classes teach the Manu language.", TRUE),
          (3, "The people of Eromonga live in an all-female society.", TRUE),
          ],
         fixup=n21_fixup),
    Text(11, "f24", "The war in Laos", range(0, 23) + range(24, 41),
         [(0, "The author is woken by gunfire from a rebel attack.", FALSE),
          (1, "Loud noise is believed necessary to end a lunar eclipse.", TRUE),
          (2, "At the time of writing, Laos was under siege.", TRUE),
          (3, "The American embassy, however, has survived intact.", FALSE),
          ]),
    Text(12, "f16", "The last voyage", range(0, 42),
         [(0, "Of the Discovery's original crew, all but four men were missing when it returned to London in 1611.", FALSE),
          (1, "Henry Hudson obtained the patronage of the Prince of Wales in the spring of 1610.", TRUE),
          (2, "The voyage of the Discovery was funded by the Dutch East India Company.", FALSE),
          (3, "The Discovery had a smaller crew than that of the Half Moon.", FALSE),
          ]),
    # Practice texts
    Text(13, "f09", "(Practice) Carpeting", range(120, 129),
         [(0, "This salesman primarily sells oriental rugs.", FALSE),
          (1, "This salesman abuses his customer's trust.", TRUE),
          ],
         type=PRACTICE),
    Text(14, "f11", "(Practice) Orthodontics", range(0, 8),
         [(0, "The children at school gave Richard the nickname \"Yosemite Sam.\"", FALSE),
          (1, "The orthodontist successfully straightened Richard's teeth.", TRUE),
          ],
         type=PRACTICE),
    Text(15, "f09", "(Practice) The golden girl", range(0, 6),
         [(0, "Lady Diana Harrington died in Houston.", TRUE),
          (1, "'Lady Diana Harrington' is the name she was born with.", FALSE),
          ],
         type=PRACTICE),
    # Mutilated texts
    Text(16, "f04", "Modern farming",
         range(0, 10) + range(11, 30), # This has an embedded title
         [(0,
           "The school is located in New York State.",
           TRUE),
          (1, 
           "The director of this school is named Walter E. Clark.", 
           TRUE),
          (2, "This 1960s school serves organic food.", TRUE),
          (3,
           "The soil on the school farm is kept moist through a sophisticated system of irrigation",
           FALSE),
          ],
         fixup=f04_fixup,
         type=MUTILATED,
         mutilations=[
             Sem(0, 26, "parents", 12, 35, "provisions"),
             Sem(1, 50, "programs", 4, 274, "pounds"),
             Syn(2, 60, "selected", "selects"),
             Syn(3, 93, "allows", "allow"),
             Sem(4, 134, "work", 6, 439, "tollgate"),
             Syn(5, 165, "located", "locate"),
             Sem(6, 179, "school", 10, 231, "roar"),
             Syn(7, 204, "come", "comes"),
             Sem(8, 229, "care", 8, 29, "engine"),
             Syn(9, 241, "caring", "cares"),
             Syn(10, 268, "began", "begin"),
             Sem(11, 282, "needs", 12, 192, "records"),
             Sem(12, 303, "farm", 12, 38, "voyage"),
             Sem(13, 324, "quick-drying", 8, 362, "hastily-summoned"),
             Syn(14, 342, "bear", "bears"),
             Syn(15, 377, "prevent", "preventing"),
             Sem(16, 425, "help", 4, 149, "stream"),
             Syn(17, 432, "excited", "exciting"), #?
             Syn(18, 441, "convinced", "convince"),
             Sem(19, 450, "equipment", 7, 267, "mouth"),
             Syn(20, 467, "stopped", "stop"),
             Sem(21, 484, "animals", 10, 237, "sparks"),
             Syn(22, 507, "kept", "keep"),
             Sem(23, 525, "fertilizers", 2, 8, "tables"),
             Syn(24, 543, "applied", "applies"),
             Sem(25, 569, "soil", 10, 468, "mandate"),
             Sem(26, 588, "soil", 0, 63, "trooper"),
             Syn(27, 604, "accomplished", "accomplish"),
             Sem(28, 613, "gardens", 2, 67, "kids"),
             Syn(29, 645, "pointed", "point"),
         ]),
    Text(17, "n18", "A Southern affair", range(0, 26),
         [(0,
           "According to the narrator, you should read classic literature to learn the best way to have an affair.", TRUE),
          (1, "The Uncle is his father's brother.", FALSE),
          (2, "The narrator moved to New Orleans after finishing college.", TRUE),
          (3,
           "The narrator was closer in age to his new Aunt than his Uncle was.",
           TRUE),
          ],
         type=MUTILATED,
         mutilations=[
             Sem(0, 85, "people", 5, 51, "waves"),
             Sem(1, 118, "shops", 4, 508, "agents"),
             Syn(2, 136, "work", "working"),
             Sem(3, 159, "man", 10, 495, "stone"),
             Syn(4, 172, "overlooked", "overlook"),
             Sem(5, 214, "colony", 3, 520, "shower"),
             Syn(6, 226, "take", "taking"),
             Sem(7, 258, "spirit", 7, 22, "valley"),
             Sem(8, 279, "romance", 8, 77, "gravel"),
             Syn(9, 300, "waiting", "wait"),
             Sem(10, 315, "fun", 10, 8, "tinder"),
             Sem(11, 335, "masks", 4, 129, "tubes"),
             Syn(12, 343, "were", "is"),
             Syn(13, 370, "died", "die"),
             Sem(14, 391, "woman", 2, 296, "stomach"),
             Syn(15, 421, "looked", "look"),
             Sem(16, 461, "woman", 12, 641, "water"),
             Syn(17, 485, "held", "holding"),
             Syn(18, 501, "fascinate", "fascinates"),
             Sem(19, 515, "wine", 11, 262, "moon"),
             Sem(20, 528, "ankle", 6, 428, "choir"),
             Syn(21, 538, "dwell", "dwelling"),
             Syn(22, 571, "reconstruct", "reconstructs"),
             Sem(23, 585, "bosom", 4, 577, "county"),
             Syn(24, 615, "brought", "bring"),
         ]),
    Text(18, "f04", "Modern farming",
         range(0, 10) + range(11, 30), # This has an embedded title
         [(0,
           "The school is located in New York State.",
           TRUE),
          (1, 
           "The director of this school is named Walter E. Clark.", 
           TRUE),
          (2, "This 1960s school serves organic food.", TRUE),
          (3,
           "The soil on the school farm is kept moist through a sophisticated system of irrigation",
           FALSE),
          ],
         fixup=f04_fixup,
         type=MUTILATED_AVAILABLE,
         ),
    Text(19, "n18", "A Southern affair", range(0, 26),
         [(0,
           "According to the narrator, you should read classic literature to learn the best way to have an affair.", TRUE),
          (1, "The Uncle is his father's brother.", FALSE),
          (2, "The narrator moved to New Orleans after finishing college.", TRUE),
          (3,
           "The narrator was closer in age to his new Aunt than his Uncle was.",
           TRUE),
          ],
         type=MUTILATED_AVAILABLE,
         ),
    ]

import copy
correct_para_texts = copy.deepcopy(texts)
for text in correct_para_texts:
    text.load_paragraphs(True)

# Parsed text:
#   -- has typo fixes, proper characters, etc.
#   -- clitics are parsed out into separate words ('re, 's, etc.)
#   -- No paragraph breaks!
#   -- No titles!

def cleanup_raw(words):
    words = list(words)
    # Remove doubled punctuation
    words = strip_double_punct(words)
    # Push close-quotes rightwards, outside of any following punctuation
    for i in xrange(len(words) - 1):
        if words[i] == "''" and all_punct(words[i + 1]):
            tmp = words[i]
            words[i] = words[i + 1]
            words[i + 1] = tmp
    # Normalize dashes to "--":
    for i in xrange(len(words)):
        if set(words[i]) == set("-"):
            words[i] = "--"
    return words

def test_cleanup_raw():
    def t(a, b):
        cleaned = cleanup_raw(a)
        print cleaned
        assert cleaned == b
    t(["a", "b"], ["a", "b"])
    t(["foo", "''", "."], ["foo", ".", "''"])
    t(["''", "``", "-"], ["``", "--", "''"])
    t(["``", "-"], ["``", "--"])
    t(["foo", "-", "--", "---", "bar"], ["foo", "--", "bar"])
    t(["-", "-", "foo", "-", "-"], ["--", "foo", "--"])
    t(["should", "n't", "'ve", "#"], ["should", "n't", "'ve", "#"])

def find_display_breaks_in_raw_words(words):
    breaks = []
    # Problem: when merging raw words into display words, some items go
    # right (open-parens, etc.), some items go left (most punctuation,
    # clitics, etc.), and some items are "nucleuses", centers of gravity that
    # the left- and right-going items glom onto (most words).
    # Solution: convert to a representation in terms of these "gravities",
    # then insert breaks whenever a word-breaking transition occurs.
    #
    # Note that "left" means left-going, i.e. an item that you will see on the
    # right side of a word.
    RIGHT = "right"
    NUCLEUS = "nucleus"
    LEFT = "left"
    BREAK_TRANSITIONS = set([(LEFT, RIGHT),
                             (LEFT, NUCLEUS),
                             (NUCLEUS, NUCLEUS),
                             (NUCLEUS, RIGHT)])
    def gravity(word):
        if word in ("$", "(", "``"):
            return RIGHT
        elif all_punct(word) or clitic(word):
            return LEFT
        else:
            return NUCLEUS
    gravities = [gravity(word) for word in words]
    # Special case: no breaks allowed to be caused by sentence-initial
    # punctuation alone; skip past all of it when looking for breaks:
    for first_non_punct in xrange(len(words)):
        if not all_punct(words[first_non_punct]):
            break
    for i in xrange(first_non_punct + 1, len(gravities)):
        if (gravities[i - 1], gravities[i]) in BREAK_TRANSITIONS:
            breaks.append(i)
    return breaks

def test_find_display_breaks_in_raw_words():
    def t(a, b):
        breaks = find_display_breaks_in_raw_words(a)
        print breaks
        assert breaks == b
    t(["foo", "bar", "baz"], [1, 2])
    t(["foo", "$", "baz"], [1])
    t(["foo", "``", "$", "baz"], [1])
    t(["foo", "''", "$", "baz"], [2])
    t(["''", ",", "+", "asdf"], [])
    t(["'til", "the"], [1])
    t(["''", "hi", "''", "she", "said", "."], [3, 4])
    t(["hi", "``", "she", "said", "."], [1, 3])

def merge_raw_words_for_display(raw_words):
    merged = []
    words = cleanup_raw(raw_words)
    breaks = find_display_breaks_in_raw_words(words)

    start = 0
    for b in breaks + [len(words)]:
        group = words[start:b]
        # Dashes get a space inserted before them in the display, and
        # double-quotes get normalized to " (b/c we don't have access to
        # proper curly-quotes in our stimulus presentation software).
        for i in xrange(len(group)):
            if group[i] == "--":
                group[i] = " " + group[i]
            if group[i] in ("``", "''"):
                group[i] = "\""
        merged.append("".join(group))
        start = b
    return merged

def test_merge_raw_words_for_display():
    assert (merge_raw_words_for_display(["...", "foo", "``", "bar", "-", "baz"])
            == ["...foo", "\"bar --", "baz"])

def old_munge_punctuation_tests():
    def tm(a, b):
        munged = merge_raw_words_for_display(a)
        print munged
        assert munged == b
    tm(["``", ",", "+", "asdf"], ["\",+asdf"])
    tm(["'til", "the"], ["'til", "the"])
    tm(["five", "o'clock", "and"], ["five", "o'clock", "and"])
    # first punct goes right, later goes left
    tm(["''", "hi", "''", "she", "said", "."],
       ["\"hi\"", "she", "said."])
    # clitics attach
    tm(["it", "'s", "."], ["it's."])
    # open-quotes go right
    tm(["he", "said", "``", "hi", "''", "yes"],
       ["he", "said", "\"hi\"", "yes"])
    # n't is a clitic that doesn't start with '
    tm(["do", "n't", ",", "does", "n't"], ["don't,", "doesn't"])
    # dollar signs go right
    tm(["for", "$", "30"], ["for", "$30"])
    # attach dashes with a space
    tm(["foo", "--", "bar"], ["foo --", "bar"])
    # doubled punctuation:
    tm(["foo", ",", ",", "bar"], ["foo,", "bar"])
    # parens go right
    tm(["foo", "(", "bar", ")"], ["foo", "(bar)"])
    # close-quotes get shoved after any adjacent punctuation
    tm(["foo", "''", "!", "."], ["foo!.\""])

# Useful for testing that word numbers and display words have not changed
# after refactoring:
def debug_dump_all(path):
    f = open(path, "w")
    for t in texts:
        for (i, numbers, display) in t.indexed_and_numbered_display_sentences():
            f.write(repr(zip(numbers, display)) + "\n")

if __name__ == "__main__":
    import nose
    nose.runmodule()
