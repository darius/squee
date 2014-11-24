"""
The kernel: stepping and sending.
"""

def trampoline(state):
    k, value = state
    while k is not None:
#        traceback((k, value))
        fn, free_var, k = k
        k, value = fn(value, free_var, k)
    return value

final_k = None

def traceback(state):
    k, value = state
    print ':', value
    while k:
        fn, free_var, k = k
        if isinstance(free_var, tuple) and free_var:
            for i, element in enumerate(free_var):
                print '%-18s %r' % (('' if i else fn.__name__), element)
        else:
            print '%-18s %r' % (fn.__name__, free_var)

def call(receiver, selector, arguments, k):
    try:                   methods = receiver.vtable
    except AttributeError: methods = primitive_vtables[type(receiver)]
    method = methods.get(selector)
    if method is None:
        method = miranda_methods[selector] # TODO: handle method-missing
    return method(receiver, arguments, k)

primitive_vtables = {}
miranda_methods = {}

def vtable_union(vtable1, vtable2):
    result = dict(vtable1)
    result.update(vtable2)
    return result
