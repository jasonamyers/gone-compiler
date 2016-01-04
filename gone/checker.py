# gone/checker.py
'''
Project 3 : Static Program Analysis
===================================
In this project you need to perform semantic checks on your program.
There are a few different aspects of doing this.

Do not start this project until you have fully completed Exercise 3.

First, you will need to define a symbol table that keeps track of
previously declared identifiers.  The symbol table will be consulted
whenever the compiler needs to lookup information about variable and
constant declarations.

Next, you will need to define objects that represent the different
builtin datatypes and record information about their capabilities.
See the file gone/types.py.

Finally, you'll need to write code that walks the AST and enforces
a set of semantic rules.  Here is a complete list of everything you'll
need to check:

1.  Names and symbols:

    All identifiers must be defined before they are used.  This
    includes variables, constants, and typenames.  For example, this
    kind of code generates an error:

       a = 3;              // Error. 'a' not defined.
       var a int;

    Note: typenames such as "int", "float", and "string" are built-in
    names that should be defined at the start of the program.

2.  Types of literals

    All literal symbols must be assigned a type of "int", "float", or "string".  
    For example:

       const a = 42;         // Type "int"
       const b = 4.2;        // Type "float"
       const c = "forty";    // Type "string"

    To do this assignment, check the Python type of the literal value
    and attach a type name as appropriate.

3.  Binary operator type checking

    Binary operators only operate on operands of the same type and produce a
    result of the same type.   Otherwise, you get a type error.  For example:

        var a int = 2;
        var b float = 3.14;

        var c int = a + 3;    // OK
        var d int = a + b;    // Error.  int + float
        var e int = b + 4.5;  // Error.  int = float

4.  Unary operator type checking.

    Unary operators return a result that's the same type as the operand.

5.  Supported operators

    Here are the operators supported by each type:

    int:      binary { +, -, *, /}, unary { +, -}
    float:    binary { +, -, *, /}, unary { +, -}
    string:   binary { + }, unary { }

    Attempts to use unsupported operators should result in an error. 
    For example:

        var string a = "Hello" + "World";     // OK
        var string b = "Hello" * "World";     // Error (unsupported op *)

6.  Assignment.

    The left and right hand sides of an assignment operation must be
    declared as the same type.

    Values can only be assigned to variable declarations, not
    to constants.

For walking the AST, use the NodeVisitor class defined in gone/ast.py.
A shell of the code is provided below.
'''

from .errors import error
from .ast import *
from . import types

class SymbolTable(object):
    '''
    Class representing a symbol table.  It should provide functionality
    for adding and looking up objects associated with identifiers. You
    could also add error checking for undefined or duplicate identifiers
    here.

    This class should not be complicated--think Python dictionaries.
    '''
    pass

class CheckProgramVisitor(NodeVisitor):
    '''
    Program checking class.   This class uses the visitor pattern as described
    in gone/ast.py.   You need to define methods of the form visit_NodeName()
    for each kind of AST node that you want to process.

    Note: You will need to adjust the names of the AST nodes if you
    used different names in your parser.  You may need to add additional
    methods as needed.
    '''
    def __init__(self):
        # Initialize the symbol table
        pass

        # Add built-in type names (int, float, string) to the symbol table
        pass

    def visit_Program(self, node):
        # 1. Visit all of the statements
        pass

    def visit_Unaryop(self, node):
        # 1. Make sure that the operation is supported by the type
        # 2. Set the result type to the same as the operand
        pass

    def visit_Binop(self, node):
        # 1. Make sure left and right operands have the same type
        # 2. Make sure the operation is supported
        # 3. Assign the result type to the result
        pass

    def visit_AssignmentStatement(self, node):
        # 1. Check the location of the assignment
        # 2. Check that the left and right hand side types match
        pass

    def visit_ConstDeclaration(self, node):
        # 1. Check that the constant name is not already defined
        # 2. Add an entry to the symbol table
        pass

    def visit_VarDeclaration(self, node):
        # 1. Check that the variable name is not already defined
        # 2. Add an entry to the symbol table
        # 3. Check that the type of the expression (if any) is the same
        # 4. If there is no expression, set an initial value for the value
        pass

    def visit_Typename(self, node):
        # 1. Make sure the typename is valid and that it's actually a type
        # 2. Attach the type object from gone/types.c 
        pass

    def visit_LoadLocation(self, node):
        # 1. Make sure the loaded location is valid.
        # 2. Assign the appropriate type to the result
        pass

    def visit_StoreLocation(self, node):
        # 1. Make sure the stored location allows assignment
        pass

    def visit_Literal(self, node):
        # Attach an appropriate type to the literal
        pass

# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW       
# ----------------------------------------------------------------------

def check_program(ast):
    '''
    Check the supplied program (in the form of an AST)
    '''
    checker = CheckProgramVisitor()
    checker.visit(ast)

def main():
    '''
    Main program. Used for testing
    '''
    import sys
    from .parser import parse

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m gone.checker filename\n")
        raise SystemExit(1)

    ast = parse(open(sys.argv[1]).read())
    check_program(ast)

if __name__ == '__main__':
    main()
            



