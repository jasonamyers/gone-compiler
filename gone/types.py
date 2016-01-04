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
    def __init__(self, name):
        '''
        You must implement yourself and figure out what else to store
        or define on subclasses.
        '''
        self.name = name

# Create specific instances of types. You will need to add
# appropriate extra arguments depending on your definition of GoneType

int_type = GoneType('int')
float_type = GoneType('float')
string_type = GoneType('string')

# In your type checking code, you will probably need to reference the
# above type objects.   Think of how you how want to provide access to them.
# Maybe create a dictionary or set that holds the defined types.




          




