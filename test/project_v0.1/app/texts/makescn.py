FONT = "vera.ttf"
FONT_SIZE = 21
LEADING_IN_PIXELS = 55
MAX_WIDTH_IN_CHARS = 35
META_COLOR = 6  # color to use for non-text items
FIXATION_DOT_COLOR = 2 # color to use for omnipresent fixation dot
FIXATION_DOT_SIZE = 5
FIXATION_PLUS_COLOR = META_COLOR # color to use for big auditory + fixation
FIXATION_PLUS_SIZE = 40
FIXATION_PLUS_WIDTH = 3
RESOLUTION = (1024, 768)

import textwrap

from codes import MartaCodeManager

cm = MartaCodeManager()

cm.add_rule("experiment", 500, 999, [("number", 500)])
cm.add_rule("subject", 1500, 1999, [("subject", 500)])
MAX_SOA = 2000
cm.add_rule("soa", 54000, 55999, [("soa", MAX_SOA)])
MAX_TEXTS = 20
MAX_QUESTIONS = 20
cm.add_rule("text-start", 3000, 3499, [("text", MAX_TEXTS)])
cm.add_rule("text-end", 3500, 3999, [("text", MAX_TEXTS)])
cm.add_rule("question", 4000, 5999, [("text", MAX_TEXTS),
                                        ("question", MAX_QUESTIONS)])
cm.add_rule("correct", 6000, 7999, [("text", MAX_TEXTS),
                                       ("question", MAX_QUESTIONS)])
cm.add_rule("incorrect", 8000, 9999, [("text", MAX_TEXTS),
                                         ("question", MAX_QUESTIONS)])
cm.add_rule("text-title", 10000, 10019, [("text", MAX_TEXTS)])

MAX_SENTENCES = 150
cm.add_rule("audio-sentence-start", 10030, 13029,
            [("text", MAX_TEXTS), ("sentence", MAX_SENTENCES)])
cm.add_rule("audio-sentence-end", 13030, 16029,
            [("text", MAX_TEXTS), ("sentence", MAX_SENTENCES)])

cm.add_rule("text-word", 17000, 48499, [("text", MAX_TEXTS),
                                           ("word", 1500)])
cm.add_rule("rating-screen", 48500, 48699,
               [("text", MAX_TEXTS), ("screen", 10)])
cm.add_rule("rating", 48700, 48899,
               [("text", MAX_TEXTS), ("screen", 10)])
cm.add_rule("sem-anomaly", 50000, 51999,
               [("text", MAX_TEXTS), ("anomaly", 100)])
cm.add_rule("syn-anomaly", 52000, 53999,
               [("text", MAX_TEXTS), ("anomaly", 100)])
cm.add_rule("pause-before-sentence", 56000, 58999,
            [("text", MAX_TEXTS), ("sentence", 150)])

for (name, code) in {"magic": 64969,
                     "text-instructions": 64000,
                     "p300-instructions": 64002,
                     "p300-fixation": 64010,
                     "p300-x": 64011,
                     "p300-o": 64012,
                     "p300-z": 64013,
                     "text-frame-offset": 64014,
                     "audio-100": 64015,
                     "audio-200": 64016,
                     "audio-300": 64017,
                     "p300-low": 64018,
                     "p300-high": 64019,
                     "p300-weird": 64020,
                     "audio-0": 64021,
                     }.items():
    cm.add_singleton(name, code)


def layout_text_centered(multiline_str, leading):
    lines = multiline_str.split("\n")
    height = LEADING_IN_PIXELS * len(lines)
    offset_lines = []
    offset = -1 * (len(lines) - 1) / 2.0 * leading
    for line in lines:
        offset_lines.append((int(round(offset)), line))
        offset += leading
    return offset_lines

def test_layout_text_centered():
    def tltc(a, b):
        layout = layout_text_centered(a, 10)
        print layout, b
        assert layout == b
    tltc("foo", [(0, "foo")])
    tltc("foo\nbar", [(-5, "foo"), (5, "bar")])
    tltc("foo\nbar\nbaz", [(-10, "foo"), (0, "bar"), (10, "baz")])

def wrap(text):
    return "\n".join(textwrap.wrap(text, MAX_WIDTH_IN_CHARS))

class SCNWriter(object):
    def __init__(self, path, expid, subjid):
        self._file = open(path, "w")
        # Magic label handling:
        self._codes = []
        self._i = 0
        self._closed = False
        self._preamble(expid, subjid)

    def _preamble(self, expid, subjid):
        self.w("GLOBAL font=%s\n" % FONT)
        self.w("GLOBAL fontsize=36\n")
        self.section("Experiment metadata:")
        self.w("100 100 %s text=\"\" mon=MAGIC\n" % cm.code("magic"))
        self.w("100 100 %s text=\"\" mon=EXP\n" % cm.code("experiment",
                                                             number=expid))
        self.w("100 100 %s text=\"\" mon=SUBJ\n" % cm.code("subject",
                                                              subject=subjid))
    def w(self, text):
        self._file.write(text)

    def section(self, text):
        self.w("################################################\n")
        lines = text.split("\n")
        for line in lines:
            self.w("# %s\n" % line)
        self.w("################################################\n")

    def fixation(self, dur, code=0):
         self.w("%s %s %s text=\"+\" color=%s\n"
                 % (dur, dur, code, META_COLOR))
    #    self.w("%s %s %s pgi=fix.pgi\n" % (dur, dur, code))

    def quote(self, s):
        return s.replace("\"", "\\\"").replace("\n", "\\n")

    def wav(self, soa, dur, code, path, label=None, extra=None,
            persistent_pgi=None):
        self.w("%s %s %s wav=\"%s\""
               % (soa, dur, code, path))
        if label is not None:
            self.w(" label=\"%s\"" % label)
        if extra is not None:
            self.w(" %s" % extra)
        if persistent_pgi is not None:
            self.w(" +\n pgi=\"%s\"" % persistent_pgi)
        self.w("\n")

    def asd(self, soa, dur, code, path, label=None, extra=None,
            persistent_pgi=None):
        self.w("%s %s %s audio=\"%s\""
               % (soa, dur, code, path))
        if label is not None:
            self.w(" label=\"%s\"" % label)
        if extra is not None:
            self.w(" %s" % extra)
        if persistent_pgi is not None:
            self.w(" +\n pgi=\"%s\"" % persistent_pgi)
        self.w("\n")

    def text_frame(self, soa, dur, code, text, color=None, label=None,
                   extra=None, persistent_pgi=None):
        self.w("%s %s %s text=\"%s\""
                % (dur, dur, code, self.quote(text)))
        if color is not None:
            self.w(" color=%s" % color)
        if label is not None:
            self.w(" label=\"%s\"" % label)
        if extra is not None:
            self.w(" %s" % extra)
        if persistent_pgi is not None:
            self.w(" +\n pgi=\"%s\"" % persistent_pgi)
        self.w("\n")
        if soa > dur:
            self.text_frame(soa - dur, soa - dur,
                            cm.code("text-frame-offset"), "",
                            persistent_pgi=persistent_pgi)

    def write_layout_lines(self, layout, color=None):
        for offset, text in layout:
            self.w("text=\"%s\" yoff=%s" % (text.replace('"', '\\"'), offset))
            if color is not None:
                self.w(" color=%s" % META_COLOR)
            self.w(" +\n")
        self.w("text=\"\"\n")

    def multiline_text_frame(self, soa, dur, code, text,
                             color=None, label=None, extra=None):
        self.w("%s %s %s text=\"\"" % (soa, dur, code))
        if label is not None:
            self.w(" label=\"%s\"" % label)
        if extra is not None:
            self.w(" %s" % extra)
        self.w(" +\n")
        layout = layout_text_centered(text, LEADING_IN_PIXELS)
        self.write_layout_lines(layout, color=color)

    def br(self, codes, label, come_back=False):
        if isinstance(codes, int):
            codes = [codes]
        bits = []
        if come_back:
            come_back_txt = "1"
        else:
            come_back_txt = ""
        for code in codes:
            bits.append(" br=\"%s %s %s\" " % (code, label, come_back_txt))
        return "".join(bits)

    def emit_on(self, on, code):
        # Uniquify our labels, to avoid the bug that gets triggered if we
        # jump to the same frame more than once:
        label = "code%sc%s" % (self._i, code)
        self._i += 1
        self._codes.append((label, code))
        return self.br(on, label, True)

    def close(self):
        if self._closed:
            return
        self.section("The end:")
        self.text_frame(100, 100, 0, "", extra="end")
        self.section("Automagic frames to emit particular codes on demand:")
        for label, code in self._codes:
            self.text_frame(100, 100, code, "", label=label)
        self._file.close()
        self._closed = True

    def __del__(self):
        self.close()

def _rating_screen_text(levels, level):
    q = "On a scale of 1-7, how well do you feel like you followed this text?"
    tmpl = """%s
    
 (not well)    [%s]    (very well)
%s

        Use right button to adjust ->
<- left button when finished        """
    scale = ["-"] * levels
    if level == 0:
        level_str = ""
    else:
        scale[level - 1] = "|"
        level_str = str(level)
    return tmpl % (wrap(q), "".join(scale), level_str)

# This supports unrolling because currently, if you branch back to a screen
# that has been previously displayed, stimpres will crash and require a hard
# reboot.
def rating_screen(scn, textno, adjust_code, accept_code, levels=7,
                  unroll=1):
    def label(name):
        return "rating_%s_%s" % (textno, name)
    scn.section("Rating screen for text %s" % textno)
    # First put in a screen with no numbers on it:
    scn.w(("100 100 %s text=\"\" color=%s mon=\"Pre-rating screen\" "
           + "%s wfron +\n")
          % (cm.code("rating-screen", text=textno, screen=0),
             META_COLOR, scn.br(adjust_code, label("screen_0"))))
    screen_text = _rating_screen_text(levels, 0)
    layout = layout_text_centered(screen_text, LEADING_IN_PIXELS)
    scn.write_layout_lines(layout, color=META_COLOR)
    screens = levels * unroll
    for screen in range(screens):
        level = (screen % levels) + 1
        next_screen = screen + 1
        if next_screen == screens:
            if unroll == 1:
                # Not unrolling -- loop instead:
                next_screen = 0
            else:
                next_screen = "overflow"
        next_label = label("screen_%s" % next_screen)
        scn.w(("100 100 %s text=\"\" color=%s mon=\"Rating screen %s (%s/%s)\" "
               + "label=\"%s\" %s %s wfron +\n")
              % (cm.code("rating-screen", text=textno, screen=level),
                 META_COLOR,
                 level, screen // levels + 1, unroll,
                 label("screen_%s" % screen),
                 scn.br(adjust_code, next_label),
                 scn.br(accept_code, label("emit_%s" % level))))
        screen_text = _rating_screen_text(levels, level)
        layout = layout_text_centered(screen_text, LEADING_IN_PIXELS)
        scn.write_layout_lines(layout, color=META_COLOR)
    scn.multiline_text_frame(100, 100,
                             cm.code("rating", text=textno, screen=0),
                             wrap("Oops!  You managed to hit a bug in this program -- but there's no problem, just ask the experimenter what to do next."),
                             color=META_COLOR,
                             label=label("screen_overflow"),
                             extra="wfron")
    for level in range(1, levels + 1):
        # We would like to unconditionally branch from here to exit... but
        # stimpres doesn't have unconditional branches, argh.
        scn.w("50 0 %s text=\"\" label=%s\n"
              % (cm.code("rating", text=textno, screen=level),
                 label("emit_%s" % level)))
    scn.text_frame(50, 0, 0, "", label=label("exit"))

def fixation_dot_pgi(pgi_out):
    pgi_out.write("# FIXATION POINT (autogenerated file, do not edit)\n")
    pgi_out.write("setfgcolor %s\n" % FIXATION_DOT_COLOR)
    adj = (FIXATION_DOT_SIZE // 2) + 1
    x = (RESOLUTION[0] // 2) - adj
    y = (RESOLUTION[1] // 2) + (LEADING_IN_PIXELS // 1.5) - adj
    pgi_out.write("moveto %s %s\n" % (x, y))
    pgi_out.write("frect %s %s\n" % (FIXATION_DOT_SIZE, FIXATION_DOT_SIZE))

def fixation_plus_pgi(pgi_out):
    pgi_out.write("# FIXATION POINT (autogenerated file, do not edit)\n")
    pgi_out.write("setfgcolor %s\n" % FIXATION_PLUS_COLOR)
    x = RESOLUTION[0] // 2
    y = RESOLUTION[1] // 2
    pgi_out.write("moveto %s %s\n" % (x - FIXATION_PLUS_WIDTH // 2 + 1,
                                      y - FIXATION_PLUS_SIZE // 2 + 1))
    pgi_out.write("frect %s %s\n" % (FIXATION_PLUS_WIDTH,
                                     FIXATION_PLUS_SIZE))
    pgi_out.write("moveto %s %s\n" % (x - FIXATION_PLUS_SIZE // 2 + 1,
                                      y - FIXATION_PLUS_WIDTH // 2 + 1))
    pgi_out.write("frect %s %s\n" % (FIXATION_PLUS_SIZE,
                                     FIXATION_PLUS_WIDTH))

def test_scn(path, fixation_dot_file, fixation_plus_file):
    scn = SCNWriter(path, 0, 0)
    scn.text_frame(100, 100, 0, "META_COLOR", color=META_COLOR, extra="wfron")
    if fixation_dot_file is not None:
        scn.text_frame(100, 100, 0, "Normal color with dot", extra="wfron",
                       persistent_pgi=fixation_dot_file)
        scn.text_frame(100, 100, 0, "I", extra="wfron",
                       persistent_pgi=fixation_dot_file)
    if fixation_plus_file is not None:
        scn.text_frame(100, 100, 0, "", extra="wfron",
                       persistent_pgi=fixation_plus_file)
    scn.multiline_text_frame(100, 100, 0, wrap("""
Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Duis lacinia mi at
felis. Maecenas congue rhoncus tellus. Nullam ac nisi. Maecenas
mi. Suspendisse congue. Donec placerat metus ac augue. Nullam id dolor at
lorem mattis commodo."""), extra="wfron")
    rating_screen(scn, 0, 1024, 1025, levels=7, unroll=2)
    scn.close()

def cals_scn(path, count):
    scn = SCNWriter(path, 0, 0)
    for i in xrange(count):
        scn.w("500 200 %s text=\"cal\"\n" % (cm.code("cal pulse"),))
    scn.close()

if __name__ == "__main__":
    import nose
    nose.runmodule()
