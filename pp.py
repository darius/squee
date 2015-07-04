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
        if 1:
            sys.stdout.write('<br>')
#            sys.stdout.write('&nbsp;' * self.margin)
        else:
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
    sys.stdout.write("""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Blah</title>
    <style type="text/css">
      div.nest, div.actor {
        display: inline-block;
        vertical-align: top;
#        border-style: solid;
#        border-width: 1px;
      }
      .d0 { background-color: #f0ffff; }
      .d1 { background-color: #f0f8f8; }
      .d2 { background-color: #f0f0f0; }
      .d3 { background-color: #e0f0f0; }
      .d4 { background-color: #e0e0f0; }
      .d5 { background-color: #e0e0e0; }
      .d6 { background-color: #e0d8d8; }
      .d7 { background-color: #e0d0d0; }
      .d8 { background-color: #d0d0d0; }
      .d9 { background-color: #c0d0d0; }
      .d10 { background-color: #f0ffff; }
    </style>  </head>
  <body>""")
    e.pp(out)
    out.newline()
    sys.stdout.write("""</body>
</html>""")
