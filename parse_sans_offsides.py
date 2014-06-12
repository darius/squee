"""
A version of the parser setting aside the indent-sensitive part, for now.
"""

from peglet import Parser, hug, join
from absyntax import Constant, Fetch, Actor, Call, Then, Define, Seclude, Method

parser_grammar = r"""
program        = _ sequence !.             mk_body

sequence       = big opt_sequence
opt_sequence   = ; _ sequence | 

big            = make
               | id ::= _ big              Define
               | binsend

make           = id method_decl :: _ body  bind_simple_actor
               | id :: _ actor             Define
               | :: _ actor
actor          = { _ method methods } _    mk_actor
methods        = ; _ method methods | 
method         = method_decl : _ body      mk_method
body           = { _ sequence } _          mk_body

method_decl    = whateverdecl              mk_method_decl
whateverdecl   = multidecl
               | opid id
               | id
multidecl      = id id multidecl
               | id id

binsend        = small opt_binmessage      mk_opt_call
opt_binmessage = opid binsend              mk_binmessage
               |                           mk_nomessage

small          = tiny opt_message          mk_opt_call
opt_message    = multimessage              mk_multimessage
               | id                        mk_unimessage
               |                           mk_nomessage
multimessage   = id tiny opt_multimessage
opt_multimessage = multimessage
                 | 

tiny           = number                int Constant
               | string                    Constant
               | id                        Fetch
               | block
               | \( _ big \) _

block          = params hug : _ body       mk_block_method mk_actor
params         = ` id params
               | 

id             = ([A-Za-z][_A-Za-z0-9-]*) _
opid           = ([~!@%&*\-+=|\\<>,?\/]+) _
number         = (-?\d+)                  _  
string         = ('(?:''|[^'])*')         _  

_              = \s*
"""

def mk_block_method(params, body):
    cue = ('of',) + ('and',)*(len(params)-1) if params else ('run',)
    return Method(cue, params, body)

def mk_actor(*methods):      return Actor(methods)

def bind_simple_actor(name, (cue, params), expr):
    return Define(name, Actor((Method(cue, params, expr),)))
def mk_method((cue, params), expr):
    return Method(cue, params, expr)

def mk_body(*exprs):         return Seclude(reduce(Then, exprs))
def mk_method_decl(*parts):  return (parts[0::2], parts[1::2])

def mk_opt_call(e, message): return message(e)
def mk_nomessage():          return lambda e: e
def mk_unimessage(cue):      return lambda e: Call(e, (cue,), ())
def mk_binmessage(opid, arg):return lambda e: Call(e, (opid,), (arg,))
def mk_multimessage(*args):  return lambda e: Call(e, args[0::2], args[1::2])

parse = Parser(parser_grammar, int=int, **globals())


# Smoke test

## parse('adjoining of (k + 5) to empty')
#. ({(adjoining of (k + 5) to empty)},)
## parse(': { 1 }')
#. ({{('run',): {1}}},)

text1 = """
empty :: 
{   is-empty: { yes }
;   has k:    { no }
;   adjoin k: { adjoining of k to empty }
;   merge s:  { s }
}
"""

## parse(text1)
#. ({empty ::= {('adjoin',) ('k',): {(adjoining of k to empty)}; ('has',) ('k',): {no}; ('is-empty',): {yes}; ('merge',) ('s',): {s}}},)

text2 = """
empty-stack ::
{   is-empty: { yes }
;   top:      { complain of 'Underflow' }
;   pop:      { complain of 'Underflow' }
;   size:     { 0 }
};

push of element on stack ::
{  ::
   {   is-empty: { no }
   ;   top:      { element }
   ;   pop:      { stack }
   ;   size:     { 1 + stack size }
}  }
"""

## parse(text2)
#. ({empty-stack ::= {('is-empty',): {yes}; ('pop',): {(complain of "'Underflow'")}; ('size',): {0}; ('top',): {(complain of "'Underflow'")}}; push ::= {('of', 'on') ('element', 'stack'): {{('is-empty',): {no}; ('pop',): {stack}; ('size',): {(1 + (stack size))}; ('top',): {element}}}}},)

## parse("foo of 42 + bar of 137")
#. ({((foo of 42) + (bar of 137))},)

## parse('a ::= 2; a + 3')
#. ({a ::= 2; (a + 3)},)
