import sys
sys.setrecursionlimit(3000)

from peglet import Parser, join

# This exposes a shortcoming of peglet: it's meant only for strings.
# Also, recursion depth, argh.

g = r"""
program = sequence !.
sequence = big newlines opt_sequence
opt_sequence = sequence | 
newlines = XXX

big     = make
        | id ::= big
        | small

make    = id method_decl :: body
        | id :: methods
        | :: methods
actor   = { methods }
methods = method methods | 
method  = method_decl body
body    = { sequence }

small   = tiny message | tiny

message = operator small
        | id tiny opt_message
        | id

tiny    = number
        | string
        | id
        | \( big \)

"""

lexer = r"""
program  = tokens !.
tokens   = token tokens | 
token    = spaces | comment | dent
         | number | symbol | punct | operator | string

spaces   = space spaces | space
space    = !\n \s

comment  = --[^\n]*

dent     = (\n\s*)                       tag_dent
number   = (-?\d+)                       tag_number
symbol   = ([A-Za-z][_A-Za-z0-9-]*)      tag_symbol
punct    = (::=|::|:|[(),])              tag_punct
operator = ([~!@%&*\-+=|\\<>?\/]+)       tag_operator

string   = ' qchars '               join tag_string
qchars   = qchar qchars |
qchar    = '(') | ([^'])
"""

def tag_dent(text):
    spaces = text.strip('\n')
    assert all(c == ' ' for c in spaces)
    return ('dent', len(spaces))

def tag_punct(text): return (text, '')

def tagger(tag): return lambda text: (tag, text)

tag_number   = tagger('number')
tag_symbol   = tagger('symbol')
tag_operator = tagger('operator')
tag_string   = tagger('string')

parse = Parser(lexer, **globals())

def dentify(tokens):
    margins = [0]
    tokens = iter(tokens)
    for token in tokens:
        if token[0] == 'dent' and token[1] < margins[-1]:
            while True:
                yield '}', ''
                margins.pop()
                if token[1] == margins[-1]:
                    break
                elif margins[-1] < token[1]:
                    raise "Mismatching indent"
            continue
        elif token[0] == 'dent':
            if token[1] == margins[-1]:
                yield '\n', ''
            else:
                assert token[1] > margins[-1]
                yield '{', ''
                margins.append(token[1])
        else:
            yield token

def show(tokens):
    def write(x):
        sys.stdout.write(str(x))
        wtf.append((depth, token, x))
    depth = 0
    wtf = []
    indent = '   '
    newline = True
    for token in tokens:
        if token[0] == '\n' or newline:
            write('\n' + indent * depth)
            newline = False
        if token[0] == '\n':
            continue
        write(' ' + (token[1] or token[0]))
        if token[0] == '}':
            depth -= 1
            newline = True
        elif token[0] == '{':
            depth += 1
            newline = True
        else:
            pass
    print '\n'
    #return wtf

text = r"""
hey
   once
      twice
back again
"""
## for x in dentify(parse(text)): print x
#. ('\n', '')
#. ('symbol', 'hey')
#. ('{', '')
#. ('symbol', 'once')
#. ('{', '')
#. ('symbol', 'twice')
#. ('}', '')
#. ('}', '')
#. ('symbol', 'back')
#. ('symbol', 'again')
#. ('\n', '')
## for x in show(dentify(parse(text1))): print x
#. 
#.  make-sokoboard {
#.     grid
#.     width
#.     I :: {
#.        find-player {
#.           grid find i default : grid find I }
#.        move thing from here to there {
#.           thing has ( grid at here ) && ( :  . has ( grid at there ) ) , {
#.              if-so : {
#.                 I clear here
#.                 I drop thing at there }
#.              }
#.           }
#.        clear pos {
#.           grid at pos put ( I target pos , if-so ( : . ) if-not ( :   ) ) }
#.        target pos {
#.           .@I has ( grid at pos ) }
#.        drop thing at pos {
#.           grid at pos put {
#.              thing at ( . = grid at pos , if-so ( : 1 ) if-not ( : 0 ) ) }
#.           }
#.        }
#.     :: {
#.        render {
#.           grid freeze }
#.        push dir {
#.           p ::= I find-player
#.           I move o@ from ( p + dir ) to ( p + dir + dir )
#.           I move iI from p to ( p + dir ) }
#.        }
#.     }
#. 
#. TypeError: 'NoneType' object is not iterable


text1 = r"""
make-sokoboard
   grid
   width
   I ::
      find-player
         grid find 'i' default: grid find 'I'
      move thing from here to there
         thing has (grid at here) && (: ' .' has (grid at there)),
            if-so:
               I clear here
               I drop thing at there
      clear pos
         grid at pos put (I target pos, if-so (:'.') if-not (:' '))
      target pos
         '.@I' has (grid at pos)
      drop thing at pos
         -- Pre: I'm clear at pos
         grid at pos put 
            thing at ('.' = grid at pos, if-so (:1) if-not (:0))
   ::
      render
         grid freeze
      push dir
         p ::= I find-player
         I move 'o@' from (p+dir) to (p+dir+dir)
         I move 'iI' from p to (p+dir)
"""

"""
   wtf
   I ::
      find-player
         grid find 'i' default: grid find 'I'
      move thing from here to there
         thing has (grid at here) && (: ' .' has (grid at there)),
            if-so: I clear here
                   I drop thing at there
      clear pos
         grid at pos put (I target pos, if-so (:'.') if-not (:' '))
      target pos
         '.@I' has (grid at pos)
      drop thing at pos
         -- Pre: I'm clear at pos
         grid at pos put 
            thing at ('.' = grid at pos, if-so (:1) if-not (:0))
   ::
      render
         grid freeze
      push dir
         p ::= I find-player
         I move 'o@' from (p+dir) to (p+dir+dir)
         I move 'iI' from p to (p+dir)
"""
