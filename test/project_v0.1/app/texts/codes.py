# m = CodeManager()
# m.rule("button_1", 1024)
# m.rule("semantic_anomaly", 52000, [("text", 20), ("anomaly", 100)], 53999)

def odometer_iter(maximums):
    cur = [0] * len(maximums)
    yield tuple(cur)
    if not maximums:
        return
    while True:
        cur[0] += 1
        for i in xrange(len(cur) - 1):
            if cur[i] >= maximums[i]:
                cur[i] = 0
                cur[i + 1] += 1
        if cur[-1] >= maximums[-1]:
            break
        yield tuple(cur)

def test_odometer_iter():
    def t(a, b):
        result = list(odometer_iter(a))
        print result
        assert result == b
    t([], [()])
    t([3], [(0,), (1,), (2,)])
    t([2, 3, 1],
      [(0, 0, 0),
       (1, 0, 0),
       (0, 1, 0),
       (1, 1, 0),
       (0, 2, 0),
       (1, 2, 0)])

class CodeManager(object):
    def __init__(self):
        self._value_to_code = {}
        self._code_to_value = {}
        self._extra_names = {}

    def add_singleton(self, name, value):
        self.add_rule(name, value, value, [])

    def add_rule(self, name, base, maximum, extras):
        assert name is not None
        assert base > 0
        assert maximum <= 65535
        assert name not in self._extra_names
        extra_names = [n for (n, m) in extras]
        self._extra_names[name] = extra_names
        maximums = [m for (n, m) in extras]
        increments = (maximums + [1])[1:]
        for extra_values in odometer_iter(maximums):
            code = base
            for extra_value, increment in zip(extra_values, increments):
                code += extra_value * increment
            assert code <= maximum
            value = (name, tuple(zip(extra_names, extra_values)))
            assert value not in self._value_to_code
            assert code not in self._code_to_value
            self._value_to_code[value] = code
            self._code_to_value[code] = value
        for i in xrange(base, maximum + 1):
            if i not in self._code_to_value:
                # Mark unused codes so that they don't get used by accident:
                self._code_to_value[i] = None

    def code(self, name, extra_values_dict=None, **kwargs):
        if extra_values_dict is None:
            # Create a new empty dict each time, because we may update it
            extra_values_dict = {}
        extra_values_dict.update(kwargs)
        extra_names = self._extra_names[name]
        assert len(extra_names) == len(extra_values_dict)
        extra_values_list = []
        for extra_name in extra_names:
            extra_values_list.append((extra_name,
                                      extra_values_dict[extra_name]))
        value = (name, tuple(extra_values_list))
        return self._value_to_code[value]

    def value(self, code):
        name, extras_tuple = self._code_to_value[code]
        return name, dict(extras_tuple)

def test_CodeManager():
    from nose.tools import assert_raises
    m = CodeManager()
    m.add_singleton("test1", 10)
    assert m.code("test1") == 10
    m.add_singleton("test2", 20)
    assert m.code("test2") == 20
    # Duplicate name:
    assert_raises(AssertionError, m.add_singleton, "test1", 30)
    # Duplicate number:
    assert_raises(AssertionError, m.add_singleton, "test3", 10)
    # Number out of bounds:
    assert_raises(AssertionError, m.add_singleton, "test3", -1)
    assert_raises(AssertionError, m.add_singleton, "test3", 65536)

    m.add_rule("text_fixation", 3000, 3499, [("text", 20)])
    assert m.code("text_fixation", {"text": 0}) == 3000
    assert m.code("text_fixation", {"text": 3}) == 3003
    assert_raises(Exception, m.code, "text_fixation")
    assert_raises(Exception, m.code, "text_fixation", {"text": 1, "foo": 1})
    assert_raises(Exception, m.code, "text_fixation", {"text": -1})
    assert_raises(Exception, m.code, "text_fixation", {"text": 20})

    assert m.value(10) == ("test1", {})
    assert m.value(3015) == ("text_fixation", {"text": 15})

    m.add_rule("text_word", 17000, 48499, [("text", 20), ("word", 1500)])
    assert m.code("text_word", {"text": 0, "word": 0}) == 17000
    assert m.code("text_word", {"text": 1, "word": 0}) == 17000 + 1500
    assert (m.code("text_word", {"text": 12, "word": 10})
            == 17000 + (1500 * 12) + 10)

    m.add_rule("foo", 50000, 50999, [])
    assert m.code("foo") == 50000
    assert_raises(Exception, m.add_singleton, "blah1", 50100)
    assert_raises(Exception, m.add_singleton, "blah2", 50999)
    m.add_singleton("blah3", 51000)
    assert m.code("blah3") == 51000

class MartaCodeManager(CodeManager):
    def __init__(self, *args, **kwargs):
        CodeManager.__init__(self, *args, **kwargs)
        # Codes that could be generated via some mechanism other by appearing
        # in an scn file:
        for name, code in [
            ("cal pulse", 1),
            ("white-button1", 1024), ("white-button2", 1025),
            ("blue-green-button1", 1040), ("blue-green-button2", 2064),
            # The white room dig interprets this as META_RECORD, i.e., like
            # hitting the record key (see the "newdig" source):
            # SHOULD be avoided, but brown1 doesn't, and hopefully that's
            # harmless:
            #("record", 40960),
            ("pause", 49152),
            # ("change-condition", 0x9000)
            # ^^ through 0xffff, actually... maybe I can convince Paul to make
            # it 0x9000 through 0x90ff instead.
            # Used in raw-reading script to mark time points where the code
            # was not actually saved.
            ("clobbered", 65535),
            ]:
            self.add_singleton(name, code)
        self.add_rule("blue-green-right-hand", 2049, 2053,
                       [("finger", 5)])
        assert self.value(2053) == ("blue-green-right-hand", {"finger": 4})
        # blue room left hand button box: ??? (currently broken)
        for i in xrange(1, 13):
            self.add_singleton("stimpres-f%s" % (i,), 16370 + i)
        

if __name__ == "__main__":
    import nose
    nose.runmodule()
