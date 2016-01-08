# bblock.py
'''
Project 7: Basic Blocks and Control Flow
----------------------------------------
This file defines classes and functions for creating and navigating
basic blocks.  You need to write all of the code needed yourself.
Make sure you fully work Exercise 7 first.
'''


class Block(object):

    def __init__(self):
        self.instructions = []   # Instructions in the block
        self.next_block = None    # Link to the next block

    def append(self, instr):
        self.instructions.append(instr)

    def __iter__(self):
        return iter(self.instructions)


class BasicBlock(Block):
    '''
    Class for a simple basic block.  Control flow unconditionally
    flows to the next block.
    '''
    pass


class IfBlock(Block):
    '''
    Class for a basic-block representing an if-else.  There are
    two branches to handle each possibility.
    '''

    def __init__(self):
        super(IfBlock, self).__init__()
        self.if_branch = None
        self.else_branch = None


class WhileBlock(Block):
    '''
    Class for representing a while-loop.  The instructions 
    in the block evaluate the loop condition.  The
    body link points to the blocks in the loop body.
    '''

    def __init__(self):
        super(WhileBlock, self).__init__()
        self.body = None
        self.testvar = None


class BlockVisitor(object):
    '''
    Class for visiting basic blocks.  Define a subclass and define
    methods such as visit_BasicBlock or visit_IfBlock to implement
    custom processing (similar to ASTs).
    '''

    def visit(self, block):
        while isinstance(block, Block):
            name = "visit_%s" % type(block).__name__
            if hasattr(self, name):
                getattr(self, name)(block)
            block = block.next_block


class PrintBlocks(BlockVisitor):

    def visit_BasicBlock(self, block):
        print("Block:[%s]" % block)
        for inst in block.instructions:
            print("    %s" % (inst,))
        print("")

    def visit_IfBlock(self, block):
        self.visit_BasicBlock(block)
        self.visit(block.if_branch)
        self.visit(block.else_branch)

    def visit_WhileBlock(self, block):
        self.visit_BasicBlock(block)
        self.visit(block.body)
