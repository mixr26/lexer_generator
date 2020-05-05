import sys
from emit_lexer import create_header_and_emit_manifest, create_body
from nfa_to_dfa import nfa_to_dfa
from pattern_descriptor import PatternDesc
from regex_lexer import tokenize_regex, TokenType, LexerError
from regex_parser import parse, add_id, ParserError
from regex_to_nfa import regex_to_nfa, combine_nfas


# error reporting helper routine
def report_error(error, line_num):
    print("Line " + str(line_num) + ": ")
    print(error)
    exit(1)


# extract the name and the pattern itself from the provided line of text from the input file
def extract_name_and_pattern(line):
    # extract the name
    if line.count(' ') == 0:
        report_error("Ill-formed regex pattern!", line_num)
    space_index = line.index(' ')
    name = line[0:space_index]

    # extract the pattern
    if line.count('%{') != 1:
        report_error("Ill-formed regex pattern!", line_num)
    ocuparr_index = line.index('%{')

    if line.count('}%') != 1:
        report_error("Ill-formed regex pattern!", line_num)
    ccparr_index = line.index('}%')

    if ccparr_index < ocuparr_index or space_index > ocuparr_index:
        report_error("Ill-formed regex pattern!", line_num)

    pattern = line[ocuparr_index + 2:ccparr_index]

    # treat the newline and tab characters so that they get recognized by the regex lexer
    pattern = pattern.replace("\\n", "\n")
    pattern = pattern.replace("\\t", "\t")

    return name, pattern


# extract the code fragment of the pattern from the provided line of text from the input file
def extract_code(line):
    if line.count('#{') != 1:
        report_error("Ill-formed regex pattern!", line_num)
    ocuparr_index = line.index('#{')

    if line.count('}#') != 1:
        report_error("Ill-formed regex pattern!", line_num)
    ccparr_index = line.index('}#')

    if ccparr_index < ocuparr_index:
        report_error("Ill-formed regex pattern!", line_num)

    return line[ocuparr_index + 1:ccparr_index + 1]


# parse the manifest part of the input file
def collect_manifest_code(file, line_num):
    manifest = file.readline()
    line_num += 1

    manifest = manifest.strip()
    manifest_code = ''
    if manifest != "_manifest:":
        report_error("_manifest: label not found!", line_num)

    while True:
        file_pos = file.tell()
        line = file.readline()
        line_num += 1
        if not line or "_defines:" in line:
            file.seek(file_pos)
            break
        manifest_code += line

    return manifest_code, line_num


# populate the ID table of the regex parser
# for every defined identifier, create a parse tree and add it to the dictionary
def hash_identifiers(file, line_num):
    defines = file.readline().strip()
    line_num += 1
    if defines != "_defines:":
        report_error("_defines: label not found!", line_num)

    while True:
        file_pos = file.tell()
        line = file.readline()
        line_num += 1
        if not line or "_patterns:" in line:
            file.seek(file_pos)
            break

        line = line.strip()
        (name, pattern) = extract_name_and_pattern(line)

        # try to tokenize the regex pattern
        token_list = None
        try:
            token_list = tokenize_regex(pattern)
        except LexerError as le:
            report_error(le, line_num)

        # try to parse the regex pattern
        root = None
        try:
            root = parse(token_list)
        except ParserError as pe:
            report_error(pe, line_num)

        # save the identifier and its AST in the dictionary
        add_id(name, root)

    return line_num


# parse the regex patterns and emit the finished lexical analyzer
def do_the_magic(file, line_num, manifest_code):
    patterns = file.readline().strip()
    line_num += 1
    if patterns != "_patterns:":
        report_error("_patterns: label not found!", line_num)

    pattern_descs = []
    while True:
        file_pos = file.tell()
        line = file.readline()
        line_num += 1
        if not line:
            file.seek(file_pos)
            break

        line = line.strip()
        (name, pattern) = extract_name_and_pattern(line)
        code = extract_code(line)

        # try to tokenize the regex pattern
        token_list = None
        try:
            token_list = tokenize_regex(pattern)
        except LexerError as le:
            report_error(le, line_num)

        # try to parse the regex pattern
        root = None
        try:
            root = parse(token_list)
        except ParserError as pe:
            report_error(pe, line_num)

        # convert the AST to nfa
        nfa = regex_to_nfa(root)

        # create PatternDesc object and append it to the list
        pattern_descs.append(PatternDesc(name, code, nfa))

    # combine the NFAs
    (nfa, pattern_descs) = combine_nfas(pattern_descs)

    # convert NFA to DFA
    (dstates, dtran, dfa_acc_states, pattern_descs) = nfa_to_dfa(nfa, pattern_descs)

    # emit the actual lexer code
    create_header_and_emit_manifest(manifest_code, len(dstates))
    create_body(dstates, dtran, dfa_acc_states, pattern_descs)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        report_error("Incorrect number of command line arguments! Should be only the input file name!", 0)

    filename = sys.argv[1]
    if ".mll" not in filename:
        print("Input file name should have .mll extension!")
        exit(1)

    with open(filename, 'r') as file:
        line_num = 0
        # collect the manifest code
        (manifest_code, line_num) = collect_manifest_code(file, line_num)

        # collect the defines
        line_num = hash_identifiers(file, line_num)

        # parse the regex patterns and emit lexer code
        do_the_magic(file, line_num, manifest_code)
