# Snapshot of njs.munge

def flatten(iterable_of_iterables):
    # Better to be non-recursive, but I'm lazy...
    result = []
    for item in iterable_of_iterables:
        if iterable(item) and not isinstance(item, (str, unicode)):
            result += flatten(item)
        else:
            result.append(item)
    return result

def test_flatten():
    assert flatten([]) == []
    assert flatten([1, 2, 3]) == [1, 2, 3]
    assert flatten([[1], [2], [3]]) == [1, 2, 3]
    assert flatten([[1, 2, [3]], ((4,), 5)]) == [1, 2, 3, 4, 5]
    # Make sure it doesn't try to recurse into strings
    assert flatten(["1"]) == ["1"]
    assert flatten([("1", "2"), ((("3",),),)]) == ["1", "2", "3"]
    assert flatten([u"1"]) == [u"1"]

def all_punct(string):
    for char in string:
        if char.isalnum():
            return False
    return True

def test_all_punct():
    assert all_punct("'$#-")
    assert not all_punct("asdfj")
    assert not all_punct("o'clock")
    assert not all_punct("'til")
    assert not all_punct("'08")

def has_punct(string):
    for char in string:
        if not char.isalnum():
            return True
    return False

def test_has_punct():
    assert has_punct("'$#-")
    assert not has_punct("asdfj")
    assert not has_punct("2010")
    assert has_punct("o'clock")
    assert has_punct("'til")
    assert has_punct("'08")


all_multichar_puncts = set(["...", "--", "---", "''", "``"])

# Arguably there are some places where we shouldn't split punctuation, like:
#   S.A.T.
#   -100
#   e.g.
#   124p.
#   L+
#   -US$100
#   +28.4
# but for now we think that such cases can be safely ignored (cross fingers!)
# (* This list acquired by running over the BNC, finding tokens that
# split_punct was not a no-op on.  There are also huge number of screwily
# formatted words in the BNC, stuff with attached ellipses and such
# wackiness.)
def split_punct(word):
    after = []
    while True:
        if not word:
            break
        for m in all_multichar_puncts:
            if word.endswith(m):
                after.insert(0, m)
                word = word[:-len(m)]
                break
        else:
            if not word[-1].isalnum():
                after.insert(0, word[-1])
                word = word[:-1]
            else:
                break
    before = []
    while True:
        if not word:
            break
        for m in all_multichar_puncts:
            if word.startswith(m):
                before.append(m)
                word = word[len(m):]
                break
        else:
            if not word[0].isalnum():
                before.append(word[0])
                word = word[1:]
            else:
                break
    if word:
        return before + [word] + after
    else:
        return before + after

def test_split_punct():
    def t(a, b):
        print a, b
        assert split_punct(a) == b
    t("foo", ["foo"])
    t("-*$foo-)*@", ["-", "*", "$", "foo", "-", ")", "*", "@"])
    t("--...`foo''``", ["--", "...", "`", "foo", "''", "``"])
    t("-", ["-"])
    t("--...", ["--", "..."])

all_clitics = set(["'d", "'ll", "'m", "'re", "'s", "'ve", "n't"])

def clitic(word):
    return word.lower() in all_clitics

def test_clitic():
    assert clitic("n't")
    assert clitic("'ll")
    assert not clitic("hi")
    assert not clitic("'90s")

# This is not robust against case issues (e.g. words in ALLCAPS):
def split_clitics(word):
    clitics = []
    while True:
        for c in all_clitics:
            if word.lower().endswith(c):
                clitics.insert(0, word[-len(c):])
                word = word[:-len(c)]
                break
        else:
            break
    return [word] + clitics

def test_split_clitics():
    def t(a, b):
        assert split_clitics(a) == b
    t("foo", ["foo"])
    t("foon't", ["foo", "n't"])
    t("shouldn't've", ["should", "n't", "'ve"])
    t("a've's", ["a", "'ve", "'s"])
    t("shOUldn'T'Ve", ["shOUld", "n'T", "'Ve"])

def merge_clitics(word_list):
    new_word_list = []
    for word in word_list:
        if (clitic(word)
            and new_word_list
            and not all_punct(new_word_list[-1])):
            new_word_list[-1] += word
        else:
            new_word_list.append(word)
    return new_word_list

def test_merge_clitics():
    def t(a, b):
        assert merge_clitics(a) == b
    t(["foo", "bar"], ["foo", "bar"])
    t(["foo", ",", "bar"], ["foo", ",", "bar"])
    t(["should", "n't", "'ve"], ["shouldn't've"])
    t(["should", ",", "n't", "'ve"], ["should", ",", "n't've"])
    t(["'ll", "'m"], ["'ll'm"])
    t(["``", "'m"], ["``", "'m"])

def strip_double_punct(word_list):
    new_word_list = []
    for word in word_list:
        if all_punct(word) and new_word_list and word == new_word_list[-1]:
            continue
        else:
            new_word_list.append(word)
    return new_word_list

def test_strip_double_punct():
    def t(a, b):
        assert strip_double_punct(a) == b
    t(["a", "b", "b", "c"], ["a", "b", "b", "c"])
    t(["a", "-", ".", ":"], ["a", "-", ".", ":"])
    t(["a", "-", "-", "-", ":"], ["a", "-", ":"])
    t(["-", "-", "+"], ["-", "+"])

def split_and_strip_hyphens(word):
    if word.startswith("-"):
        # A bare hyphen, or part of an en/em-dash, or a negative
        # number... just ignore it.
        return [word]
    if word.endswith("-"):
        # Weird trailing hyphen... just kill it
        word = word[:-1]
    return word.split("-")

def test_split_and_strip_hyphens():
    assert split_and_strip_hyphens("self-defeating") == ["self", "defeating"]
    assert split_and_strip_hyphens("R-rated") == ["R", "rated"]
    assert split_and_strip_hyphens("-") == ["-"]
    assert split_and_strip_hyphens("---") == ["---"]
    assert split_and_strip_hyphens("-3") == ["-3"]
    assert split_and_strip_hyphens("-30-") == ["-30-"]
    assert split_and_strip_hyphens("self-") == ["self"]
    assert split_and_strip_hyphens("self-defeating-") == ["self", "defeating"]

def normalize_quote(suspected_quote):
    if suspected_quote in ("``", "''"):
        return '"'
    else:
        return suspected_quote

def munge_word_to_generic_lm(word, kill_hyphens, do_split_clitics):
    pieces = split_punct(word)
    pieces = [normalize_quote(piece) for piece in pieces]
    if kill_hyphens:
        pieces = flatten([split_and_strip_hyphens(piece)
                          for piece in pieces])
    if do_split_clitics:
        pieces = flatten([split_clitics(piece) for piece in pieces])
    return tuple(pieces)

# Takes a list of words:
#   ["When", "in", "the", "course", ...]
# Returns a list of word tuples:
#   [("When",), ("in",), ("the",), ("course",), ...]
def munge_to_generic_lm(words, kill_hyphens, do_split_clitics):
    return [munge_word_to_generic_lm(word, kill_hyphens, do_split_clitics)
            for word in words]
    
def test_munge_to_generic_lm():
    def t(hyphens, clitics, a, b):
        munged = munge_to_generic_lm(a, hyphens, clitics)
        print munged
        assert munged == b
    t(False, True, ["When", "in", "the", "course"],
      [("When",), ("in",), ("the",), ("course",)])
    t(False, True, ["I", "can't...", "-stay"],
      [("I",), ("ca", "n't", "..."), ("-", "stay")])
    t(False, True,
      ["The", "R-rated-", "movie"], [("The",), ("R-rated", "-"), ("movie",)])
    t(True, True,
      ["The", "R-rated-", "movie"], [("The",), ("R", "rated", "-"), ("movie",)])
    t(True, False,
      ["The", "R-rated-", "can't."],
      [("The",), ("R", "rated", "-"), ("can't", ".")])
    t(False, False,
      ["The", "R-rated-", "can't."],
      [("The",), ("R-rated", "-"), ("can't", ".",)])

def _bnc_specific_textual_fixups(word):
    # BNC has no punctuation for titles:
    # (Surely there are more I'm not thinking of?)
    for title in ["Mrs", "Mr", "Dr", "Prof", "Lt", "Adm"]:
        word = word.replace(title + ".", title)
    # BNC uses "-" for all dashes (with a few scattered exceptions, of
    # course):
    while word.replace("--", "-") != word:
        word = word.replace("--", "-")
    return word

def munge_word_to_bnc_lm(word):
    word = _bnc_specific_textual_fixups(word)
    return munge_word_to_generic_lm(word, False, True)

def munge_to_bnc_lm(words):
    return [munge_word_to_bnc_lm(word) for word in words]

def munge_word_to_declitic_bnc_lm(word):
    word = _bnc_specific_textual_fixups(word)
    return munge_word_to_generic_lm(word, False, False)

def munge_to_declitic_bnc_lm(words):
    assert merge_clitics(words) == words
    return [munge_word_to_declitic_bnc_lm(word) for word in words]

def test_munge_to_declitic_bnc_lm():
    assert munge_to_declitic_bnc_lm(["A", "b", "c"]) == [("A",), ("b",), ("c",)]
    assert munge_to_declitic_bnc_lm(["can't."]) == [("can't", ".")]
    try:
        munge_to_declitic_bnc_lm(["ca", "n't", "."])
    except:
        pass
    else:
        assert False, "failed to raise"

def munge_word_to_google_lm(word):
    # Could happen if we are given pre-tokenized text, but by this point it's
    # too late to handle this case correctly (because if we are processing
    # ["ca", "n't"] we would produce [("ca",), ("not",)]). Call merge_clitics
    # if you have such text.
    assert word != "n't"
    # Bizarrely, the Google ngrams tokenize "can't" as "can not", "won't" as
    # "will not", etc.
    # In all of the BNC, the irregulars with n't are:
    #    can't, won't, ain't, shan't
    # (Irregular meaning, not like "couldn't" -> "could not" etc.)
    # Looking at google, the mappings are:
    #    can't -> can not
    #    won't -> will not
    #    ain't -> ???? (not "ai n't" or "ai not")
    #    shan't -> shall not, far as I can tall (not "shall n't", "sha n't",
    #              "sha not")
    # So first we do a pass looking for these weirdos:
    split_word = list(munge_word_to_generic_lm(word, True, True))
    irregulars = {"ca": "can",
                  "wo": "will",
                  "sha": "shall",
                  }
    for i in xrange(len(split_word) - 1):
        if (split_word[i].lower() in irregulars
            and split_word[i + 1].lower() == "n't"):
            new = irregulars[split_word[i].lower()]
            if split_word[i].isupper():
                new = new.upper()
            elif split_word[i].istitle():
                new = new.title()
            split_word[i] = new
    # And then just turn n't -> not
    for i in xrange(len(split_word)):
        if split_word[i] == "n't":
            split_word[i] = "not"
        elif split_word[i] == "N'T":
            split_word[i] = "NOT"
    return tuple(split_word)

def munge_to_google_lm(words):
    return [munge_word_to_google_lm(word) for word in words]

def test_munge_to_google_lm():
    def t(a, b):
        munged = munge_to_google_lm(a)
        print munged
        assert munged == b
    t(["When", "in", "the", "course"],
      [("When",), ("in",), ("the",), ("course",)])
    t(["I", "can't...", "-stay"],
      [("I",), ("can", "not", "..."), ("-", "stay")])
    t(["In't"], [("I", "not")])
    t(["--can't,"], [("--", "can", "not", ",")])
    t(["can't", "won't", "shan't"],
      [("can", "not"), ("will", "not"), ("shall", "not")])
    t(["Can't", "Won't", "Shan't"],
      [("Can", "not"), ("Will", "not"), ("Shall", "not")])
    t(["CAN'T", "WON'T", "SHAN'T"],
      [("CAN", "NOT"), ("WILL", "NOT"), ("SHALL", "NOT")])
    t(["don't", "didn't", "wasn't", "doesn't"],
      [("do", "not"), ("did", "not"), ("was", "not"), ("does", "not")])
    t(["DON'T", "DIDN'T", "WASN'T", "DOESN'T"],
      [("DO", "NOT"), ("DID", "NOT"), ("WAS", "NOT"), ("DOES", "NOT")])
    t(["-ca!"], [("-", "ca", "!")])
    t(["an", "R-rated", "movie,"], [("an",), ("R", "rated"), ("movie", ",")])

##### Below this is detritus, not sure what to do with it


# Some language models (e.g., the simple BNC model, and the Google ngrams in
# practice) use only " characters, so to use such model we need to normalize
# our `` and '' quotes to that.  But open and close quotes behave differently
# when coalescing punctuation into display words, e.g. for the Brown stimuli.
# So this class lets us normalize both sorts of quotes to ", while retaining a
# hint about which sort of quote they started out as.
#
# OTOH, other language models (like our current Brown model) do not so
# normalize double-quotes, so we have both options, here.
class Quote(str):
    def __new__(cls, s, normalize):
        if normalize:
            # Normalize:
            self = str.__new__(cls, '"')
        else:
            # Don't normalize:
            self = str.__new__(cls, s)
        # Preserve information in either case:
        self.type = s
        return self

# This assumes that its input has already been broken into words (including
# punctuation separated off as separate "words"):
def munge_sentence_to_lm(words, normalize):
    words = list(words)
    # Push close-quotes rightwards, outside of any following punctuation
    for i in xrange(len(words) - 1):
        if words[i] == "''" and all_punct(words[i + 1]):
            tmp = words[i]
            words[i] = words[i + 1]
            words[i + 1] = tmp
    # Turn `` and '' into Quote objects, and normalize dashes to "--"
    for i in xrange(len(words)):
        if words[i] in ("``", "''"):
            words[i] = Quote(words[i], normalize)
        if set(words[i]) == set("-"):
            words[i] = "--"
    # Remove doubled punctuation
    # Can't use range() because len(words) will change as we go:
    i = 0
    while i < len(words) - 1:
        if all_punct(words[i]) and words[i + 1] == words[i]:
            words.pop(i)
        else:
            i += 1
    # Merge separated clitics (as seen in parsed trees) into single words:
    i = 0
    while i < len(words) - 1:
        if words[i + 1] in all_clitics:
            words[i] += words.pop(i + 1)
        else:
            i += 1
    return words

def test_munge_sentence_to_lm():
    def t(normalize, a, b):
        munged = munge_sentence_to_lm(a, normalize)
        print munged
        assert munged == b
    for normalize in (True, False):
        print "normalize: %s" % normalize
        t(normalize, ["a", "b"], ["a", "b"])
        t(normalize, ["foo", "''", "."], ["foo", ".", Quote("''", normalize)])
        t(normalize,
          ["''", "``", "-"],
          [Quote("``", normalize), "--", Quote("''", normalize)])
        t(normalize, ["``", "-"], [Quote("``", normalize), "--"])
        t(normalize, ["foo", "-", "--", "---", "bar"], ["foo", "--", "bar"])
        t(normalize, ["-", "-", "foo", "-", "-"], ["--", "foo", "--"])
        assert munge_sentence_to_lm(["``"], normalize)[0].type == "``"
        assert munge_sentence_to_lm(["''"], normalize)[0].type == "''"
        t(normalize, ["should", "n't", "'ve", "#"], ["shouldn't've", "#"])

if __name__ == "__main__":
    import nose
    nose.runmodule()
