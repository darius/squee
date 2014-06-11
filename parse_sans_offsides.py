"""
A version of the parser setting aside the indent-sensitive part, for now.
"""

from peglet import Parser, join
from absyntax import Constant, Fetch, Actor, Call, Then, Define, Seclude, Method
## from top import global_env, trampoline, final_k

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

tiny           = number                int mk_lit
               | string                    mk_lit
               | id                        mk_var
               | \( _ big \) _

id             = ([A-Za-z][_A-Za-z0-9-]*) _
opid           = ([~!@%&*\-+=|\\<>,?\/]+) _
number         = (-?\d+)                  _  
string         = ('(?:''|[^'])*')         _  

_              = \s*
"""

def mk_body(*exprs):         return Seclude(reduce(Then, exprs))
def mk_method((selector, params), expr): return Method(selector, params, expr)
def mk_method_decl(*parts):  return (parts[0::2], parts[1::2])
def mk_actor(*methods):      return Actor(methods) #  XXX right?
def bind_simple_actor(name, (selector, params), expr): return Define(name, Actor((Method(selector, params, expr),)))

def mk_opt_call(e, message): return message(e)
def mk_nomessage():          return lambda e: e
def mk_unimessage(selector): return lambda e: Call(e, (selector,), ())
def mk_binmessage(opid, arg):return lambda e: Call(e, (opid,), (arg,))
def mk_multimessage(*args):  return lambda e: Call(e, args[0::2], args[1::2])
def mk_lit(c):    return Constant(c)
def mk_var(name): return Fetch(name)

## parse('adjoining of (k + 5) to empty')
#. ({(adjoining of (k + 5) to empty)},)

parse = Parser(parser_grammar, int=int, **globals())

text1 = """
empty :: 
{   is-empty: { yes }
;   has k:    { no }
;   adjoin k: { adjoining of k to empty }
;   merge s:  { s }
}
"""

## print parse(text1)
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

## print parse(text2)
#. ({empty-stack ::= {('is-empty',): {yes}; ('pop',): {(complain of "'Underflow'")}; ('size',): {0}; ('top',): {(complain of "'Underflow'")}}; push ::= {('of', 'on') ('element', 'stack'): {{('is-empty',): {no}; ('pop',): {stack}; ('size',): {(1 + (stack size))}; ('top',): {element}}}}},)

## print parse("foo of 42 + bar of 137")
#. ({((foo of 42) + (bar of 137))},)

## trampoline(parse('2 + 3')[0].eval(global_env, final_k))
#. 5

## parse('a ::= 2; a + 3')
#. ({a ::= 2; (a + 3)},)
## trampoline(parse('a ::= 2; a + 3')[0].eval(global_env, final_k))
#. 5

text3 = """
empty :: {
   size: { 0 } };
push of element on stack :: {
   :: { size: { 1 + stack size } } };
(push of 'a' on (push of 'b' on empty)) size
"""
## trampoline(parse(text3)[0].eval(global_env, final_k))
#. 2
