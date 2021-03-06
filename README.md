## Lambda, the Original Object: a sketch

Abstract syntax, with expressions e, variables v, constants c:

    e        = Literal c               'hello'
             | Variable v              answer
             | Call e selector [e]     array at i put x
             | Actor [method] e        :: double n; 2 * n
             | Define v e              answer ::= 42
             | Nest e                  foo; bar
             | Then e1 e2              foo; bar
    method   = Method selector [v] e
    selector = [string] -- XXX arity 0/1 both imply selector has length 1...

A Then evaluates its subexpressions in order and returns the last
value.

A Define expression evaluates to what its subexpression evaluates to.
The scope of the variable is the whole Nest it's defined in;
if it's referenced before it's bound, an error is raised. (I think
I want to change this to a promise semantics instead, but promises
aren't implemented yet.)

(Nest was called 'block' in Algol-60; it's renamed here to avoid
confusion with Smalltalk blocks.)

In Actor the last e should evaluate to a block with selector and
argument-list parameters; it's called on selector-not-found.
(Actually maybe it'd be simpler to make it a method instead of a block.)
For now let's just not support this feature either way.

Actors have Miranda methods defined elsewhere, for things like 
repr and hash. There's also a default selector-not-found handler.

If you want mutability, use one of the primitive mutable data
structures. We don't have mutable variables. (Maybe we should, if only
for convenience in coding in a workspace.)


Term-tree abstract syntax:

    term = Number n                           42
         | String s                           'hello'
         | Symbol v                           hello
         | Compound term selector [term]      array at i put x

For the sake of Lispiness, we want the language's concrete syntax to
have a simple and transparent mapping to term-trees, which have a
concrete syntax that looks the same -- i.e. term trees play the role
of s-expressions. Call maps directly to Compound. Certain selectors
are reserved in this mapping to denote the other special
forms. (That's kind of ugly in a 'defaulty' way, but Lisp shares that
quality.)

Another possible way to map special forms/macros: with a special
symbol for the leading term of the Compound. Not sure which way to go
at the moment. Maybe the whole idea sucks.
