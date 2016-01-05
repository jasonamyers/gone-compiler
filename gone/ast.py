# gone/ast.py
'''
Abstract Syntax Tree (AST) objects.

This file defines classes for different kinds of nodes of an Abstract
Syntax Tree.  During parsing, you will create these nodes and connect
them together.  In general, you will have a different AST node for
each kind of grammar rule.  A few sample AST nodes can be found at the
top of this file.  You will need to add more on your own.
'''

# DO NOT MODIFY
class AST(object):
    '''
    Base class for all of the AST nodes.  Each node is expected to
    define the _fields attribute which lists the names of stored
    attributes.   The __init__() method below takes positional
    arguments and assigns them to the appropriate fields.  Any
    additional arguments specified as keywords are also assigned. 
    '''
    _fields = []
    def __init__(self, *args, **kwargs):
        assert len(args) == len(self._fields)
        for name, value in zip(self._fields, args):
            setattr(self, name, value)
        # Assign additional keyword arguments if supplied
        for name, value in kwargs.items():
            setattr(self, name, value)

# ----------------------------------------------------------------------
# Specific AST nodes.
#
# For each node, you need to define a class and add the appropriate _fields = []
# specification that indicates what fields are to be stored.  Just as
# an example, for a binary operator, you might store the operator, the
# left expression, and the right expression like this:
#
#    class Binop(AST):
#        _fields = ['op','left','right']
# ----------------------------------------------------------------------

# A few sample nodes
class Statements(AST):
    ''' A sequence of statements (e.g. multiple print statements)
    '''
    _fields = ['statements']

class PrintStatement(AST):
    '''
    print expression ;
    '''
    _fields = ['expr']

class Literal(AST):
    '''
    A literal value such as 2, 2.5, or "two"
    '''
    _fields = ['value']

class BinaryOperator(AST):
    ''' expr + expr
    '''
    _fields = ['op', 'left', 'right']

class UnaryOperator(AST):
    ''' (-/+)expr
    '''
    _fields = ['op', 'expr']

class ConstantDeclaration(AST):
    '''
    A constant declaration such as const pi = 3.14159;
    '''
    _fields = ['name', 'expr']

class VariableDeclaration(AST):
    '''
    A variable declaration such as var cookies = 'yummy'
    '''
    _fields = ['name', 'typename', 'expr']

class StoreVariable(AST):
    '''
    Stores a var in an assignment statement
    '''
    _fields = ['name']

class Typename(AST):
    '''
    Defines a possible variable type
    '''
    _fields = ['name']

class LoadVariable(AST):
    '''
    Load a var used in an expression
    '''
    _fields = ['name']   
# You need to add more nodes here.  Suggested nodes include
# BinaryOperator, UnaryOperator, ConstDeclaration, VarDeclaration, 
# AssignmentStatement, etc...

# ----------------------------------------------------------------------
#                  DO NOT MODIFY ANYTHING BELOW HERE
# ----------------------------------------------------------------------

# The following classes for visiting and rewriting the AST are taken
# from Python's ast module.   

# DO NOT MODIFY
class NodeVisitor(object):
    '''
    Class for visiting nodes of the parse tree.  This is modeled after
    a similar class in the standard library ast.NodeVisitor.  For each
    node, the visit(node) method calls a method visit_NodeName(node)
    which should be implemented in subclasses.  The generic_visit() method
    is called for all nodes where there is no matching visit_NodeName() method.

    Here is a example of a visitor that examines binary operators:

        class VisitOps(NodeVisitor):
            visit_Binop(self, node):
                print("Binary operator", node.op)
                self.visit(node.left)
                self.visit(node.right)
            visit_Unaryop(self, node):
                print("Unary operator", node.op)
                self.visit(node.expr)

        tree = parse(txt)
        VisitOps().visit(tree)
    '''
    def visit(self, node):
        '''
        Execute a method of the form visit_NodeName(node) where
        NodeName is the name of the class of a particular node.
        '''
        if node:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            return visitor(node)
        else:
            return None
    
    def generic_visit(self, node):
        '''
        Method executed if no applicable visit_ method can be found.
        This examines the node to see if it has _fields, is a list,
        or can be further traversed.
        '''
        for field in getattr(node, "_fields"):
            value = getattr(node, field, None)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        self.visit(item)
            elif isinstance(value, AST):
                self.visit(value)

# DO NOT MODIFY
def flatten(top):
    '''
    Flatten the entire parse tree into a list for the purposes of
    debugging and testing.  This returns a list of tuples of the
    form (depth, node) where depth is an integer representing the
    parse tree depth and node is the associated AST node.
    '''
    class Flattener(NodeVisitor):
        def __init__(self):
            self.depth = 0
            self.nodes = []
        def generic_visit(self, node):
            self.nodes.append((self.depth, node))
            self.depth += 1
            NodeVisitor.generic_visit(self, node)
            self.depth -= 1

    d = Flattener()
    d.visit(top)
    return d.nodes
