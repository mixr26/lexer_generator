from regex_lexer import tokenize_regex, TokenType
from enum import Enum


# node types for regex parser
class NodeType(Enum):
    CHAR = 0
    UNION = 1
    KLEENE = 2
    CONCAT = 3
    ERROR = 4


# represents a node within the abstract syntax tree (AST)
class Node:
    def __init__(self, type, value, *children):
        self.type = type
        self.value = value
        self.children = []
        for child in children:
            self.children.append(child)

    def __str__(self):
        return "Type: " + str(self.type) + " Value: " + str(self.value)


# helper function which prints the AST
def print_tree_postorder(root):
    for child in root.children:
        print_tree_postorder(child)
    print(root)


# parsing error exception
class ParserError(Exception):
    def __init__(self, message):
        self.token = Node(NodeType.ERROR, '')
        self.message = message

    def __str__(self):
        return self.message


# dictionary of IDs
# regex for every ID defined in the first stage should be hashed here, to be used in the second stage
id_dict = {}


# add a regex for an ID to the dictionary
def add_id(id, regex):
    global id_dict
    id_dict[id] = regex


# lookahead symbol for the parser
lookahead = None
# list of tokens acquired from the lexical analyzer
token_list = None
# AST is built using a stack-machine-like algorithm
# productions which represent operands of a regex expression (eg. factor) push the AST node which corresponds
# to the operand on the stack
# productions which represent operators of a regex expression (eg. concat) pop the right number of operands off
# the stack, create an operator AST node with popped operand nodes as children, and push the operator AST node
# back to the stack
stack = []


# get the next lookahead symbol
def peek():
    global token_list, lookahead
    if len(token_list) > 0:
        lookahead = token_list[0]


# check whether the expected symbol is indeed the next symbol of the token list
# advance the lookahead symbol
def match(type):
    global token_list
    if type == token_list[0].type:
        token_list = token_list[1:len(token_list)]
        peek()
    else:
        raise ParserError("Parse matching error!")


# six following functions represent productions of the LL(1) regex grammar
# recursive descent is used as parsing technique
# grammar in use is essentially the classic regex grammar transformed to be right-recursive, which makes it
# possible to implement it using recursive descent
def factor():
    global lookahead, stack
    if lookahead.type == TokenType.OPAR:
        match(TokenType.OPAR)
        union()
        match(TokenType.CPAR)
    elif lookahead.type == TokenType.CHAR:
        tmp = lookahead
        match(TokenType.CHAR)
        stack.append(Node(NodeType.CHAR, tmp.lexeme))
    elif lookahead.type == TokenType.ID:
        tmp = lookahead
        match(TokenType.ID)
        # check whether the ID was previously defined
        global id_dict
        if tmp.lexeme in id_dict.keys():
            stack.append(id_dict[tmp.lexeme])
        else:
            raise ParserError("ID " + tmp.lexeme + " was not previously defined!")
    else:
        raise ParserError("Parse error!")


def kleene():
    global lookahead, stack
    factor()
    if lookahead.type == TokenType.KLEENE:
        match(TokenType.KLEENE)
        op = stack.pop()
        stack.append(Node(NodeType.KLEENE, '*', op))


def temp2():
    global lookahead, stack
    if lookahead.type == TokenType.CONCAT:
        match(TokenType.CONCAT)
        kleene()
        op2 = stack.pop()
        op1 = stack.pop()
        stack.append(Node(NodeType.CONCAT, '^', op1, op2))
        temp2()


def concat():
    kleene()
    temp2()


def temp1():
    global lookahead, stack
    if lookahead.type == TokenType.UNION:
        match(TokenType.UNION)
        concat()
        op2 = stack.pop()
        op1 = stack.pop()
        stack.append(Node(NodeType.UNION, '|', op1, op2))
        temp1()


def union():
    concat()
    temp1()


# parser driver
# after the successful parse, the sole node on the stack is the AST root
# after the unsuccessful parse, the sole node on the stack is an AST error node
def parse(tokens):
    global stack, token_list
    try:
        token_list = tokens
        # load the first lookahead token
        peek()
        union()
    except ParserError as pe:
        print(pe)
        stack.clear()
        stack.append(Node(NodeType.ERROR, ''))


if __name__ == "__main__":
    token_list = tokenize_regex("([1-2][a-b])x|b*abc")
    parse(token_list)
    print_tree_postorder(stack[0])
