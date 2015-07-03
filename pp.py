"""
Pretty-printing Squee source code.
"""

import sys

class Out(object):
    def __init__(self):
        self.col = 0
        self.margin = 0
    def indent(self, delta):
        self.margin += delta
    def newline(self):
        sys.stdout.write('\n')
        sys.stdout.write(' ' * self.margin)
        self.col = self.margin
    def pr(self, s):
        for c in s:
            assert 32 <= ord(c) < 127
        sys.stdout.write(s)
        self.col += len(s)

if __name__ == '__main__':
    import parse_sans_offsides as parsing

    if len(sys.argv) == 1:
        e1, = parsing.parse(parsing.text1)
        text = parsing.text2
    elif len(sys.argv) == 2:
        text = open(sys.argv[1]).read()
    else:
        assert False

    e, = parsing.parse(text)
    out = Out()
    e.pp(out)
    out.newline()
