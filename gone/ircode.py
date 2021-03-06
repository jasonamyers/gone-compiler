# gone/ircode.py
'''
Project 4
=========
Code generation for the Gone language.  In this project, you are going
to turn the AST into an intermediate machine code known as Single
Static Assignment (SSA).  There are a few important parts you'll need
to make this work.  Please read carefully before beginning:

Single Static Assignment
========================
The first problem is how to decompose complex expressions into
something that can be handled more simply.  One way to do this is
to decompose all expressions into a sequence of simple assignments
involving binary or unary operations.

As an example, suppose you had a mathematical expression like this:

        2 + 3*4 - 5

Here is one possible way to decompose the expression into simple
operations:

        int_1 = 2
        int_2 = 3
        int_3 = 4
        int_4 = int_2 * int_3
        int_5 = int_1 + int_4
        int_6 = 5
        int_7 = int_5 - int_6

In this code, the int_n variables are simply temporaries used while
carrying out the calculation.  A critical feature of SSA is that such
temporary variables are only assigned once (single assignment) and
never reused.  Thus, if you were to evaluate another expression, you
would simply keep incrementing the numbers. For example, if you were
to evaluate 10+20+30, you would have code like this:

        int_8 = 10
        int_9 = 20
        int_10 = int_8 + int_9
        int_11 = 30
        int_12 = int_11 + int_11

SSA is meant to mimic the low-level instructions one might carry out
on a CPU.  For example, the above instructions might be translated to
low-level machine instructions (for a hypothetical CPU) like this:

        MOVI   #2, R1
        MOVI   #3, R2
        MOVI   #4, R3
        MUL    R2, R3, R4
        ADD    R4, R1, R5
        MOVI   #5, R6
        SUB    R5, R6, R7

Another benefit of SSA is that it is very easy to encode and
manipulate using simple data structures such as tuples. For example,
you could encode the above sequence of operations as a list like this:

       [
         ('movi', 2, 'int_1'),
         ('movi', 3, 'int_2'),
         ('movi', 4, 'int_3'),
         ('mul', 'int_2', 'int_3', 'int_4'),
         ('add', 'int_1', 'int_4', 'int_5'),
         ('movi', 5, 'int_6'),
         ('sub', 'int_5','int_6','int_7'),
       ]

Dealing with Variables
======================
In your program, you are probably going to have some variables that get
used and assigned different values.  For example:

       a = 10 + 20;
       b = 2 * a;
       a = a + 1;

In "pure SSA", all of your variables would actually be versioned just
like temporaries in the expressions above.  For example, you would
emit code like this:

       int_1 = 10
       int_2 = 20
       a_1 = int_1 + int_2
       int_3 = 2
       b_1 = int_3 * a_1
       int_4 = 1
       a_2 = a_1 + int_4
       ...

For reasons that will make sense later, we're going to treat declared
variables as memory locations and access them using load/store
instructions.  For example:

       int_1 = 10
       int_2 = 20
       int_3 = int_1 + int_2
       store(int_3, "a")
       int_4 = 2
       int_5 = load("a")
       int_6 = int_4 * int_5
       store(int_6,"b")
       int_7 = load("a")
       int_8 = 1
       int_9 = int_7 + int_8
       store(int_9, "a")

With the load/store model, it's not necessary to version the
variables and code generation will be easier.

A Word About Types
==================
At a low-level, CPUs can only operate a few different kinds of
data such as ints and floats.  Because the semantics of the
low-level types might vary slightly, you'll need to take
some steps to handle them separately.

In our intermediate code, we're simply going to tag temporary variable
names and instructions with an associated type low-level type.  For
example:

      2 + 3*4          (ints)
      2.0 + 3.0*4.0    (floats)

The generated intermediate code might look like this:

      ('literal_int', 2, 'int_1')
      ('literal_int', 3, 'int_2')
      ('literal_int', 4, 'int_3')
      ('mul_int', 'int_2', 'int_3', 'int_4')
      ('add_int', 'int_1', 'int_4', 'int_5')

      ('literal_float', 2.0, 'float_1')
      ('literal_float', 3.0, 'float_2')
      ('literal_float', 4.0, 'float_3')
      ('mul_float', 'float_2', 'float_3', 'float_4')
      ('add_float', 'float_1', 'float_4', 'float_5')

Note: These types may or may not correspond directly to the type names
used in the input program.   For example, during translation, higher
level data structures would be reduced to a low-level operations.

Your Task
=========
Your task is as follows: Write a AST Visitor() class that takes an
Gone program and flattens it to a single sequence of SSA code instructions
represented as tuples of the form

       (operation, operands, ..., destination)

To start, your SSA code should only contain the following operators:

       ('alloc_type',varname)             # Allocate a variable of a given type
       ('literal_type', value, target)    # Load a literal value into target
       # Load the value of a variable into target
       ('load_type', varname, target)
       # Store the value of source into varname
       ('store_type',source, varname)
       ('add_type', left, right, target ) # target = left + right
       ('sub_type',left,right,target)     # target = left - right
       ('mul_type',left,right,target)     # target = left * right
       # target = left / right  (integer truncation)
       ('div_type',left,right,target)
       ('uadd_type',source,target)        # target = +source
       ('uneg_type',source,target)        # target = -source
       ('print_type',source)              # Print value of source

In this code the word "type" is replaced by an appropriate low-level type
such as "int" or "float".

A Word About Correctness
========================
In writing your code, you can assume that the input program is fully
correct--that is, you don't need to be performing any correctness
checks here.   That was the whole point of Project 3 involving static
program analysis.  If the program was checked without any errors, then
it is assumed to be correct for the purposes of generated code.
'''

from . import ast
from collections import defaultdict
from .bblock import *


class Function(object):
    '''
    Class to represent function objects.
    '''

    def __init__(self, name, return_type, parameters, start_block):
        self.name = name
        self.return_type = return_type
        self.parameters = parameters
        self.start_block = start_block


# Map various operator symbol names such as +, -, *, /
# to actual opcode names 'add','sub','mul','div' to be emitted in
# the SSA code.   This is easy to do using dictionaries:

binary_ops = {
    '+': 'add',
    '-': 'sub',
    '*': 'mul',
    '/': 'div',
    '<': 'lt',
    '<=': 'le',
    '>': 'gt',
    '>=': 'ge',
    '==': 'eq',
    '!=': 'ne',
    '&&': 'and',
    '||': 'or'
}

unary_ops = {
    '+': 'uadd',
    '-': 'usub',
    '!': 'not'
}

# Implement the following Node Visitor class so that it creates
# a sequence of SSA instructions in the form of tuples.  Use the
# above description of the allowed op-codes as a guide.


class GenerateCode(ast.NodeVisitor):
    '''
    Node visitor class that creates 3-address encoded instruction sequences.
    '''

    def __init__(self):
        super(GenerateCode, self).__init__()

        # version dictionary for temporaries
        self.versions = defaultdict(int)

        # The generated code (list of tuples)
        self.code = BasicBlock()
        self.start_block = self.code

        # A list of external declarations (and types)
        self.externs = []
        self.functions = []
        self.functions.append(Function('__init', 'void', [], self.start_block))

    def new_temp(self, typeobj):
        '''
        Create a new temporary variable of a given type.
        '''
        name = "__%s_%d" % (typeobj.name, self.versions[typeobj.name])
        self.versions[typeobj.name] += 1
        return name

    # You must implement visit_Nodename methods for all of the other
    # AST nodes.  In your code, you will need to make instructions
    # and append them to the self.code list.
    #
    # A few sample methods follow.  You may have to adjust depending
    # on the names of the AST nodes you've defined.

    def visit_Literal(self, node):
        # Create a new temporary variable name
        target = self.new_temp(node.type)

        # Make the SSA opcode and append to list of generated instructions
        inst = ('literal_' + node.type.name, node.value, target)
        self.code.append(inst)

        # Save the name of the temporary variable where the value was placed
        node.gen_location = target

    def visit_BinaryOperator(self, node):
        # print('visit_BinaryOperator %s' % node)
        # Visit the left and right expressions
        self.visit(node.left)
        self.visit(node.right)

        # Make a new temporary for storing the result
        target = self.new_temp(node.type)

        # Create the opcode and append to list
        opcode = binary_ops[node.op] + "_" + node.left.type.name
        inst = (opcode, node.left.gen_location,
                node.right.gen_location, target)
        self.code.append(inst)

        # Store location of the result on the node
        node.gen_location = target

    def visit_IfStatement(self, node):
        # Step 1: Make a new BasicBlock for the conditional test
        ifblock = IfBlock()
        self.code.next_block = ifblock
        self.code = ifblock

        # Step 2:  Evaluate the test condition
        self.visit(node.condition)
        ifblock.testvar = node.condition.gen_location

        # Step 3: Create a branch for the if-body
        self.code = BasicBlock()
        ifblock.if_branch = self.code

        # Step 4: Traverse all of the statements in the if-biody
        print(node.__dict__)
        for bnode in node.tblock.statements:
            self.visit(bnode)

        # Step 5: If there's an else-clause, create a new block and
        if getattr(node, 'orelse', None):
            self.code = BasicBlock()
            ifblock.else_branch = self.code

            # Visit the body of the else-clause
            for bnode in node.fblock.statements:
                self.visit(bnode)

        # Step 6: Create a new basic block to start the next section
        self.code = BasicBlock()
        ifblock.next_block = self.code

    def visit_IfElseStatement(self, node):
        self.visit_IfStatement(node)

    def visit_WhileStatement(self, node):
        whileblock = WhileBlock()
        self.code.next_block = whileblock
        self.code = whileblock
        # Evaluate the condition
        self.visit(node.condition)

        # Save the variable where the test value is stored
        whileblock.testvar = node.condition.gen_location

        # Traverse the body
        whileblock.body = BasicBlock()
        self.code = whileblock.body
        self.visit(node.block)

        # Create the terminating block
        self.code = BasicBlock()
        whileblock.next_block = self.code

    def visit_BooleanOperator(self, node):
        self.visit_BinaryOperator(node)

    def visit_PrintStatement(self, node):
        # Visit the printed expression
        self.visit(node.expr)

        # Create the opcode and append to list
        inst = ('print_' + node.expr.type.name, node.expr.gen_location)
        self.code.append(inst)

    def visit_LoadVariable(self, node):
        """
        ('load_type', varname, target)
        """
        target = self.new_temp(node.type)
        opcode = 'load_' + node.type.name
        inst = (opcode, node.name, target)
        self.code.append(inst)
        node.gen_location = target

    def visit_UnaryOperator(self, node):
        """
        ('uadd_type',source,target)  # target = +source
        ('uneg_type',source,target)  # target = -source
        """
        self.visit(node.expr)
        target = self.new_temp(node.type)
        opcode = unary_ops[node.op] + '_' + node.type.name
        inst = (opcode, node.expr.gen_location, target)
        self.code.append(inst)
        node.gen_location = target

    def visit_ConstantDeclaration(self, node):
        """
        ('alloc_type',varname)
        ('store_type',source, varname)
        """
        # print('visit_ConstantDeclaration')
        opcode = 'global_' + node.type.name
        inst = (opcode, node.name)
        self.code.append(inst)
        self.visit(node.expr)
        opcode = 'store_' + node.type.name
        inst = (opcode, node.expr.gen_location, node.name)
        self.code.append(inst)

    def visit_VariableDeclaration(self, node):
        """
        ('alloc_type',varname)
        ('store_type',source, varname)
        """
        # print('visit_VariableDeclaration')
        if not node.is_global:
            opcode = 'alloc_' + node.type.name
        else:
            opcode = 'global_' + node.type.name
        inst = (opcode, node.name)
        self.code.append(inst)
        if node.expr:
            self.visit(node.expr)
            opcode = 'store_' + node.type.name
            inst = (opcode, node.expr.gen_location, node.name)
            self.code.append(inst)

    def visit_AssignmentStatement(self, node):
        """
        ('store_type',source, varname)
        """
        self.visit(node.expr)
        self.visit(node.store_location)

    def visit_StoreVariable(self, node):
        """
        ('store_type',source, varname)
        """
        # print('visit_StoreVariable')
        opcode = 'store_' + node.type.name
        inst = (opcode, node.expr.gen_location, node.name)
        self.code.append(inst)

    def visit_ExternFunctionDeclaration(self, node):
        # print('visit_ExternFunctionDeclaration')
        self.visit(node.prototype)
        paramtypes = [p.type.name for p in node.prototype.parameters]
        inst = ('extern_func', node.prototype.name,
                *paramtypes, node.type.name)
        self.code.append(inst)

    def visit_FunctionDeclaration(self, node):
        saved_block = self.code
        self.code = BasicBlock()
        paramtypes = [p.type.name for p in node.prototype.parameters]
        func = Function(node.prototype.name, node.type.name,
                        paramtypes, self.code)
        # print(func.name)
        self.functions.append(func)
        # Emit the function parameters
        for n, parm in enumerate(node.prototype.parameters):
            inst = ('parm_' + parm.type.name, parm.name, n)
            self.code.append(inst)

        # Visit the function body
        self.visit(node.statements)

        # Restore the last saved block
        self.code = saved_block

    def visit_ReturnStatement(self, node):
        self.visit(node.expr)
        self.code.append(
            ('return_' + node.expr.type.name, node.expr.gen_location))

    def visit_FunctionCall(self, node):
        # print('visit_FunctionCall')
        target = self.new_temp(node.type)
        args = []
        for arg in node.arglist:
            self.visit(arg)
            args.append(arg.gen_location)
        inst = ('call_func', node.name) + tuple(args) + (target,)
        self.code.append(inst)
        node.gen_location = target
        # Project 6 - Comparisons/Booleans
        # --------------------------------
        # You will need to extend this code to support comparisons and boolean
        # operators.  This will mostly involve the addition of new opcodes
        #
        # Project 7 - Control Flow
        # ------------------------
        # You will extend this code to emit code in basic blocks that are
        # linked together.  Most of the underlying code will remain unchanged
        # except that instructions will be append to a block.  You'll also need
        # to add support for if/else statements and while loops.
        #
        # Project 8 - Functions
        # ---------------------
        # You will extend this code to organize the emitted code into a
        # functions.
        # Each function will consist of a name and a starting block.   Any code
        # emitted outside of a function needs to be placed into a default
        # function called __init().

        # ----------------------------------------------------------------------
        #                          TESTING/MAIN PROGRAM
        # ----------------------------------------------------------------------


def compile_ircode(source):
    '''
    Generate intermediate code from source.
    '''
    from .parser import parse
    from .checker import check_program
    from .errors import errors_reported

    ast = parse(source)
    check_program(ast)

    # If no errors occurred, generate code
    if not errors_reported():
        gen = GenerateCode()
        gen.visit(ast)

        # !!!  This part will need to be changed slightly in Projects 7/8
        # return gen
        gen.code.append(('return_void',))
        return gen.functions
    else:
        return []


def main():
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m gone.ircode filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    functions = compile_ircode(source)

    # !!! This part will need to be changed slightly in Projects 7/8
    for func in functions:
        print(":::::::::::::::: FUNCTION: %s %s %s" % (func.name,
                                                       func.return_type,
                                                       func.parameters))
        PrintBlocks().visit(func.start_block)
        print()

if __name__ == '__main__':
    main()
