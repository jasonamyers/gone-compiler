# gone/parser.py
'''
Project 2:  Write a parser
==========================
In this project, you write the basic shell of a parser for the expression
language.  A formal BNF of the language follows.  Your task is to write
parsing rules and build the AST for this grammar using PLY.

program : statements
        | empty

statements :  statements statement
           |  statement

statement :  const_declaration
          |  var_declaration
          |  extern_declaration
          |  assign_statement
          |  print_statement

const_declaration : CONST ID = expression ;

var_declaration : VAR ID typename ;
                | VAR ID typename = expression ;

extern_declaration : EXTERN func_prototype ;

func_prototype : FUNC ID LPAREN parameters RPAREN typename

parameters : parameters , parm_declaration
           | parm_declaration
           | empty

parm_declaration : ID typename

assign_statement : store_location = expression ;

print_statement : PRINT expression ;

expression :  + expression
           |  - expression
           | expression + expression
           | expression - expression
           | expression * expression
           | expression / expression
           | ( expression )
           | ID ( exprlist )
           | load_location
           | literal

exprlist : | exprlist , expression
           | expression
           | empty

literal : INTEGER
        | FLOAT
        | STRING

location : ID

typename : ID

empty    :

To do the project, follow the instructions contained below.
'''

# ----------------------------------------------------------------------
# parsers are defined using PLYs yacc module.
#
# See http://www.dabeaz.com/ply/ply.html#ply_nn23
# ----------------------------------------------------------------------
from ply import yacc

# ----------------------------------------------------------------------
# The following import loads a function error(lineno,msg) that should be
# used to report all error messages issued by your parser.  Unit tests and
# other features of the compiler will rely on this function.  See the
# file errors.py for more documentation about the error handling mechanism.
from .errors import error

# ----------------------------------------------------------------------
# Get the token list defined in the lexer module.  This is required
# in order to validate and build the parsing tables.
from .tokenizer import tokens

# ----------------------------------------------------------------------
# Get the AST nodes.
# Read instructions in goneast.py
from .ast import *

# ----------------------------------------------------------------------
# Operator precedence table.   Operators must follow the same
# precedence rules as in Python.  Instructions to be given in the project.
# See http://www.dabeaz.com/ply/ply.html#ply_nn27

precedence = (
    ('left', 'LOR'),
    ('left', 'LAND'),
    ('nonassoc', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UNARY'),  # Dave Trolly Hack
)

# ----------------------------------------------------------------------
# YOUR TASK.   Translate the BNF in the doc string above into a collection
# of parser functions.  For example, a rule such as :
#
#   program : statements
#
# Gets turned into a Python function of the form:
#
# def p_program(p):
#      '''
#      program : statements
#      '''
#      p[0] = Program(p[1])
#
# For symbols such as '(' or '+', you'll need to replace with the name
# of the corresponding token such as LPAREN or PLUS.
#
# In the body of each rule, create an appropriate AST node and assign it
# to p[0] as shown above.
#
# For the purposes of lineno number tracking, you should assign a line number
# to each AST node as appropriate.  To do this, I suggest pulling the
# line number off of any nearby terminal symbol.  For example:
#
# def p_print_statement(p):
#     '''
#     print_statement: PRINT expr SEMI
#     '''
#     p[0] = PrintStatement(p[2],lineno=p.lineno(1))
#
#

# STARTING OUT
# ============
# The following grammar rules should give you an idea of how to start.
# Try running this file on the input Tests/parsetest0.g
#
# Now, add features by looking at the code in Tests/parsetest1-6.g


def p_program(p):
    """
    program : basicblock
    """
    p[0] = Program(p[1])


def p_basicblock(p):
    """
    basicblock : statements
    """
    p[0] = p[1]


def p_basicblock_empty(p):
    """
    basicblock : empty
    """
    p[0] = []


def p_statements(p):
    """
    statements :  statements statement
    """
    p[1].statements.append(p[2])
    p[0] = p[1]


def p_statements_single(p):
    """
    statements : statement
    """
    p[0] = Statements([p[1]])


def p_statement(p):
    """
    statement :  print_statement
              |  constant_declaration
              |  var_declaration
              |  assign_statement
              |  extern_declaration
              |  ifelse_statement
              |  if_statement
    """
    p[0] = p[1]


def p_print_statemnt(p):
    """
    print_statement : PRINT expression SEMI
    """
    p[0] = PrintStatement(p[2], lineno=p.lineno(1))


def p_if_statement(p):
    """
    if_statement : IF expression LBRACE basicblock RBRACE
    """
    p[0] = IfStatement(p[2], p[4], lineno=p.lineno(1))


def p_ifelse_statement(p):
    """
    ifelse_statement : IF expression LBRACE basicblock RBRACE ELSE LBRACE basicblock RBRACE
    """
    p[0] = IfElseStatement(p[2], p[4], p[8], lineno=p.lineno(1))


def p_expression_unary(p):
    """
    expression :  PLUS expression %prec UNARY
               |  MINUS expression %prec UNARY
               |  LNOT expression %prec UNARY
    """
    p[0] = UnaryOperator(p[1], p[2], lineno=p.lineno(1))


def p_expression_binary(p):
    """
    expression : expression PLUS  expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
    """
    p[0] = BinaryOperator(p[2], p[1], p[3], lineno=p.lineno(1))


def p_expression_boolean(p):
    """
    expression : expression LT expression
               | expression GT expression
               | expression LE expression
               | expression GE expression
               | expression EQ expression
               | expression NE expression
               | expression LAND expression
               | expression LOR expression
    """
    p[0] = BooleanOperator(p[2], p[1], p[3], lineno=p.lineno(1))


def p_expression(p):
    """
    expression : literal
    """
    p[0] = p[1]


def p_function_call(p):
    """
    expression : ID LPAREN  exprlist RPAREN
    """
    p[0] = FunctionCall(p[1], p[3])


def p_function_call_no_args(p):
    """
    expression : ID LPAREN RPAREN
    """
    p[0] = FunctionCall(p[1], [])


def p_exprlist(p):
    """
    exprlist : exprlist COMMA expression
    """
    p[0] = p[1]
    p[0].append(p[3])


def p_exprlist_single(p):
    """
    exprlist : expression
    """
    p[0] = [p[1]]


def p_empty(p):
    """
    empty :
    """


def p_expression_location(p):
    """
    expression : load_location
    """
    p[0] = p[1]


def p_assign_statement(p):
    """
    assign_statement : store_location ASSIGN expression SEMI
    """
    p[0] = AssignmentStatement(p[1], p[3], lineno=p.lineno(2))


def p_load_location(p):
    """
    load_location : ID
    """
    p[0] = LoadVariable(p[1], lineno=p.lineno(1))


def p_store_location(p):
    """
    store_location : ID
    """
    p[0] = StoreVariable(p[1], lineno=p.lineno(1))


def p_expression_group(p):
    """
    expression : LPAREN expression RPAREN
    """
    p[0] = p[2]


def p_constant_declaration(p):
    """
    constant_declaration : CONST ID ASSIGN expression SEMI
    """
    p[0] = ConstantDeclaration(p[2], p[4], lineno=p.lineno(1))


def p_typename(p):
    """
    typename : ID
    """
    p[0] = Typename(p[1], lineno=p.lineno(1))


def p_variable_declaration(p):
    """
    var_declaration : VAR ID typename SEMI
    """
    p[0] = VariableDeclaration(p[2], p[3], None, lineno=p.lineno(1))


def p_variable_declaration_assignment(p):
    """
    var_declaration : VAR ID typename ASSIGN expression SEMI
    """
    p[0] = VariableDeclaration(p[2], p[3], p[5], lineno=p.lineno(1))


def p_literal(p):
    """
    literal : INTEGER
            | FLOAT
            | STRING
    """
    p[0] = Literal(p[1], lineno=p.lineno(1))


def p_literal_bool(p):
    """
    literal : TRUE
            | FALSE
    """
    p[0] = Literal(p[1] == 'true', lineno=p.lineno(1))


def p_extern_declaration(p):
    """
    extern_declaration : EXTERN func_prototype SEMI
    """
    p[0] = ExternFunctionDeclaration(p[2], lineno=p.lineno(1))


def p_func_prototype(p):
    """
    func_prototype : FUNC ID LPAREN parameters RPAREN typename
    """
    p[0] = FunctionPrototype(p[2], p[4], p[6], lineno=p.lineno(1))


def p_func_prototype_no_args(p):
    """
    func_prototype : FUNC ID LPAREN RPAREN typename
    """
    p[0] = FunctionPrototype(p[2], [], p[5], lineno=p.lineno(1))


def p_parameters(p):
    """
    parameters : parameters COMMA parm_declaration
    """
    p[0] = p[1]
    p[0].append(p[3])


def p_parameter(p):
    """
    parameters : parm_declaration
    """
    p[0] = [p[1]]


def p_parm_declaration(p):
    """
    parm_declaration : ID typename
    """
    p[0] = ParameterDeclaration(p[1], p[2], lineno=p.lineno(1))

    # You need to implement the rest of the grammar rules here

    # ----------------------------------------------------------------------
    # DO NOT MODIFY
    #
    # catch-all error handling.   The following function gets called on any
    # bad input.  See http://www.dabeaz.com/ply/ply.html#ply_nn31


def p_error(p):
    if p:
        error(p.lineno, "Syntax error in input at token '%s'" % p.value)
    else:
        error("EOF", "Syntax error. No more input.")

# ----------------------------------------------------------------------
#                     DO NOT MODIFY ANYTHING BELOW HERE
# ----------------------------------------------------------------------

_parser = yacc.yacc()


def parse(source):
    """
    Parse source code into an AST. Return the top of the AST tree.
    """
    from .tokenizer import get_lexer
    lexer = get_lexer()

    ast = _parser.parse(source, lexer=lexer)
    return ast


def main():
    """
    Main program. Used for testing.
    """
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m gone.parser filename\n")
        raise SystemExit(1)

    # Parse and create the AST
    ast = parse(open(sys.argv[1]).read())

    # Output the resulting parse tree structure
    for depth, node in flatten(ast):
        print('%s%s' % (' ' * (4 * depth), node))

if __name__ == '__main__':
    main()
