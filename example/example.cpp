#include <iostream>

#include "my_little_lexer.h"

int main() {
    Lexer lex("example.txt");
    std::shared_ptr<Token> tok;

    while (true) {
        tok = lex.get_next_word();
        TokenType token_type = tok->get_token_type();

        if (token_type == TokenType::ERROR) {
           std::cout << "Lexing error on line " << tok->get_line() << std::endl;
           break;
        }

        if (token_type == TokenType::LAST)
            break;

        std::cout << *tok << std::endl;
    }

    return 0;
}
