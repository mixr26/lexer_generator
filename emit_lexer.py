from regex_parser import parse
from regex_lexer import tokenize_regex
from regex_to_nfa import combine_nfas, regex_to_nfa, print_matrix
from nfa_to_dfa import nfa_to_dfa, print_dfa


# final stage of the lexer generator
# generates a pair of .h and .cpp files that represent the specified lexer
# since we generate c++ code, tokens and the lexer itself are represented by the eponymous classes
# the core of the generated lexer is a table-driven, direct-coded scanning algorithm, described in [1]
#
# [1] "Engineering a Compiler" 2nd edition, p. 60


# open the header file and emit necessary class and enum declarations (eg. Token class, States enum, etc.)
# also emit manifest code, which is provided by the user in the first part of the input file
def create_header_and_emit_manifest(manifest, states_num):
    with open("my_little_lexer.h", 'w') as header:
        # emit header guards and includes
        header.writelines([
            "#ifndef __MY_LITTLE_LEXER_H\n"
            "#define __MY_LITTLE_LEXER_H\n"
            "\n"
            "#include <string>\n"
            "#include <fstream>\n"
            "#include <stack>\n"
            "#include <cstdint>\n\n"
        ])

        # emit manifest code
        header.writelines(manifest)
        header.write("\n// Token class, which represents one lexeme of the input file.\n")

        # emit Token class
        header.writelines([
            "class Token {\n"
            "\tstd::string lexeme;\n"
            "\t// Is this the last token of the stream.\n"
            "\tbool last;\n"
            "\t// Line in input file which contains this lexeme. Currently only used for\n"
            "\t// error reporting.\n"
            "\tint16_t line;\n"
            "public:\n"
            "\tToken() = delete;\n"
            "\tToken(std::string lexeme, int16_t line = 0)\n"
            "\t\t: lexeme(lexeme), last(false), line(line) {}\n\n"
            "\tvoid set_lexeme(std::string lexeme) { this->lexeme = lexeme; }\n"
            "\tvoid set_last(bool last) { this->last = last; }\n\n"
            "\tstd::string& get_lexeme() { return this->lexeme; }\n"
            "\tbool is_last() { return this->last; }\n"
            "\tint16_t get_line() { return this->line; }\n"
            "};\n\n"
        ])

        # emit States enum
        header.write("// States of the lexer DFA.\n")
        header.write("enum class States : uint32_t {\n")
        header.write("\tS0 = 0,\n")
        for i in range (1, states_num):
            header.write("\tS" + str(i) + ",\n")
        header.write("\tBAD,\n")
        header.write("};\n\n")

        # emit Lexer class
        header.write("// Takes a stream of characters from the input file and tokenizes them\n")
        header.write("into a stream of lexemes.\n\n")

        header.writelines([
            "class Lexer {\n"
            "\tstatic uint32_t token_class;\n"
            "\tstatic bool is_last_token;\n"
            "\t// Input file.\n"
            "\tstd::ifstream filestream;\n"
            "\t// Current DFA state.\n"
            "\tStates state;\n"
            "\t// A stack of states used for backtracking.\n"
            "\tstd::stack<States> states_stack;\n\n"
            "\t// Return the next character of the input file.\n"
            "\tchar next_char() { return static_cast<char>(this->filestream.get()); }\n"
            "\t// Roll back the filestream one character.\n"
            "\tvoid rollback() { this->filestream.seekg(-1, std::ios_base::cur); }\n\n"
            "\t// Whether the provided state is an accepting state.\n"
            "\tstatic constexpr bool is_accepting_state(States);\n"
            "\t// Whether the provided character is newline.\n"
            "\tstatic constexpr bool is_newline(char c) { return c == 10 || c == 13; }\n"
            "public:\n"
            "\tLexer() = delete;\n"
            "\tLexer(const Lexer&) = delete;\n"
            "\tLexer(Lexer&&) = delete;\n"
            "\tLexer() {}\n"
            "\t~Lexer() {}\n"
            "\tLexer& operator=(Lexer&) = delete;\n"
            "\tLexer& operator=(Lexer&&) = delete;\n\n"
            "\t// Try to tokenize next word from the input file. This is the heart of the\n"
            "\t// lexer. This method implements a table-driven, direct-coded scanning algorithm\n"
            "\t// described in 'Engineering a Compiler' by Cooper and Torczon (2nd edition, p. 60).\n"
            "\tuint32_t next_word();\n"
            "};\n\n"
        ])

        # emit guard end
        header.write("#endif //__MY_LITTLE_LEXER_H")


# open the source file and emit class method definitions
def create_body(dstates, dtran, dfa_acc_states, nfa_acc_states):
    with open("my_little_lexer.cpp", 'w') as body:
        # emit includes
        body.writelines([
            "#include <type_traits>\n"
            "#include \"lexer.h\"\n\n"
        ])

        # emit the is_accepting_state Lexer class method
        body.writelines([
            "// Whether the provided state is an accepting state.\n"
            "constexpr bool Lexer::is_accepting_state(States s) {\n"
            "\treturn (false\n"
        ])

        for state in dfa_acc_states:
            body.write("\t\t\t|| s == S" + str(state) + "\n")
        body.write("\t\t\t);\n")

        body.write("}\n\n")

        # emit the next_word Lexer method
        body.writelines([
            "uint32_t Lexer::next_word() {\n"
            "Init:\n"
            "\tstatic int16_t line{1};\n"
            "\tstd::string lexeme{""};\n"
            "\tthis->state = States::S0;\n\n"
            "\twhile (!this->states_stack.empty())\n"
            "\t\tthis->states_stack.pop();\n"
            "\tthis->states_stack.push(States::BAD);\n\n"
        ])

        for i in range(len(dstates)):
            body.writelines([
                "S" + str(i) + ":\n"
                "\tthis->state = States::S" + str(i) + ";\n"
                "\tchar c{this->next_char()};\n"
                "\tif (c == std::char_traits<char>::eof())\n"
                "\t\tgoto SOut;\n\n"
                "\tif (this->is_newline(c))\n"
                "\t\tthis->line++;\n\n"
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
                    "\tcase " + "\'" + in_sym[0] + "\':\n"
                    "\t\tgoto S" + str(in_sym[1]) + ";\n"
                ])
            body.write("\tdefault:\n\t\tgoto SOut;\n")

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
        ])

        body.write("}\n\n")


if __name__ == "__main__":
    token_list_1 = tokenize_regex("(a|b)*abb")
    root_1 = parse(token_list_1)

    mat_1 = regex_to_nfa(root_1)

    pattern_dict = [("pat1", mat_1)]

    (nfa, nfa_acc_states) = combine_nfas(pattern_dict)
    print(nfa_acc_states)

    #(dstates, dtran, dfa_acc_states) = nfa_to_dfa(nfa, nfa_acc_states)
    #print_matrix(dtran)
    #print_dfa(dstates, dtran, dfa_acc_states)
    #print(dfa_acc_states)

    #create_header_and_emit_manifest([""], len(dstates))
    #create_body(dstates, dtran, dfa_acc_states, nfa_acc_states)