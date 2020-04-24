from enum import Enum
from numpy import *


# states of the regex lexical analyzer DFA
class States(Enum):
    SE = 0
    S0 = 1
    S1 = 2
    S2 = 3
    S3 = 4
    S4 = 5
    S5 = 6
    S6 = 7
    S7 = 8
    S8 = 9
    S9 = 10
    S10 = 11
    S11 = 12
    S12 = 13
    S13 = 14
    S14 = 15
    S15 = 16


# classes of expected input characters
class CharClass(Enum):
    char = 0
    digit = 1
    ocupar = 2
    ccupar = 3
    oblpar = 4
    cblpar = 5
    dash = 6
    opar = 7
    cpar = 8
    union = 9
    kleene = 10
    escape = 11


# transition matrix of the regex lexical analyzer DFA
# given the current state and the next input character, return the next DFA state
transition_matrix = array([
    [States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE,
     States.SE, States.SE],
    [States.S10, States.S10, States.S1, States.SE, States.S3, States.SE, States.SE, States.S11, States.S11, States.S11,
     States.S11, States.S12],
    [States.S1, States.SE, States.SE, States.S2, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE,
     States.SE, States.SE],
    [States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE,
     States.SE, States.SE],
    [States.S4, States.S7, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE,
     States.SE, States.SE],
    [States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.S5, States.SE, States.SE, States.SE,
     States.SE, States.SE],
    [States.S14, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE,
     States.SE, States.SE],
    [States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE,
     States.SE, States.SE],
    [States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.S8, States.SE, States.SE, States.SE,
     States.SE, States.SE],
    [States.SE, States.S15, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE,
     States.SE, States.SE],
    [States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE,
     States.SE, States.SE],
    [States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE,
     States.SE, States.SE],
    [States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE,
     States.SE, States.SE],
    [States.SE, States.SE, States.S13, States.S13, States.S13, States.S13, States.S13, States.S13, States.S13,
     States.S13, States.S13, States.S13],
    [States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE, States.SE,
     States.SE, States.SE],
    [States.SE, States.SE, States.SE, States.SE, States.SE, States.S6, States.SE, States.SE, States.SE, States.SE,
     States.SE, States.SE],
    [States.SE, States.SE, States.SE, States.SE, States.SE, States.S9, States.SE, States.SE, States.SE, States.SE,
     States.SE, States.SE]
])


def is_accepting_state(state):
    return state in (States.S2, States.S6, States.S9, States.S10, States.S11, States.S13)


def character_class(c):
    if c.isalpha():
        return CharClass.char
    elif c.isdigit():
        return CharClass.digit
    elif c == '{':
        return CharClass.ocupar
    elif c == '}':
        return CharClass.ccupar
    elif c == '[':
        return CharClass.oblpar
    elif c == ']':
        return CharClass.cblpar
    elif c == '-':
        return CharClass.dash
    elif c == '(':
        return CharClass.opar
    elif c == ')':
        return CharClass.cpar
    elif c == '|':
        return CharClass.union
    elif c == '*':
        return CharClass.kleene
    elif c == '\\':
        return CharClass.escape
    else:
        return CharClass.char


# types of tokens for the regex lexical analyzer
class TokenType(Enum):
    ID = 0
    INTERVAL = 1
    UNION = 2
    CONCAT = 3
    KLEENE = 4
    CHAR = 5
    OPAR = 6
    CPAR = 7
    SPECIAL = 8
    ERROR = 9


# given the DFA state, return ERROR if it is not an accepting state, else return the token type for the state
token_type_table = [TokenType.ERROR, TokenType.ERROR, TokenType.ERROR, TokenType.ID, TokenType.ERROR, TokenType.ERROR,
                    TokenType.ERROR, TokenType.INTERVAL, TokenType.ERROR, TokenType.ERROR, TokenType.INTERVAL,
                    TokenType.CHAR, TokenType.SPECIAL, TokenType.ERROR, TokenType.CHAR]


# token class for the regex lexical analyzer
class Token:
    def __init__(self, type, lexeme, end):
        self.type = type
        self.lexeme = lexeme
        self.end = end

    def __str__(self):
        return "Type: " + str(self.type) + " Lexeme: " + self.lexeme


# holds the regex being processed by the lexical analyzer
global_regex = ''
# after the tokenize_regex() call, contains the list of tokens if the tokenization was successful
token_list = []


# return the next input character
def next_char():
    global global_regex
    if len(global_regex) > 0:
        peek = global_regex[0:1]
        global_regex = global_regex[1:len(global_regex)]
        return peek, False
    else:
        return '', True


def rollback(c):
    global global_regex
    global_regex = c + global_regex


# extract the next regex token
# performs the simulation of the DFA
def get_next_token():
    global token_type_table
    lexeme = ''
    state = States.S0
    old_state = States.S0

    while state != States.SE:
        [peek, end] = next_char()
        if end:
            if is_accepting_state(state):
                return Token(token_type_table[state.value], lexeme, True)
            else:
                return Token(TokenType.ERROR, '', True)

        lexeme += peek
        global transition_matrix
        old_state = state
        state = transition_matrix[state.value][character_class(peek).value]

    rollback(peek)
    lexeme = lexeme[0:len(lexeme) - 1]

    if is_accepting_state(old_state):
        return Token(token_type_table[old_state.value], lexeme, False)
    else:
        return Token(TokenType.ERROR, '', True)


# populates token_list with regex tokens
def tokenize_regex(regex):
    global global_regex
    global token_list
    global_regex = regex
    token_list = []

    while True:
        token = get_next_token()

        # to reduce the number of DFA states, some special characters which should have different types were labeled as
        # SPECIAL
        if token.type == TokenType.SPECIAL:
            if token.lexeme == '(':
                token.type = TokenType.OPAR
            elif token.lexeme == ')':
                token.type = TokenType.CPAR
            elif token.lexeme == '|':
                token.type = TokenType.UNION
            else:
                token.type = TokenType.KLEENE

        # check whether the interval is correctly formed
        if token.type == TokenType.INTERVAL:
            if (token.lexeme[1] > token.lexeme[3]) or \
                    (token.lexeme[1].isupper() and token.lexeme[3].islower()):
                token.type = TokenType.ERROR
                break

        # strip the ID token of the unnecessary curly braces
        if token.type == TokenType.ID:
            token.lexeme = token.lexeme[1:len(token.lexeme) - 1]

        # concatenation operator is implicit (there is no input character for concatenation), but it would make the job
        # easier for the parser if it were explicit
        # we insert the concatenation operator token where appropriate
        if len(token_list) > 0:
            prev = token_list[len(token_list) - 1]
            if token.type in (TokenType.CHAR, TokenType.INTERVAL, TokenType.ID, TokenType.OPAR) and \
                    prev.type in (TokenType.CHAR, TokenType.INTERVAL, TokenType.ID, TokenType.CPAR, TokenType.KLEENE):
                token_list.append(Token(TokenType.CONCAT, '^', False))
        token_list.append(token)

        if token.end:
            break

    if token.type == TokenType.ERROR:
        print("Ill-formed regex!")
        token_list = []


if __name__ == "__main__":
    tokenize_regex("[1-5](abc)|a*{a}")
    for token in token_list:
        print(token)
