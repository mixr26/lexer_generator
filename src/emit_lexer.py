# final stage of the lexer generator
# generates a pair of .h and .cpp files that represent the specified lexer
# since we generate c++ code, tokens and the lexer itself are represented by the eponymous classes
# the core of the generated lexer is a table-driven, direct-coded scanning algorithm, described in [1]
#
# [1] "Engineering a Compiler" 2nd edition, p. 60


# open the header file and emit necessary class and enum declarations (eg. Token class, States enum, etc.)
# also emit manifest code, which is provided by the user in the first part of the input file
def create_header_and_emit_manifest(manifest, token_list, states_num):
    with open("my_little_lexer.h", 'w') as header:
        # emit header guards and includes
        header.writelines([
            "#ifndef __MY_LITTLE_LEXER_H\n"
            "#define __MY_LITTLE_LEXER_H\n"
            "\n"
            "#include <string>\n"
            "#include <fstream>\n"
            "#include <iostream>\n"
            "#include <stack>\n"
            "#include <memory>\n"
            "#include <functional>\n"
            "#include <cstdint>\n\n"
        ])

        # emit an enum representing the token types
        token_num = 0
        header.write("enum class TokenType : uint16_t {\n")
        for token in token_list:
            header.write("\t" + token + " = " + str(token_num) + ",\n")
            token_num += 1
        header.writelines([
            "\tLAST = " + str(token_num) + ",\n"
            "\tERROR = " + str(token_num + 1) + ",\n"
            "\tDEFAULT = " + str(token_num + 2) + "\n"
            "};\n\n"
        ])

        # emit manifest code
        header.writelines(manifest)
        header.write("\n// Token class, which represents one lexeme of the input file.\n")

        # emit Token class
        header.writelines([
            "class Token {\n"
            "\tTokenType token_type;\n"
            "\tstd::string lexeme;\n"
            "\t// Line in input file which contains this lexeme. Currently only used for\n"
            "\t// error reporting.\n"
            "\tint16_t line;\n"
            "\t// Whether this token should be ignored.\n"
            "\tbool ignore;\n"
            "public:\n"
            "\tToken() = delete;\n"
            "\tToken(std::string lexeme = \"\", TokenType token_type = TokenType::DEFAULT, int16_t line = "
            "0, bool ignore = false)\n "
            "\t\t: lexeme(lexeme), token_type(token_type), line(line), ignore(ignore) {}\n\n"
            "\tvoid set_token_type(TokenType token_type) { this->token_type = token_type; }\n"
            "\tvoid set_ignore(bool ignore) { this->ignore = ignore; }\n"
            "\tvoid set_lexeme(std::string lexeme) { this->lexeme = lexeme; }\n\n"
            "\tconst std::string& get_lexeme() const { return this->lexeme; }\n"
            "\tTokenType get_token_type() const { return this->token_type; }\n"
            "\tbool is_ignore() const { return this->ignore; }\n"
            "\tint16_t get_line() const { return this->line; }\n"
            "};\n\n"
        ])

        # emit overloaded << operator prototype for Token class
        header.writelines([
            "// << operator overload for the Token class\n"
            "std::ostream& operator<<(std::ostream& os, const Token& tok);\n\n"
        ])

        # emit States enum
        header.writelines([
            "// States of the lexer DFA.\n"
            "enum class States : uint32_t {\n"
            "\tS0 = 0,\n"
        ])
        for i in range (1, states_num):
            header.write("\tS" + str(i) + ",\n")
        header.writelines([
            "\tSE,\n"
            "\tBAD\n"
            "};\n\n"
        ])

        # emit Lexer class
        header.writelines([
            "// Takes a stream of characters from the input file and tokenizes them\n"
            "// into a stream of lexemes.\n\n"
        ])

        header.writelines([
            "class Lexer {\n"
            "\tstatic uint32_t token_class;\n"
            "\tstatic bool is_last_token;\n"
            "\t// Input file.\n"
            "\tstd::ifstream filestream;\n"
            "\t// Current DFA state.\n"
            "\tStates state;\n"
            "\t// A stack of states used for backtracking.\n"
            "\tstd::stack<States> states_stack;\n"
            "\t// Return the next character of the input file.\n"
            "\tchar next_char() { return static_cast<char>(this->filestream.get()); }\n"
            "\t// Roll back the filestream one character.\n"
            "\tvoid rollback() { this->filestream.seekg(-1, std::ios_base::cur); }\n\n"
            "\t// Whether the provided state is an accepting state.\n"
            "\tstatic constexpr bool is_accepting_state(States);\n"
            "\t// Whether the provided character is newline.\n"
            "\tstatic constexpr bool is_newline(char c) { return c == 10 || c == 13; }\n"
            "\t// Try to tokenize next word from the input file. This is the heart of the\n"
            "\t// lexer. This method implements a table-driven, direct-coded scanning algorithm\n"
            "\t// described in 'Engineering a Compiler' by Cooper and Torczon (2nd edition, p. 60).\n"
            "\tstd::shared_ptr<Token> next_word();\n"
            "public:\n"
            "\tLexer() = delete;\n"
            "\tLexer(const Lexer&) = delete;\n"
            "\tLexer(Lexer&&) = delete;\n"
            "\tLexer(const char* input_file) { \n"
            "\t\tthis->filestream.open(input_file);\n"
            "\t\tif (!this->filestream.is_open()) {\n"
            "\t\t\tstd::cout << \"Input file not opened correctly!\" << std::endl;\n"
            "\t\t\texit(1);\n"
            "\t\t}\n"
            "\t}\n"
            "\t~Lexer() { this->filestream.close(); }\n"
            "\tLexer& operator=(Lexer&) = delete;\n"
            "\tLexer& operator=(Lexer&&) = delete;\n"
            "\tstd::shared_ptr<Token> get_next_word();\n"
            "};\n\n"
        ])

        # emit guard end
        header.write("#endif //__MY_LITTLE_LEXER_H")


# open the source file and emit class method definitions
def create_body(dstates, dtran, dfa_acc_states, pattern_descs, token_list):
    with open("my_little_lexer.cpp", 'w') as body:
        # emit includes
        body.writelines([
            "#include <type_traits>\n"
            "#include \"my_little_lexer.h\"\n\n"
        ])

        # emit overloaded << operator for Token class
        body.writelines([
            "// << operator overload for the Token class\n"
            "std::ostream& operator<<(std::ostream& os, const Token& tok) {\n"
            "\tos << \"Token type: \" << static_cast<uint16_t>(tok.get_token_type()) << std::endl;\n"
            "\tos << \"Lexeme: \" << tok.get_lexeme() << std::endl;\n"
            "\tos << \"Line: \" << tok.get_line() << std::endl;\n"
            "\tif (tok.get_token_type() == TokenType::LAST)\n"
            "\t\tos << \"Last\" << std::endl;\n\n"
            "\treturn os;\n"
            "}\n\n"
        ])

        # emit the functions which contain the user-provided code for each pattern
        for patt_desc in pattern_descs:
            if patt_desc.code != '':
                body.write("void " + patt_desc.name + "__(std::shared_ptr<Token> token)\n")
                for token in token_list:
                    if token in patt_desc.code:
                        patt_desc.code = patt_desc.code.replace(token, "TokenType::" + token)
                body.write(patt_desc.code)
                body.write("\n\n")

        # emit the is_accepting_state Lexer class method
        body.writelines([
            "// Whether the provided state is an accepting state.\n"
            "constexpr bool Lexer::is_accepting_state(States s) {\n"
            "\treturn (false\n"
        ])

        for state in dfa_acc_states:
            body.write("\t\t\t|| s == States::S" + str(state) + "\n")
        body.write("\t\t\t);\n")

        body.write("}\n\n")

        # emit the get_next_word Lexer method
        body.writelines([
            "std::shared_ptr<Token> Lexer::get_next_word() {\n"
            "\tstd::shared_ptr<Token> tok;\n"
            "\twhile((tok = this->next_word())->is_ignore());\n"
            "\treturn tok;\n"
            "}\n\n"
        ])

        # emit the next_word Lexer method
        body.writelines([
            "std::shared_ptr<Token> Lexer::next_word() {\n"
            "Init:\n"
            "\tstatic int16_t line{1};\n"
            "\tstd::string lexeme{""};\n"
            "\tchar c;\n"
            "\tthis->state = States::S0;\n\n"
            "\twhile (!this->states_stack.empty())\n"
            "\t\tthis->states_stack.pop();\n"
            "\tthis->states_stack.push(States::BAD);\n\n"
        ])

        for i in range(len(dstates)):
            body.writelines([
                "S" + str(i) + ":\n"
                "\tthis->state = States::S" + str(i) + ";\n\n"
                "\tc = this->next_char();\n"
                "\tif (this->is_newline(c))\n"
                "\t\tline++;\n\n"
                "\tlexeme.push_back(c);\n\n"
                "\tif (this->is_accepting_state(this->state))\n"
                "\t\twhile (!this->states_stack.empty())\n"
                "\t\t\tthis->states_stack.pop();\n"
                "\tthis->states_stack.push(this->state);\n\n"
            ])

            body.write("\tswitch (c) {\n")
            state = dtran[i]
            for in_sym in state:
                body.writelines([
                    "\tcase " + repr(in_sym[0]) + ":\n"
                    "\t\tgoto S" + str(in_sym[1]) + ";\n"
                ])
            body.writelines(["\tdefault:\n",
                             "\t\tthis->state = States::SE;\n"
                             "\t\tgoto SOut;\n"])

            body.write("\t}\n\n")

        body.writelines([
            "SOut:\n"
            "\twhile (!this->is_accepting_state(this->state) && this->state != States::BAD) {\n"
            "\t\tthis->state = this->states_stack.top();\n"
            "\t\tthis->states_stack.pop();\n\n"
            "\t\tif (this->is_newline(lexeme.back()))\n"
            "\t\t\tline--;\n\n"
            "\t\tif (!lexeme.empty())\n"
            "\t\t\tlexeme.pop_back();\n"
            "\t\tthis->rollback();\n"
            "\t}\n\n"
            "\tstd::shared_ptr<Token> tok{std::make_shared<Token>(lexeme, TokenType::DEFAULT, line, false)};\n"
            "\tif (this->is_accepting_state(this->state)) {\n"
        ])

        # each DFA accepting states recognize exactly one pattern, so just iterate through the list of patterns
        # and emit calls to its user-provided code
        body.write("\t\tswitch(this->state) {\n")
        for patt_desc in pattern_descs:
            for dfa_acc_state in patt_desc.dfa_acc_states:
                body.write("\t\tcase States::S" + str(dfa_acc_state) + ":\n")
                body.write("\t\t\t" + patt_desc.name + "__(tok);\n")
                body.write("\t\t\tbreak;\n")
        body.write("\t\t}\n")

        body.writelines([
            "\t}\n"
            "\telse if (c == std::char_traits<char>::eof())\n"
            "\t\ttok->set_token_type(TokenType::LAST);\n"
            "\telse\n"
            "\t\ttok->set_token_type(TokenType::ERROR);\n\n"
            "\treturn tok;\n"
        ])

        body.write("}\n\n")
