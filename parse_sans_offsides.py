"""
A version of the parser setting aside the indent-sensitive part, for now.
"""

from parson import Grammar
from absyntax import Constant, Fetch, Actor, Call, Then, Define, Nest, Method

parser_grammar = r"""
program        : _ sequence ~/./                 :mk_body.

sequence       : big (';'_ sequence)?.

big            : make
               | id '::='_ big                   :Define
               | binsend.

make           : id method_decl '::'_ body       :bind_simple_actor
               | id '::'_ actor                  :Define
               |    '::'_ actor.
actor          : '{'_ method (';'_ method)* '}'_ :mk_actor.
method         : method_decl ':'_ body           :mk_method.
body           : '{'_ sequence '}'_              :mk_body.

method_decl    : ( id id (id id)*
                 | opid id
                 | id)                           :mk_method_decl.

binsend        : small opt_binmessage            :mk_opt_call.
opt_binmessage : opid binsend                    :mk_binmessage
               |                                 :mk_nomessage.

small          : tiny opt_message                :mk_opt_call.
opt_message    : (id tiny)+                      :mk_multimessage
               | id                              :mk_unimessage
               |                                 :mk_nomessage.

tiny           : number                          :Constant
               | string                          :Constant
               | id                              :Fetch
               | block
               | '('_ big ')'_.

block          : ('`' id)* :hug ':'_ body        :mk_block_method :mk_actor.

id             : /([A-Za-z][_A-Za-z0-9-]*)/   _.
opid           : /([~!@%&*\-+=|\\<>,?\\\/]+)/ _.
number         : /(-?\d+)/                    _  :int.
string         : /'((?:''|[^'])*)'/           _.  

_              : /\s*/.
"""
# XXX string literals with '' need unescaping

def mk_block_method(params, body):
    cue = ('of',) + ('and',)*(len(params)-1) if params else ('run',)
    return Method(cue, params, body)

def mk_actor(*methods):      return Actor(methods)

def bind_simple_actor(name, (cue, params), expr):
    return Define(name, Actor((Method(cue, params, expr),)))
def mk_method((cue, params), expr):
    return Method(cue, params, expr)

def mk_body(*exprs):         return Nest(reduce(Then, exprs))
def mk_method_decl(*parts):  return (parts[0::2], parts[1::2])

def mk_opt_call(e, message): return message(e)
def mk_nomessage():          return lambda e: e
def mk_unimessage(cue):      return lambda e: Call(e, (cue,), ())
def mk_binmessage(opid, arg):return lambda e: Call(e, (opid,), (arg,))
def mk_multimessage(*args):  return lambda e: Call(e, args[0::2], args[1::2])

parse = Grammar(parser_grammar)(**globals()).program


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
#. ({empty-stack ::= {('is-empty',): {yes}; ('pop',): {(complain of 'Underflow')}; ('size',): {0}; ('top',): {(complain of 'Underflow')}}; push ::= {('of', 'on') ('element', 'stack'): {{('is-empty',): {no}; ('pop',): {stack}; ('size',): {(1 + (stack size))}; ('top',): {element}}}}},)

## parse("foo of 42 + bar of 137")
#. ({((foo of 42) + (bar of 137))},)

## parse('a ::= 2; a + 3')
#. ({a ::= 2; (a + 3)},)

## sets = open('sets.squee').read()
## parse(sets)
#. ({empty ::= {('adjoin',) ('k',): {(adjoining of k to empty)}; ('has',) ('k',): {no}; ('is-empty',): {yes}; ('merge',) ('s',): {s}}; adjoining ::= {('of', 'to') ('n', 's'): {((s has n) if-so {('run',): {s}} if-not {('run',): {extension ::= {('adjoin',) ('k',): {(adjoining of k to extension)}; ('has',) ('k',): {(n == (k || {('run',): {(s has k)}}))}; ('is-empty',): {no}; ('merge',) ('t',): {(merging of extension with t)}}}})}}; merging ::= {('of', 'with') ('s1', 's2'): {meld ::= {('adjoin',) ('k',): {(adjoining of k to meld)}; ('has',) ('k',): {((s1 has k) || {('run',): {(s2 has k)}})}; ('is-empty',): {((s1 is-empty) && {('run',): {(s2 is-empty)}})}; ('merge',) ('s',): {(merging of meld with s)}}}}},)
