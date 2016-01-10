# gone/interp.py
'''
Reference Interpreter - Optional
================================

This is an interpreter than can run gone programs directly from the
generated IR code.  This can be used to check results without
requiring an LLVM dependency.

To run a program use::

    bash % python3 -m gone.interp someprogram.g

This file will likely only work in the final stages of the compiler
project.  You may need to make modifications to it to get it to work.
'''
import sys
from . import bblock


class Frame(object):
    '''
    Object representing a stack frame.
    '''

    def __init__(self, args):
        self.args = args
        self.vars = {'return': None}

    def __getitem__(self, name):
        return self.vars[name]

    def __setitem__(self, name, value):
        self.vars[name] = value

    def __contains__(self, name):
        return name in self.vars


class Interpreter(object):
    '''
    Runs an interpreter on the SSA intermediate code generated for
    your compiler.   The implementation idea is as follows.  Given
    a sequence of instruction tuples such as:

         code = [
              ('literal_int', 1, '_int_1'),
              ('literal_int', 2, '_int_2'),
              ('add_int', '_int_1', '_int_2, '_int_3')
              ('print_int', '_int_3')
              ...
         ]

    The class executes methods self.run_opcode(args).  For example:

             self.run_literal_int(1, '_int_1')
             self.run_literal_int(2, '_int_2')
             self.run_add_int('_int_1', '_int_2', '_int_3')
             self.run_print_int('_int_3')

    To store the values of variables created in the intermediate
    language, simply use a dictionary.

    For external function declarations, allow specific Python modules
    (e.g., math, os, etc.) to be registered with the interpreter.
    We don't have namespaces in the source language so this is going
    to be a bit of sick hack.
    '''

    def __init__(self, name="module"):
        # Frame stack
        self.framestack = []

        # Current stack frame
        self.frame = None

        # Current program counter
        self.pc = 0

        # Global variables
        self.globals = {}

        # List of Python modules to search for external decls
        external_libs = ['math', 'os']
        if sys.version_info.major >= 3:
            external_libs.append('builtins')
        else:
            external_libs.append('__builtin__')

        self.external_libs = [__import__(name) for name in external_libs]

    # Add user-defined functions to the globals.  Builds a dictionary mapping
    # function names to the code associated with each function
    def register_functions(self, functionlist):
        self.functions = {}
        for func, code in functionlist:
            self.functions[func.name] = code

    def execute_function(self, funcname, args):
        '''
        Run intermediate code in the interpreter.  ircode is a list
        of instruction tuples.  Each instruction (opcode, *args) is
        dispatched to a method self.run_opcode(*args)
        '''
        code = self.functions[funcname]
        self.framestack.append((self.pc, self.frame))
        self.frame = Frame(args)
        self.pc = 0
        while self.pc < len(code):
            instr = code[self.pc]
            opcode = instr[0]
            self.pc += 1
            if hasattr(self, "run_" + opcode):
                getattr(self, "run_" + opcode)(*instr[1:])
            else:
                print("Warning: No run_" + opcode + "() method")
            if self.pc < 0:
                break
        result = self.frame['return']
        self.pc, self.frame = self.framestack.pop()
        return result

    # Interpreter opcodes

    def run_literal_int(self, value, target):
        '''
        Create a literal integer value
        '''
        self.frame[target] = value

    def run_add_int(self, left, right, target):
        '''
        Add two integer varibles
        '''
        self.frame[target] = self.frame[left] + self.frame[right]

    def run_print_int(self, source):
        '''
        Output an integer value.
        '''
        print(self.frame[source])

    run_literal_float = run_literal_int
    run_literal_string = run_literal_int
    run_literal_bool = run_literal_int

    def run_alloc_int(self, name):
        self.frame[name] = 0

    def run_alloc_float(self, name):
        self.frame[name] = 0.0

    def run_alloc_string(self, name):
        self.frame[name] = ''

    def run_alloc_bool(self, name):
        self.frame[name] = False

    # Added support for global variable declarations
    def run_global_int(self, name):
        self.globals[name] = 0

    def run_global_float(self, name):
        self.globals[name] = 0.0

    def run_global_string(self, name):
        self.globals[name] = ''

    def run_global_bool(self, name):
        self.globals[name] = False

    def run_store_int(self, source, target):
        if target in self.frame:
            self.frame[target] = self.frame[source]
        else:
            self.globals[target] = self.frame[source]

    run_store_float = run_store_int
    run_store_string = run_store_int
    run_store_bool = run_store_int

    def run_load_int(self, name, target):
        if name in self.frame:
            self.frame[target] = self.frame[name]
        else:
            self.frame[target] = self.globals[name]

    run_load_float = run_load_int
    run_load_string = run_load_int
    run_load_bool = run_load_int

    def run_add_int(self, left, right, target):
        self.frame[target] = self.frame[left] + self.frame[right]

    run_add_float = run_add_int
    run_add_string = run_add_int

    def run_sub_int(self, left, right, target):
        self.frame[target] = self.frame[left] - self.frame[right]

    run_sub_float = run_sub_int

    def run_mul_int(self, left, right, target):
        self.frame[target] = self.frame[left] * self.frame[right]

    run_mul_float = run_mul_int

    def run_div_int(self, left, right, target):
        self.frame[target] = self.frame[left] // self.frame[right]

    def run_div_float(self, left, right, target):
        self.frame[target] = self.frame[left] / self.frame[right]

    def run_uadd_int(self, source, target):
        self.frame[target] = self.frame[source]

    run_uadd_float = run_uadd_int

    def run_usub_int(self, source, target):
        self.frame[target] = -self.frame[source]

    run_usub_float = run_usub_int

    def run_print_int(self, source):
        print(self.frame[source])

    run_print_float = run_print_int
    run_print_string = run_print_int
    run_print_bool = run_print_int

    def run_extern_func(self, name, rettypename, *parmtypenames):
        '''
        Scan the list of external modules for a matching function name.
        Place a reference to the external function in the dict of vars.
        '''
        for module in self.external_libs:
            func = getattr(module, name, None)
            if func:
                self.globals[name] = func
                break
        else:
            raise RuntimeError("No extern function %s found" % name)

    def run_call_func(self, funcname, *args):
        '''
        Call a previously declared external function.
        '''
        target = args[-1]
        argvals = [self.frame[name] for name in args[:-1]]
        if funcname in self.globals:
            func = self.globals[funcname]
            self.frame[target] = func(*argvals)
        elif funcname in self.functions:
            result = self.execute_function(funcname, argvals)
            self.frame[target] = result
        else:
            raise RuntimeError("No function %s found" % name)

    def run_lt_int(self, left, right, target):
        self.frame[target] = self.frame[left] < self.frame[right]

    run_lt_float = run_lt_int
    run_lt_string = run_lt_int

    def run_le_int(self, left, right, target):
        self.frame[target] = self.frame[left] <= self.frame[right]

    run_le_float = run_le_int
    run_le_string = run_le_int

    def run_gt_int(self, left, right, target):
        self.frame[target] = self.frame[left] > self.frame[right]

    run_gt_float = run_gt_int
    run_gt_string = run_gt_int

    def run_ge_int(self, left, right, target):
        self.frame[target] = self.frame[left] >= self.frame[right]

    run_ge_float = run_ge_int
    run_ge_string = run_ge_int

    def run_eq_int(self, left, right, target):
        self.frame[target] = self.frame[left] == self.frame[right]

    run_eq_float = run_eq_int
    run_eq_string = run_eq_int
    run_eq_bool = run_eq_int

    def run_ne_int(self, left, right, target):
        self.frame[target] = self.frame[left] != self.frame[right]

    run_ne_float = run_ne_int
    run_ne_string = run_ne_int
    run_ne_bool = run_ne_int

    def run_and_bool(self, left, right, target):
        self.frame[target] = self.frame[left] and self.frame[right]

    def run_or_bool(self, left, right, target):
        self.frame[target] = self.frame[left] or self.frame[right]

    def run_not_bool(self, source, target):
        self.frame[target] = not self.frame[source]

    def run_return_int(self, source):
        self.frame['return'] = self.frame[source]
        self.pc = -1
    run_return_float = run_return_int
    run_return_string = run_return_int
    run_return_bool = run_return_int

    def run_return_void(self):
        self.frame['return'] = None
        self.pc = -1

    def run_parm_int(self, name, num):
        self.frame[name] = self.frame.args[num]

    run_parm_float = run_parm_int
    run_parm_string = run_parm_int
    run_parm_bool = run_parm_int

    def run_jump(self, target):
        self.pc = target

    def run_cbranch(self, testvar, true_target, false_target):
        if self.frame[testvar]:
            self.pc = true_target
        else:
            self.pc = false_target

# BlockLinker.  This block visitor walks through the block structure
# and turns it into a single sequence of instructions with added
# jump and cbranch instructions.


class BlockLinker(bblock.BlockVisitor):

    def __init__(self):
        # The single sequence of code
        self.code = []

        # Mapping of block ids to code positions
        self.blockmap = {}

    def link_blocks(self, start_block):
        # Visit the starting block
        self.visit(start_block)

        # Patch the jumps in the code sequence
        for n, instr in enumerate(self.code):
            opcode = instr[0]
            if opcode == 'jump' and isinstance(instr[1], bblock.Block):
                newinstr = ('jump', self.blockmap[id(instr[1])])
                self.code[n] = newinstr
            elif opcode == 'cbranch' and isinstance(instr[2], bblock.Block):
                newinstr = ('cbranch', instr[1], self.blockmap[
                            id(instr[2])], self.blockmap[id(instr[3])])
                self.code[n] = newinstr

    def visit_BasicBlock(self, block):
        self.blockmap[id(block)] = len(self.code)
        self.code.extend(block.instructions)
        if block.next_block is not None:
            self.code.append(('jump', block.next_block))

    def visit_IfBlock(self, block):
        self.blockmap[id(block)] = len(self.code)
        self.code.extend(block.instructions)
        # Insert the conditional branch instruction
        if block.else_branch is None:
            else_branch = block.next_block
        else:
            else_branch = block.else_branch
        self.code.append(
            ('cbranch', block.testvar, block.if_branch, else_branch))

        # Visit the if-branch
        self.visit(block.if_branch)

        # Insert a jump to the merge point
        self.code.append(('jump', block.next_block))

        # Visit the else-branch (if any)
        if block.else_branch is not None:
            self.visit(block.else_branch)
            self.code.append(('jump', block.next_block))

    def visit_WhileBlock(self, block):
        self.blockmap[id(block)] = len(self.code)
        self.code.extend(block.instructions)
        # Insert the conditional branch instruction
        self.code.append(
            ('cbranch', block.testvar, block.body, block.next_block))

        # Visit the loop-body
        self.visit(block.body)

        # Insert the jump back to the loop test
        self.code.append(('jump', block))

# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW
# ----------------------------------------------------------------------


def main():
    import sys
    from .ircode import compile_ircode
    from .errors import errors_reported

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m gone.interp filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    functions = compile_ircode(source)
    if not errors_reported():
        # Take the list of functions and build fully linked versions
        linked_functions = []
        for func in functions:
            linker = BlockLinker()
            linker.link_blocks(func.start_block)
            linked_functions.append((func, linker.code))

        # Monkey patch os with a putchar() function so certain examples work
        import os
        os.putchar = lambda x: os.write(1, chr(x).encode('latin-1'))

        interpreter = Interpreter()
        interpreter.register_functions(linked_functions)
        # Execute the __init function which is responsible for global vars and
        # constants
        interpreter.execute_function('__init', [])

        # Execute the main() entry point
        result = interpreter.execute_function('main', [])
        print("Program Returned: %d" % result)

if __name__ == '__main__':
    main()
