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

    e1, = parsing.parse(parsing.text1)
    e2, = parsing.parse(parsing.text2)

    out = Out()
    e1.pp(out)
    out.newline()
    e2.pp(out)
    out.newline()
