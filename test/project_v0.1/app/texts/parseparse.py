# For parsing brown parse-tree sexps

import sys

EOF = "eof"
OPEN = "("
CLOSE = ")"

magic = {
    "": EOF,
    "(": OPEN,
    ")": CLOSE,
    " ": None,
    "\t": None,
    "\n": None,
    }

def tokenize(f):
    c = f.read(1)
    while True:
        if c in magic:
            token = magic[c]
            if token is not None:
                yield token
                if token is EOF:
                    return
            c = f.read(1)
        else:
            token = [c]
            while True:
                c = f.read(1)
                if c not in magic:
                    token.append(c)
                else:
                    break
            yield "".join(token)

def test_tokenize():
    from cStringIO import StringIO
    def tt(s, t):
        tokenized = list(tokenize(StringIO(s)))
        print tokenized
        assert tokenized == t
    tt("", [EOF])
    tt("((foo))", [OPEN, OPEN, "foo", CLOSE, CLOSE, EOF])
    tt("foo bar ( \n\n\t  (", ["foo", "bar", OPEN, OPEN, EOF])

def parse(f):
    stack = []
    for token in tokenize(f):
        if token is EOF:
            assert not stack
            return
        elif token is OPEN:
            stack.append([])
        elif token is CLOSE:
            body = stack.pop()
            if stack:
                stack[-1].append(body)
            else:
                yield body
        else:
            if stack:
                stack[-1].append(token)
            else:
                yield token

def test_parse():
    from cStringIO import StringIO
    def tp(s, p):
        print s
        parsed = list(parse(StringIO(s)))
        print parsed
        assert parsed == p
    tp("", [])
    tp("asdf foo", ["asdf", "foo"])
    tp("(asdf)", [["asdf"]])
    tp("(asdf (b  c) ((d)))", [["asdf", ["b", "c"], [["d"]]]])
    tp("(asdf) (foo bar) (baz)", [["asdf"], ["foo", "bar"], ["baz"]])

def reduce_tree_to_words(tree):
    if isinstance(tree, str):
        if tree == "-LRB-":
            tree = "("
        if tree == "-RRB-":
            tree = ")"
        return [tree]
    else:
        if isinstance(tree[0], list):
            head = None
            rest = tree
        else:
            head, rest = tree[0], tree[1:]
            assert isinstance(head, str)
        if head == "-NONE-":
            return []
        words = []
        for subtree in rest:
            words += reduce_tree_to_words(subtree)
        return words

def test_rttw():
    assert(reduce_tree_to_words(["S",
                                 ["N", "a"],
                                 ["V", ["DT", "b"], ["V", "c"]]])
           == ["a", "b", "c"])
    assert(reduce_tree_to_words(["S",
                                 ["N", "a"],
                                 ["V", ["-NONE-", "b"], ["V", "c"]]])
           == ["a", "c"])
    assert(reduce_tree_to_words([["S",
                                  ["N", "a"],
                                  ["V", ["DT", "b"], ["V", "c"]]]])
           == ["a", "b", "c"])
        
def words_only(f):
    for tree in parse(f):
        for word in reduce_tree_to_words(tree):
            yield word

def trees_to_normed_text(f, o):
    for word in words_only(f):
        word = {"``": "\"",
                "''": "\"",
                "--": "-",
                }.get(word, word)
        word.replace("/", "")
        for punct in ".!?":
            word = word.replace(punct, punct + "\n")
        o.write(word.lower())

def text_to_normed_text(f, o):
    for line in f:
        text = line[len("F01 0010  1    "):]
        normed = "".join(text.strip().split()).lower()
        for a, b in [("&", "."), ("**h", ""), ("~", ""), ("#", ""),
                     ("/", ""), ("@", ""),
                     (".", ".\n"), ("!", "!\n"), ("?", "?\n")]:
            normed = normed.replace(a, b)
        o.write(normed)

def normtwo(raw_path, tree_path):
    text_to_normed_text(open(raw_path), open(raw_path + ".normed", "w"))
    trees_to_normed_text(open(tree_path), open(tree_path + ".normed", "w"))

if __name__ == "__main__":
    import sys
    if sys.argv[1] == "test":
        import nose
        nose.runmodule()
    else:
        normtwo(*sys.argv[1:])
