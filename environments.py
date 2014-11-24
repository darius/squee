"""
Environments map name -> value. A global env can be mutated; an
ordinary env shadows a containing env, and can have undefined
bindings, resolved once.
"""

from collections import namedtuple
from core import vtable_union

env_vtable = {
    ('at',):       lambda self, (key,), k:  (k, self.get(key)),
}

class GlobalEnv(namedtuple('_GlobalEnv', 'rib')):
    def adjoin(self, key, value):
        assert value is not undefined
        self.rib[key] = value
    def get(self, key):
        return self.rib[key]
    def __repr__(self):
        return 'GlobalEnv'
    vtable = vtable_union(env_vtable, {
        ('at', 'adjoin'): lambda self, (key, value), k: (k, self.adjoin(key, value)),
    })

undefined = object()

def extend(container, variables, values):
    return Env(dict(zip(variables, values)), container)

class Env(namedtuple('_Env', 'rib container')):
    def define(self, key, value):
        assert self.rib.get(key) is undefined
        assert value is not undefined
        self.rib[key] = value
    def get(self, key):
        if key in self.rib:
            value = self.rib[key]
            assert value is not undefined
            return value
        else:
            return self.container.get(key)
    def __repr__(self):
        return 'Env(%r) / %r' % (self.rib, self.container)
    vtable = vtable_union(env_vtable, {
        ('at', 'define'): lambda self, (key, value), k: (k, self.define(key, value)),
    })
