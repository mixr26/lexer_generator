from regex_lexer import tokenize_regex, Token, TokenType


lookahead = None
g_token_list = None


def peek():
    global token_list, lookahead
    (lookahead, token_list) = (token_list[0], token_list[1:len(token_list)-1])


def union(parent):
    return 9


def parse(token_list):
    peek()
    root = None
    union(root)


if __name__ == "__main__":
    token_list = tokenize_regex("[1-5](abc)|a*{a}")
    for token in token_list:
        print(token)
    parse(token_list)