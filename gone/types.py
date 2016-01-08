# gone/types.py
'''
Project 3: Type System
======================
This file implements the Gone type system.  There is a lot of
flexibility with the implementation, but start by defining a
class representing a type.

class GoneType(object):
    def __init__(self, typename):
        self.name = typename
        ...

Concrete types are then created as instances.  For example:

    int_type = GoneType('int',...)
    float_type = GoneType('float',...)
    string_type = GoneType('string', ...)

The contents of the type class is entirely up to you. However,
it must minimally provide information about the following:

   a.  What operations are supported (+, -, *, etc.).
   b.  The result type of each operator.
   c.  Default values for newly created instances of each type
   d.  Methods for type-checking of binary and unary operators
   e.  Maintain a registry mapping builtin type names (e.g. 'int', 'float')
       to type instances (e.g., int_type, float_type, string_type, etc.).

Don't forget that all of the built-in types might need to be registered
with symbol tables and other code that checks for type names. This
might require some coding in 'checker.py'.

Interesting Aside:  A class that represents instances of types or
other classes (e.g., the GoneType class), is sometimes known as
a "metaclass."
'''


class GoneType(object):
    '''
    Class that represents a type in the Gone language.  Types
    are declared as instances of this type.
    '''

    built_ins = {}

    def __init__(self, name, default_value, binary_ops, unary_ops):
        '''
        You must implement yourself and figure out what else to store
        or define on subclasses.
        '''
        self.name = name
        self.default_value = default_value
        self.binary_ops = binary_ops
        self.unary_ops = unary_ops
        GoneType.built_ins[name] = self

    def __str__(self):
        return '%s' % self.name

    def lookup(cls, name):
        if name in cls.built_ins:
            return cls.built_ins[name]
        else:
            raise ValueError('%s is not a built in type' % name)

    # Create specific instances of types. You will need to add
    # appropriate extra arguments depending on your definition of GoneType

int_type = GoneType(
    'int',
    default_value=0,
    binary_ops={
        '+': 'int',
        '-': 'int',
        '*': 'int',
        '/': 'int',
        '<': 'bool',
        '>': 'bool',
        '<=': 'bool',
        '>=': 'bool',
        '==': 'bool',
        '!=': 'bool',
    },
    unary_ops={
        '+': 'int',
        '-': 'int',
    }
)

float_type = GoneType(
    'float',
    default_value=0.0,
    binary_ops={
        '+': 'float',
        '-': 'float',
        '*': 'float',
        '/': 'float',
        '<': 'bool',
        '>': 'bool',
        '<=': 'bool',
        '>=': 'bool',
        '==': 'bool',
        '!=': 'bool',
    },
    unary_ops={
        '+': 'float',
        '-': 'float'
    }
)

bool_type = GoneType(
    'bool',
    default_value=0,
    binary_ops={
        '==': 'bool',
        '!=': 'bool',
        '&&': 'bool',
        '||': 'bool',
    },
    unary_ops={
        '!': 'bool'
    }
)

string_type = GoneType(
    'string',
    default_value='',
    binary_ops={
        '+': 'string'
    },
    unary_ops={}
)

error_type = GoneType(
    'error',
    default_value=None,
    binary_ops={
        '+': '<error>',
        '-': '<error>',
        '*': '<error>',
        '/': '<error>',
        '<': 'bool',
        '>': 'bool',
        '<=': 'bool',
        '>=': 'bool',
        '==': 'bool',
        '!=': 'bool',
        '&&': 'bool',
        '||': 'bool',
    },
    unary_ops={
        '+': '<error>',
        '-': '<error>',
        '!': '<error>'
    }
)

# In your type checking code, you will probably need to reference the
# above type objects.   Think of how you how want to provide access to them.
# Maybe create a dictionary or set that holds the defined types.
