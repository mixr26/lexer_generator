# lexer_generator

## Introduction
This is my take on the lexical analyzer generator in the style of Flex.

It is not meant to be particularly fast or efficient, it is just meant to crystallize the concepts
of lexical analysis described in Chapter 3 of the 'Dragon Book' [1], hence Python was used as the programming tool.

Lexical analyzer generator is a tool which takes a specification of a language and creates a lexical analyzer which
is capable of scanning a program written in the specified language and returning a set of tokens which comprise the
program (the scanning process is usually the first stage of a compiler).

Token is an independent lexical unit of the program (eg. a variable name, a keyword, a chunk of whitespace,
or an assignment operator).

Writing a lexical analyzer for a large language is a tedious and error-prone job, so it is better left to a specialized tool.
Lexical analysis of the program boils down to simulation of a deterministic finite automaton (DFA) which represents
the language. A DFA is represented in code by the transition matrix which can get enormous pretty quickly, so you see
why it is unpractical to do it by hand.

## Method
As was said earlier, all of the algorithms which will be mentioned are described in [1], with the exception of
DFA simulation algorithm (essentially the scanning algorithm itself), which is presented in [2].

### Parsing the input file
Input file contains a specification of the language. Every token which can be extracted by the lexer is described using
a regular expression. In order to understand the regular expressions, first they must be tokenized (inception, huh?).
Since regular expression language is not too large, we can hand-code a lexer to do it without much problems.

**regex_lexer.py** contains the code for scanning a regular expression. Algorithm in use is a table-driven scanner from [2].
Transition matrix is small, and there are only a few DFA states. I decided not to support a wide range of standard regular
expression operators just so that the matrix size would not get out of hand.

Supported regex operators are:
  * Concatenation - ^
  * Union - |
  * Kleene closure - *
  * Parentheses - ()
  * Character sequences (intervals) - [a-z]
  
Once the tokens are extracted, they are parsed by the LL(1) grammar parser using recursive descent as parsing technique [1].
After parsing, we get an abstract syntax tree (AST) of the regular expression, with operators as nodes, and operands as
leaves of the tree.
Parser code is contained in **regex_parser.py**.

### Regex to DFA
The next step is converting the presented AST of the regular expression to non-deterministic finite automaton (NFA).
This is done using the McNaughton-Yamada-Thompson algorithm, as presented in **regex_to_nfa.py**.

There is only one more step before we get the complete transition matrix of the DFA, and that's the NFA to DFA conversion
in **nfa_to_dfa.py**.

### Lexer code generation
Now that we have the description of the DFA, we can emit the C++ which will simulate it. Tokens are represented by the *Token*
class, while the lexer itself is described by the *Lexer* class. The algorithm emitted for DFA simulation is a direct-coded
scanner from [1]. **emit_lexer.py** contains the code.

## Input file description
Input file which contains the language description must have an '.mll' extension.
It must have three distinct sections:
  * Manifest section contains user-written C++ code which will be inserted in the generated lexer's header file as-is.
  It begins with a label '_manifest:'.
  * Tokens section should be used to define token types, which can subsequently be used in set_token_type method. If this lexer generator is used as input to my parser generator, then the token sections of lexer and parser generators MUST look exactly the same. Token types described here will be enumerated as a part of TokenType enum.
  * Defines section can be used to give names to some frequently used regex patterns. Instead of writing the whole pattern
  later in the language description, its name could be used instead, enclosed in curly braces. This section begins with a
  label '_defines:'
  * Patterns section actually describes the tokens of the language. Each token must be given a name, a regex which defines it,
  and a piece of code which will be called when the pattern is recognized. This section is labeled with '_patterns:'.
  
  It must be noted that if the generated lexer recognizes a token which matches more than one given pattern, the pattern
  which comes earliest in the patterns section will be selected.
  
  A piece of code which is provided with the pattern will be put in a function which will be called when the pattern
  is recognized. This function has the following prototype:
  
        void foo(std::shared_ptr<Token> token)
        
  which means that the code can use the available methods of the *Token* class to manipulate the produced token.
  Available *Token* class methods are:
  
        // Set the token type.
        void set_token_type(TokenType token_type) { this->token_type = token_type; }
        // Whether the lexer should return this token, or just ignore it and search for the next.
        void set_ignore(bool ignore) { this->ignore = ignore; }
        // Set the lexeme of the token.
        void set_lexeme(std::string lexeme) { this->lexeme = lexeme; }

        // Get the lexeme of the token.
        const std::string& get_lexeme() const { return this->lexeme; }
        // Get the token type.
        TokenType get_token_type() const { return this->token_type; }
        // Whether this token should be ignored by the lexer.
        bool is_ignore() const { return this->ignore; }
        // Get the line of the input program on which this token was found.
        int16_t get_line() const { return this->line; }

## Example
All which was previously explained can be seen in action by running the lexer generator on the **example.mll** file
found in the *example/* directory. This example file describes a very simple language which recognizes variable names,
numbers, and if-then-else keywords.

**example.cpp** contains the *main()* function of the example program and includes the generated lexer's header. The program
calls the lexer to retreive and print tokens of the input program from the **example.txt** file.

To try this you should:
  * Download the *lexer_generator* binary from the *releases* tab of this GitHub page
  * Run the *lexer_generator* binary with **example.mll** as input file. This will produce header and source files of the
  generated lexer (**my_little_lexer.h** and **my_little_lexer.cpp**).
  * Compile the example program with a compiler which supports C++11 standard.
        
        g++ -std=c++11 my_little_lexer.cpp example.cpp -O3 -o example.out
        
  * Run the program and see the results!

## *TODO* list
* Support additional regex operators, such as +, [a-zA-Z] and similar.
* Implement a DFA minimalizing algorithm, which will further reduce the number of final DFA states.
* Change the input reading technique of the generated lexer to something like input buffering with double buffers,
as current character-by-character input reading is painfully slow.

## Citations
[1] Aho, A., Sethi, R. & Ullman, J. (1986). Compilers, principles, techniques, and tools.
Reading, Mass: Addison-Wesley Pub. Co.

[2] Cooper, K. & Torczon, L. (2012). Engineering a compiler. San Francisco: Morgan Kaufmann.
