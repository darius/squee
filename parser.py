import sys
sys.setrecursionlimit(3000)

from peglet import Parser, join

parser_grammar = r"""
program = sequence !.
sequence = big newlines opt_sequence
opt_sequence = sequence | 
newlines = ; | 

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

method_decl = multidecl | unidecl
unidecl = id
multidecl = id id opt_multidecl
opt_multidecl = multidecl | 

small   = tiny opt_message               mk_opt_call

opt_message = message
            |                            mk_nomessage
message = multimessage                   mk_multimessage
        | unimessage

multimessage = id tiny opt_multimessage
opt_multimessage = multimessage | 

unimessage = id                          mk_unimessage

tiny    = number                     int mk_lit
        | string                         mk_lit
        | id                             mk_var
        | \( _ big \) _

id       = ([A-Za-z][_A-Za-z0-9-]*) _
number   = (-?\d+)                  _  
string   = ('(?:''|[^'])*')         _  
_ = \s*
"""

def mk_opt_call(e, message): return message(e)
def mk_nomessage(): return lambda e: e
def mk_unimessage(selector): return lambda e: ('call', e, (selector,), ())
def mk_multimessage(*args): return lambda e: ('call', e, tuple(args[0::2]), tuple(args[1::2]))
def mk_lit(c): return ('lit', c)
def mk_var(name): return ('var', name)

## parse_scanned('adjoining of (k plus 5) to empty')
#. (('call', ('var', 'adjoining'), ('of', 'to'), (('call', ('var', 'k'), ('plus',), (('lit', 5),)), ('var', 'empty'))),)

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
punct    = (::=|::|:|[`()\[\],;])        tag_punct
operator = ([~!@%&*\-+=|\\<>?\/]+)       tag_operator
string   = ('(?:''|[^'])*')              tag_string
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

scan = Parser(lexer, **globals())
parse_scanned = Parser(parser_grammar, int=int, **globals())

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
    depth = 0
    indent = '   '
    newline = True
    for token in tokens:
        if token[0] == '\n' or newline:
            yield '\n' + (';' if token[0] == '\n' else '') + indent * depth
            newline = False
        if token[0] == '\n':
            continue
        yield token[1] or token[0]
        if token[0] == '}':
            depth -= 1
            newline = True
        elif token[0] == '{':
            depth += 1
            newline = True
        else:
            pass

text = r"""
hey
   once
      twice
back again
"""
## for x in dentify(scan(text)): print x
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
## print ' '.join(show(dentify(scan(text1))))
#. 
#. ; make-sokoboard { 
#.     grid 
#. ;    width 
#. ;    I :: { 
#.        find-player { 
#.           grid find 'i' default : grid find 'I' } 
#.        move thing from here to there { 
#.           thing has ( grid at here ) && ( : ' .' has ( grid at there ) ) , { 
#.              if-so : { 
#.                 I clear here 
#. ;                I drop thing at there } 
#.              } 
#.           } 
#.        clear pos { 
#.           grid at pos put ( I target pos , if-so ( : '.' ) if-not ( : ' ' ) ) } 
#.        target pos { 
#.           '.@I' has ( grid at pos ) } 
#.        drop thing at pos { 
#. ;          grid at pos put { 
#.              thing at ( '.' = grid at pos , if-so ( : 1 ) if-not ( : 0 ) ) } 
#.           } 
#.        } 
#.     :: { 
#.        render { 
#.           grid freeze } 
#.        push dir { 
#.           p ::= I find-player 
#. ;          I move 'o@' from ( p + dir ) to ( p + dir + dir ) 
#. ;          I move 'iI' from p to ( p + dir ) } 
#.        } 
#.     }


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

## examples = open('examples.loo').read()
## print ' '.join(show(dentify(scan(examples))))
#. 
#. ; 
#. ; empty :: { 
#.     is-empty : yes 
#. ;    has k : no 
#. ;    adjoin k : adjoining of k to empty 
#. ;    merge s : s } 
#.  adjoining of n to s :: { 
#.     s has n , { 
#.        if-so : s 
#. ;       if-not : { 
#.           extension :: { 
#.              is-empty : no 
#. ;             has k : n == k 
#. ;             adjoin k : adjoining of k to extension 
#. ;             merge s : merging of extension with s } 
#.           } 
#.        } 
#.     } 
#.  merging of s1 with s2 :: { 
#.     meld :: { 
#.        is-empty : s1 is-empty && : s2 is-empty 
#. ;       has k : s1 has k || : s2 has k 
#. ;       adjoin k : adjoining of k to meld 
#. ;       merge s : merging of meld with s } 
#.     } 
#. ; 
#. ; finding in xs where ok :: { 
#.     escaping as ` return : { 
#.        xs enumerate ` i ` x : { 
#.           ok of x , if-so : return of i } 
#.        } 
#.     -1 } 
#.  r ::= 2 
#. ; i ::= finding in [ 1 ; 2 ; 3 ] where ` x : x > r 
#. ;
