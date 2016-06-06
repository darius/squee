"""
A version of the parser setting aside the indent-sensitive part, for now.
"""

from parson import Grammar, alter
from absyntax import Constant, Fetch, Actor, Call, Then, Define, Nest, Method, Parenthesize

parser_grammar = r"""
program        : _ sequence :end                 :mk_body.

sequence       : big (';'_ sequence)?.

big            : make
               | id '::='_ big                   :Define
               | body
               | binsend
               | small.

make           : id [method_decl '::'_ body      :Method :hug :Actor]
                                                 :Define
               | id '::'_ actor                  :Define
               |    '::'_ actor.
actor          : '{'_ method (';'_ method)* '}'_ :hug :Actor.
method         : method_decl ':'_ body           :Method.
body           : '{'_ sequence '}'_              :mk_body.

method_decl    : ( opid id
                 | (id id)+
                 | id)                           :unzip.

binsend        : small ([opid small :unzip]      :Call)*.

small          : tiny
                 ( [((id tiny)+ | id) :unzip]    :Call)?.

tiny           : number                          :Constant
               | string                          :Constant
               | id                              :Fetch
               | block
               | '('_ big ')'_                   :Parenthesize.

block          : ('`' id)* :hug ':'_ body        :mk_block_method :hug :Actor.

id             : /([A-Za-z][_A-Za-z0-9-]*)/   _.
opid           : /([~!@%&*\-+=|\\<>,?\\\/]+)/ _.
number         : /(-?\d+)/                    _  :int.
string         : /'((?:''|[^'])*)'/           _.  

_              = whitespace*.
whitespace     = /\s+|-- .*/.
"""
# XXX string literals with '' need unescaping

def mk_block_method(params, body):
    cue = ('of',) + ('and',)*(len(params)-1) if params else ('run',)
    return Method(cue, params, body)

def mk_body(*exprs): return Nest(reduce(Then, exprs))

unzip = alter(lambda *parts: (parts[0::2], parts[1::2]))

parse = Grammar(parser_grammar)(**globals()).program


# Smoke test

## parse('adjoining of (k + 5) to empty')[0]
#. {adjoining of (k + 5) to empty}
## parse(': { 1 }')[0]
#. {:: {run: {1}}}

text1 = """
empty :: 
{   is-empty: { yes }
;   has k:    { no }
;   adjoin k: { adjoining of k to empty }
;   merge s:  { s }
}
"""

## parse(text1)[0]
#. {empty :: {is-empty: {yes}; has k: {no}; adjoin k: {adjoining of k to empty}; merge s: {s}}}

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

## parse(text2)[0]
#. {empty-stack :: {is-empty: {yes}; top: {complain of 'Underflow'}; pop: {complain of 'Underflow'}; size: {0}}; push :: {of element on stack: {:: {is-empty: {no}; top: {element}; pop: {stack}; size: {1 + stack size}}}}}

## parse("foo of 42 + bar of 137")[0]
#. {foo of 42 + bar of 137}

## parse('a ::= 2; a + 3')[0]
#. {a ::= 2; a + 3}

## sets = open('sets.squee').read()
## parse(sets)[0]
#. {empty :: {is-empty: {yes}; has k: {no}; adjoin k: {adjoining of k to empty}; merge s: {s}}; adjoining :: {of n to s: {(s has n) if-so :: {run: {s}} if-not :: {run: {extension :: {is-empty: {no}; has k: {n = k || :: {run: {s has k}}}; adjoin k: {adjoining of k to extension}; merge t: {merging of extension with t}}}}}}; merging :: {of s1 with s2: {meld :: {is-empty: {s1 is-empty && :: {run: {s2 is-empty}}}; has k: {s1 has k || :: {run: {s2 has k}}}; adjoin k: {adjoining of k to meld}; merge s: {merging of meld with s}}}}; make-list of (empty has 42) and ((empty adjoin 42) has 42)}
