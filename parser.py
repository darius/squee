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
    margins = [-1]
    tokens = iter(tokens)
    for token in tokens:
        while token[0] == 'dent' and token[1] < margins[-1]:
            yield '}', ''
            margins.pop()
            token = next(tokens)
        if token[0] == 'dent':
            if token[1] == margins[-1]:
                yield '\n', ''
            else:
                assert token[1] > margins[-1]
                yield '{', ''
                margins.append(token[1])
        else:
            yield token

def show(tokens):
    depth = 0
    for token in tokens:
        print token[1] or token[0],
        if token[0] == '\n':
            print ('  ' * depth),
        elif token[0] == '{':
            print '\n' + ('  ' * depth),
            depth += 1
        elif token[0] == '}':
            depth -= 1
            print '\n' + ('  ' * depth),
        else:
            pass

text = r"""
-- Thoughts:

-- We don't really need the ':' at the end of method declarations,
-- since we'll be viewing them in a dedicated editor that could 
-- color-code them -- no worries about too little redundancy.
-- That leaves two plausible uses for the ':': for blocks and for
-- avoiding some parentheses. Let's try blocks here.
-- (But we would still need : in one-line method defs...)

-- If we made *all* binding instances of variables start with `
-- then it'd be natural to extend this with patterns somehow, in
-- the places you can bind variables -- it'd be easy to distinguish
-- the variables from the pattern pieces. Look into Barry Jay's
-- stuff again?

make-sokoboard of initial-grid ::
   grid ::= initial-grid thaw  -- Make a mutable copy. (What's a better name?)
   width ::= grid find '\n' + 1
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

## show(dentify(parse(text)))
#. { 
#. 
#.    
#.    
#.    
#.    
#.    
#.    
#.    
#.    
#.    
#.    
#.    
#.    make-sokoboard of initial-grid :: { 
#.    grid ::= initial-grid thaw 
#.      width ::= grid find \n + 1 
#.      I :: { 
#.      find-player { 
#.        grid find i default : grid find I } 
#.        move thing from here to there { 
#.        thing has ( grid at here ) && ( :  . has ( grid at there ) ) , { 
#.          if-so : I clear here { 
#.            I drop thing at there } 
#.            clear pos } 
#.          grid at pos put ( I target pos , if-so ( : . ) if-not ( :   ) ) } 
#.        target pos { 
#.        .@I has ( grid at pos ) } 
#.        drop thing at pos { 
#.        
#.          grid at pos put { 
#.          thing at ( . = grid at pos , if-so ( : 1 ) if-not ( : 0 ) ) } 
#.          :: } 
#.        render { 
#.        grid freeze } 
#.        push dir { 
#.        p ::= I find-player 
#.          I move o@ from ( p + dir ) to ( p + dir + dir ) 
#.          I move iI from p to ( p + dir ) } 
#.       
