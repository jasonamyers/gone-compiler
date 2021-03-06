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
        self.global_symtab = SymbolTable()
        self.local_symtab = None
        self.current_function = None
        self.has_return = False

        # Add built-in type names (int, float, string) to the symbol table
        self.symtab_add('int', types.int_type)
        self.symtab_add('float', types.float_type)
        self.symtab_add('string', types.string_type)
        self.symtab_add('bool', types.bool_type)

    # Method for adding a symbol to the appropriate symbol table
    def symtab_add(self, name, node):
        if self.local_symtab:
            self.local_symtab.add(name, node)
            node.is_global = False
        else:
            self.global_symtab.add(name, node)
            node.is_global = True

    # Method for looking up a symbol (checks both symbol tables)
    def symtab_lookup(self, name):
        result = None
        if self.local_symtab:
            result = self.local_symtab.get(name)
        if result is None:
            result = self.global_symtab.get(name)
        return result

    def visit_Program(self, node):
        # 1. Visit all of the statements
        self.visit(node.statements)

    def visit_UnaryOperator(self, node):
        self.visit(node.expr)
        # 1. Make sure that the operation is supported by the type
        unary_ops = node.expr.type.unary_ops
        if node.op not in unary_ops.keys():
            error(node.lineno, '%s is not a valid unary operator for type %s' %
                  (node.op, node.expr.type))
        # 2. Set the result type to the same as the operand
        node.type = node.expr.type

    def visit_IfStatement(self, node):
        # print('IfStatement: %r', node)
        self.visit(node.condition)
        if getattr(node.condition, 'type') != types.bool_type:
            error(node.lineno, 'The IF condition must be a boolean')
        self.visit(node.tblock)
        node.type = node.condition.type

    def visit_IfElseStatement(self, node):
        # print('IfElseStatement: %r', node)
        self.visit(node.condition)
        if getattr(node.condition, 'type') != types.bool_type:
            error(node.lineno, 'The IF condition must be a boolean')
        self.visit(node.tblock)
        if_has_return = self.has_return
        self.has_return = False
        self.visit(node.fblock)
        else_has_return = self.has_return
        self.has_return = if_has_return & else_has_return
        node.orelse = True
        node.type = node.condition.type

    def visit_WhileStatement(self, node):
        # print('WhileStatement: %r', node.__dict__)
        self.visit(node.condition)
        if getattr(node.condition, 'type') != types.bool_type:
            error(node.lineno, 'The IF condition must be a boolean')
        self.visit(node.block)
        node.type = node.condition.type

    def visit_BinaryOperator(self, node):
        # print('BinaryOperator %r' % node)
        self.visit(node.left)
        self.visit(node.right)
        # 1. Make sure left and right operands have the same type
        if not node.left.type == node.right.type:
            error(node.lineno, 'You can not %s %s with %s' % (
                node.op, node.left.type, node.right.type))
        # 2. Make sure the operation is supported
        left_bin_ops = set(node.left.type.binary_ops.keys())
        bin_ops = left_bin_ops.intersection(
            set(node.right.type.binary_ops.keys()))
        # print(bin_ops)
        if node.op not in bin_ops:
            error(node.lineno, 'The binary operation %s is not supported '
                  'between %s and %s types' % (node.op, node.left.type,
                                               node.right.type))
        # 3. Assign the result type to the result
        node.type = node.left.type

    def visit_BooleanOperator(self, node):
        self.visit_BinaryOperator(node)
        node.type = types.bool_type

    def visit_AssignmentStatement(self, node):
        # print('%s: AssignmentStatement: %s' % (node.lineno, node.__dict__))
        # 1. Check the location of the assignment
        symbol = self.symtab_lookup(node.store_location.name)
        if not symbol:
            error(node.lineno, '%s was not previously defined' %
                  node.store_location.name)
        else:
            self.visit(node.store_location)
            if isinstance(node.store_location.symbol, ConstantDeclaration):
                error(node.lineno,
                      '%s is a constant and is immutable' %
                      node.store_location.name)
            else:
                self.visit(node.expr)
                # 2. Check that the left and right hand side types match
                if getattr(node.store_location, 'type', None) != getattr(
                        node.expr, 'type', None):
                    error(node.lineno, "Can not store type %s in type %s" %
                          (node.store_location.type.name, getattr(
                              node.expr, 'type.name', None)))
                else:
                    node.store_location.expr = node.expr

    def visit_ConstantDeclaration(self, node):
        # print('%s: ConstantDeclaration: %s' % (node.lineno, node.__dict__))
        # 1. Check that the constant name is not already defined
        symbol = self.symtab_lookup(node.name)
        if symbol:
            error(node.lineno, '%s from %i was already defined at %s' %
                  (node.name, node.lineno, symbol.lineno))
        else:
            self.visit(node.expr)
            node.type = node.expr.type
            # 2. Add an entry to the symbol table
            self.symtab_add(node.name, node)

    def visit_VariableDeclaration(self, node):
        # print('%s: VariableDeclaration: %s' % (node.lineno, node.__dict__))
        # 1. Check that the variable name is not already defined
        symbol = self.symtab_lookup(node.name)
        if symbol:
            error(node.lineno, '%s from %i was already defined at %s' %
                  (node.name, node.lineno, symbol.lineno))
        self.visit(node.typename)
        if getattr(node.typename, 'type'):
            node.type = node.typename.type
            if node.expr:
                self.visit(node.expr)
                if node.expr.type != node.type:
                    error(node.lineno, '%s is of type %s and is being set to '
                          '%s which is of type %s' % (
                              node.name, node.type, node.expr, node.expr.type))
            else:
                node.expr = Literal(node.type.default_value)
                node.expr.type = node.type
            # 2. Add an entry to the symbol table
            # 3. Check that the type of the expression (if any) is the same
            self.symtab_add(node.name, node)
        # print('Post Visit VariableDeclaration %s' % node.__dict__)

    def visit_Typename(self, node):
        # print('Visited Typename: %s' % node.__dict__)
        symbol = self.symtab_lookup(node.name)
        if not symbol or not isinstance(symbol, types.GoneType):
            error(node.lineno, '%s is not a valid type at line %i' % (
                node.name, node.lineno))
        # 1. Make sure the typename is valid and that it's actually a type
        node.type = symbol
        # 2. Attach the type object from gone/types.c
        pass

    def visit_LoadVariable(self, node):
        # print('Visited LoadVariable: %r' % node.__dict__)
        # 1. Make sure the loaded location is valid.
        symbol = self.symtab_lookup(node.name)
        if not symbol:
            error(node.lineno, '%s on line %i is not a valid variable to '
                  'load data' % (node.name, node.lineno))
            node.type = types.error_type
        else:
            if isinstance(symbol, (ConstantDeclaration, VariableDeclaration,
                                   ParameterDeclaration)):
                node.type = symbol.type
            # 1. Make sure the typename is valid and that it's actually a type
        node.symbol = symbol

        # 2. Assign the appropriate type to the result

    def visit_StoreVariable(self, node):
        # 1. Make sure the stored location allows assignment
        # print('Visited StoreVariable: %s' % node.__dict__)
        symbol = self.symtab_lookup(node.name)
        if not symbol:
            error(node.lineno, '%s on line %i is not a valid variable to '
                  'store data' % (node.name, node.lineno))
        elif isinstance(symbol, ConstantDeclaration):
            error(node.lineno, '%s is a constant and is immutable' % node.name)
        elif isinstance(symbol, (VariableDeclaration, ParameterDeclaration)):
            node.type = symbol.type
        # 1. Make sure the typename is valid and that it's actually a type

        node.symbol = symbol

    def visit_Literal(self, node):
        # Attach an appropriate type to the literal
        if isinstance(node.value, bool):
            node.type = types.bool_type
        elif isinstance(node.value, int):
            node.type = types.int_type
        elif isinstance(node.value, float):
            node.type = types.float_type
        elif isinstance(node.value, str):
            node.type = types.string_type
        else:
            error(node.lineno, '%r on line %i is not of a known type' % (
                node.value, node.lineno))
        # print('Visited Literal: %s' % node.value)

    def visit_ExternFunctionDeclaration(self, node):
        self.visit(node.prototype)
        node.type = node.prototype.type
        # print('Visited ExternFunctionDeclaration: %s' % node.__dict__)

    def visit_FunctionPrototype(self, node):
        for param in node.parameters:
            self.visit(param)
        self.visit(node.typename)
        node.type = node.typename.type
        self.symtab_add(node.name, node)
        # print('Visited FunctionPrototype: %s' % node.__dict__)

    def visit_ParameterDeclaration(self, node):
        # 1. Visit the typename and propagate types
        self.visit(node.typename)
        node.type = node.typename.type

    def visit_FunctionCall(self, node):
        # print(node.__dict__)
        symbol = self.symtab_lookup(node.name)
        if not symbol:
            error(node.lineno, '%s on line %i is not a known function' %
                  (node.name, node.lineno))
        else:
            for arg in node.arglist:
                self.visit(arg)
            node.type = symbol.type

        # print('Visited FunctionCall: %s' % node.__dict__)

    # Function call support
    def visit_ReturnStatement(self, node):
        # 1. Check if we're actually inside a function
        if self.current_function is None:
            error(node.lineno, "return used outside of a function")
        else:
            # 2. Visit the expression
            self.visit(node.expr)

            # 3. Make sure the expression type matches the return type
            if node.expr.type != self.current_function.prototype.type:
                error(node.lineno, "Type error in return.  %s != %s" % (
                    node.expr.type.name,
                    getattr(self.current_function.prototype.type, 'name', None)
                )
                )
            self.has_return = True

    # Function declaration
    def visit_FunctionDeclaration(self, node):
        # 1. Check to make sure not nested function
        if self.current_function:
            error(node.lineno, "Nested functions not supported.")
        else:
            # 2. Visit prototype to check for duplication/typenames
            self.visit(node.prototype)
            node.type = node.prototype.type

            # 3. Set up a new local scope
            self.local_symtab = SymbolTable()
            self.current_function = node
            self.has_return = False

            # 4. Processing function parameters and add symbols to symbol table
            for parm in node.prototype.parameters:
                self.symtab_add(parm.name, parm)

            # 5. Visit the statements
            self.visit(node.statements)

            # 6. Pop the local scope
            self.local_symtab = None
            self.current_function = None

            # 7. Check for return
            if not self.has_return:
                error(node.lineno, 'Control might reach the end of function '
                      '%s without a return.' % node.prototype.name)
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
