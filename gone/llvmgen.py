# gone/llvmgen.py
'''
Project 5 : Generate LLVM
=========================
In this project, you're going to translate the SSA intermediate code
into LLVM IR.    Once you're done, your code will be runnable.  It
is strongly advised that you do *all* of the steps of Exercise 5
prior to starting this project.   Don't rush into it.

For Project 5, you are going to emit all of the LLVM instructions into
a single function main().  This is a temporary shim to get things to
work before we implement further support for user-defined functions in
Project 8.

Further instructions are contained in the comments below.
'''

# LLVM imports. Don't change this.

from llvmlite.ir import (
    Module, IRBuilder, Function, IntType, DoubleType, VoidType, Constant, GlobalVariable,
    FunctionType
    )

# Declare the LLVM type objects that you want to use for the low-level
# in our intermediate code.  Basically, you're going to need to
# declare the integer, float, and string types here.  These correspond
# to the types being used the intermediate code being created by
# the ircode.py file.

int_type    = IntType(32)         # 32-bit integer
float_type  = DoubleType()        # 64-bit float
string_type = None                # Up to you (leave until the end)

void_type   = VoidType()          # Void type.  This is a special type
                                  # used for internal functions returning
                                  # no value

# A dictionary that maps the typenames used in IR to the corresponding
# LLVM types defined above.   This is mainly provided for convenience
# so you can quickly look up the type object given its type name.
typemap = {
    'int' : int_type,
    'float' : float_type,
    'string' : string_type,
}

# The following class is going to generate the LLVM instruction stream.  
# The basic features of this class are going to mirror the experiments
# you tried in Exercise 5.  The execution model is somewhat similar
# to the visitor class.
#
# Given a sequence of instruction tuples such as this:
#
#         code = [ 
#              ('literal_int', 1, '_int_1'),
#              ('literal_int', 2, '_int_2'),
#              ('add_int', '_int_1', '_int_2, '_int_3')
#              ('print_int', '_int_3')
#              ...
#         ]
#
#    The class executes methods self.emit_opcode(args).  For example:
#
#             self.emit_literal_int(1, '_int_1')
#             self.emit_literal_int(2, '_int_2')
#             self.emit_add_int('_int_1', '_int_2', '_int_3')
#             self.emit_print_int('_int_3')
#
#    Internally, you'll need to track variables, constants and other
#    objects being created.  Use a Python dictionary to emulate
#    storage. 

class GenerateLLVM(object):
    def __init__(self, name='module'):
        # Perform the basic LLVM initialization.  You need the following parts:
        #
        #    1.  A top-level Module object
        #    2.  A Function instance in which to insert code
        #    3.  A Builder instance to generate instructions
        #
        # Note: For project 5, we don't have any user-defined
        # functions so we're just going to emit all LLVM code into a top
        # level function void main() { ... }.   This will get changed later.

        self.module = Module(name)
        self.function = Function(self.module,
                                 FunctionType(void_type, []),
                                 name='main')

        self.block = self.function.append_basic_block('entry')
        self.builder = IRBuilder(self.block)

        # Dictionary that holds all of the global variable/function declarations.
        # Any declaration in the Gone source code is going to get an entry here
        self.vars = {}

        # Dictionary that holds all of the temporary variables created in
        # the intermediate code.   For example, if you had an expression
        # like this:
        #
        #      a = b + c*d
        #
        # The corresponding intermediate code might look like this:
        #
        #      ('load_int', 'b', 'int_1')
        #      ('load_int', 'c', 'int_2')
        #      ('load_int', 'd', 'int_3')
        #      ('mul_int', 'int_2','int_3','int_4')
        #      ('add_int', 'int_1','int_4','int_5')
        #      ('store_int', 'int_5', 'a')
        #
        # The self.temp dictionary below is used to map names such as 'int_1', 
        # 'int_2' to their corresponding LLVM values.  Essentially, every time
        # you make anything in LLVM, it gets stored here.
        self.temps = {}

        # Initialize the runtime library functions (see below)
        self.declare_runtime_library()


    def declare_runtime_library(self):
        # Certain functions such as I/O and string handling are often easier
        # to implement in an external C library.  This method should make
        # the LLVM declarations for any runtime functions to be used
        # during code generation.    Please note that runtime function
        # functions are implemented in C in a separate file gonert.c

        self.runtime = {}
        
        # Declare printing functions
        self.runtime['_print_int'] = Function(self.module,
                                              FunctionType(void_type, [int_type]),
                                              name="_print_int")

        self.runtime['_print_float'] = Function(self.module,
                                                FunctionType(void_type, [float_type]),
                                                name="_print_float")

    def generate_code(self, ircode):
        # Given a sequence of SSA intermediate code tuples, generate LLVM
        # instructions using the current builder (self.builder).  Each
        # opcode tuple (opcode, args) is dispatched to a method of the
        # form self.emit_opcode(args)

        for opcode, *args in ircode:
            if hasattr(self, 'emit_'+opcode):
                getattr(self, 'emit_'+opcode)(*args)
            else:
                print('Warning: No emit_'+opcode+'() method')

        # Add a return statement.  Note, at this point, we don't really have
        # user-defined functions so this is a bit of hack--it may be removed later.
        self.builder.ret_void()

    # ----------------------------------------------------------------------
    # Opcode implementation.   You must implement the opcodes.  A few
    # sample opcodes have been given to get you started.
    # ----------------------------------------------------------------------

    # Creation of literal values.  Simply define as LLVM constants.
    def emit_literal_int(self, value, target):
        self.temps[target] = Constant(int_type, value)

    def emit_literal_float(self, value, target):
        pass                # You must implement
    
    # Allocation of variables.  Declare as global variables and set to
    # a sensible initial value.
    def emit_alloc_int(self, name):
        var = GlobalVariable(self.module, int_type, name=name)
        var.initializer = Constant(int_type, 0)
        self.vars[name] = var

    def emit_alloc_float(self, name):
        pass                # You must implement


    # Load/store instructions for variables.  Load needs to pull a
    # value from a global variable and store in a temporary. Store
    # goes in the opposite direction.
    def emit_load_int(self, name, target):
        self.temps[target] = self.builder.load(self.vars[name], target)

    def emit_load_float(self, name, target):
        pass                 # You must implement

    def emit_store_int(self, source, target):
        self.builder.store(self.temps[source], self.vars[target])

    def emit_store_float(self, source, target):
        pass                 # You must implement


    # Binary + operator
    def emit_add_int(self, left, right, target):
        self.temps[target] = self.builder.add(self.temps[left], self.temps[right], target)

    def emit_add_float(self, left, right, target):
        pass                 # You must implement

    # Binary - operator
    def emit_sub_int(self, left, right, target):
        pass                 # You must implement

    def emit_sub_float(self, left, right, target):
        pass                 # You must implement

    # Binary * operator
    def emit_mul_int(self, left, right, target):
        pass                 # You must implement

    def emit_mul_float(self, left, right, target):
        pass                 # You must implement

    # Binary / operator
    def emit_div_int(self, left, right, target):
        pass                 # You must implement

    def emit_div_float(self, left, right, target):
        pass                 # You must implement

    # Unary + operator
    def emit_uadd_int(self, source, target):
        pass                 # You must implement

    def emit_uadd_float(self, source, target):
        pass                 # You must implement

    # Unary - operator
    def emit_usub_int(self, source, target):
        pass                 # You must implement
        self.temps[target] = self.builder.sub(
            Constant(int_type, 0),
            self.temps[source],
            target)

    def emit_usub_float(self, source, target):
        pass                 # You must implement

    # Print statements
    def emit_print_int(self, source):
        self.builder.call(self.runtime['_print_int'], [self.temps[source]])

    def emit_print_float(self, source):
        pass                 # You must implement

    # Extern function declaration.  
    def emit_extern_func(self, name, rettypename, *parmtypenames):
        rettype = typemap[rettypename]
        parmtypes = [typemap[pname] for pname in parmtypenames]
        func_type = FunctionType(rettype, parmtypes)
        self.vars[name] = Function(self.module, func_type, name=name)

    # Call an external function.
    def emit_call_func(self, funcname, *args):
        pass                 # You must implement

#######################################################################
#                      TESTING/MAIN PROGRAM
#######################################################################

def compile_llvm(source):
    from .ircode import compile_ircode

    # Compile intermediate code 
    # !!! This needs to be changed in Project 7/8
    code = compile_ircode(source)

    # Make the low-level code generator
    generator = GenerateLLVM()

    # Generate low-level code
    # !!! This needs to be changed in Project 7/8
    generator.generate_code(code)

    return str(generator.module)

def main():
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m gone.llvmgen filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    llvm_code = compile_llvm(source)
    print(llvm_code)

if __name__ == '__main__':
    main()



        
        
        
