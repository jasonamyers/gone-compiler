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
    """
    Class representing a symbol table.  It should provide functionality
    for adding and looking up objects associated with identifiers. You
    could also add error checking for undefined or duplicate identifiers
    here.

    This class should not be complicated--think Python dictionaries.
    """

    def __init__(self):
        self.symbols = {}

    def add(self, name, node):
        if name in self.symbols:
            error(node.lineno, '%s was previously defined on %s' % (
                name, getattr(self.symbols[name], 'lineno', 'I forgot where')))
        else:
            self.symbols[name] = node

    def get(self, name):
        if name not in self.symbols:
            return None
        else:
            return self.symbols[name]

    def get_all(self):
        return [self.symbols[key] for key in self.symbols.keys()]


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
        self.symbols = SymbolTable()

        # Add built-in type names (int, float, string) to the symbol table
        self.symbols.add('int', types.int_type)
        self.symbols.add('float', types.float_type)
        self.symbols.add('string', types.string_type)

    def visit_Program(self, node):
        # 1. Visit all of the statements
        pass

    def visit_UnaryOperator(self, node):
        print('UnaryOperator %r' % node)
        self.visit(node.expr)
        # 1. Make sure that the operation is supported by the type
        print('UnaryOperator %s' % node.op.__class__.__name__)
        # 2. Set the result type to the same as the operand

    def visit_BinaryOperator(self, node):
        print('BinaryOperator %r' % node)
        self.visit(node.left)
        self.visit(node.right)
        node.type = node.left.type
        if not node.left.type == node.right.type:
            error(node.lineno, 'You can not %s a %s with a %s' % (
                node.op, node.left.type, node.right.type))
        # 1. Make sure left and right operands have the same type
        # 2. Make sure the operation is supported
        # 3. Assign the result type to the result

    def visit_AssignmentStatement(self, node):
        print('%s: AssignmentStatement: %s' % (node.lineno, node.__dict__))
        self.visit(node.store_location)
        self.visit(node.expr)
        # 1. Check the location of the assignment
        # 2. Check that the left and right hand side types match
        if node.store_location.type != node.expr.type:
            error(node.lineno, "Type error %s = %s" %
                  (node.store_location.type.name, node.expr.type.name))
        node.store_location.expr = node.expr
        print([symbol.__dict__
               for symbol in self.symbols.get_all()])

    def visit_ConstantDeclaration(self, node):
        print('%s: ConstantDeclaration: %s' % (node.lineno, node.__dict__))
        symbol = self.symbols.get(node.name)
        if symbol:
            error(node.lineno, '%s from %i was already defined at %s' %
                  (node.name, node.lineno, symbol.lineno))
        else:
            self.visit(node.expr)
            node.type = node.expr.type
            self.symbols.add(node.name, node)
        # 1. Check that the constant name is not already defined
        # 2. Add an entry to the symbol table

    def visit_VariableDeclaration(self, node):
        print('%s: VariableDeclaration: %s' % (node.lineno, node.__dict__))
        symbol = self.symbols.get(node.name)
        if symbol:
            error(node.lineno, '%s from %i was already defined at %s' %
                  (node.name, node.lineno, symbol.lineno))
        self.visit(node.typename)
        node.type = node.typename.type
        if node.expr:
            self.visit(node.expr)
            if node.expr.type != node.type:
                error(node.lineno, '%s is of type %s and is being set to %s '
                      'which is of type %s' % (node.name, node.type, node.expr,
                                               node.expr.type))
        else:
            node.expr = Literal(node.type.default_value)
            node.expr.type = node.type
            node.type = node.typename.type
            # 1. Check that the variable name is not already defined
            # 2. Add an entry to the symbol table
            # 3. Check that the type of the expression (if any) is the same
        self.symbols.add(node.name, node)
        print('Post Visit VariableDeclaration %s' % node.__dict__)

    def visit_Typename(self, node):
        print('Visited Typename: %s' % node.__dict__)
        symbol = self.symbols.get(node.name)
        if not symbol or not isinstance(symbol, types.GoneType):
            error(node.lineno, '%s is not a valid type at line %i' % (
                node.name, node.lineno(1)))
        # 1. Make sure the typename is valid and that it's actually a type
        node.type = symbol
        # 2. Attach the type object from gone/types.c
        pass

    def visit_LoadVariable(self, node):
        print('Visited LoadVariable: %r' % node.__dict__)
        # 1. Make sure the loaded location is valid.
        symbol = self.symbols.get(node.name)
        if not symbol:
            error(node.lineno, '%s on line %i is not a valid variable to '
                  'load data' % (node.name, node.lineno))
        else:
            if isinstance(symbol, (ConstantDeclaration, VariableDeclaration,
                                   ParameterDeclaration)):
                node.type = symbol.type
            # 1. Make sure the typename is valid and that it's actually a type
        node.symbol = symbol

        # 2. Assign the appropriate type to the result

    def visit_StoreVariable(self, node):
        # 1. Make sure the stored location allows assignment
        print('Visited StoreVariable: %s' % node.__dict__)
        symbol = self.symbols.get(node.name)
        if not symbol:
            error(node.lineno, '%s on line %i is not a valid variable to '
                  'store data' % (node.name, node.lineno(1)))
        elif isinstance(symbol, ConstantDeclaration):
            error(node.lineno, '%s is a constant and is immutable' % node.name)
        elif isinstance(symbol, (VariableDeclaration, ParameterDeclaration)):
            node.type = symbol.type
        # 1. Make sure the typename is valid and that it's actually a type

        node.symbol = symbol
        pass

    def visit_Literal(self, node):
        # Attach an appropriate type to the literal
        if isinstance(node.value, int):
            node.type = types.int_type
        elif isinstance(node.value, float):
            node.type = types.float_type
        elif isinstance(node.value, str):
            node.type = types.string_type
        else:
            error(node.lineno, '%r on line %i is not of a known type' % (
                node.value, node.lineno))

        print('%s: Literal: %r, %s' % (node.lineno, node.value, node.type))
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
