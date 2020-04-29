from regex_parser import parse, NodeType
from regex_lexer import tokenize_regex
import networkx as nx
import matplotlib.pyplot as plt

# transformation of regex ASTs to non-deterministic finite automata (NFAs) using the McNaughton-Yamada-Thompson
# algorithm
# we start by transforming the simplest one character expressions, which are then fed to the functions for transforming
# Kleene closure, union or concatenation, depending on the AST
# three properties of the resulting NFAs dictate the way the transition matrix is represented in the program [1]
#   1. DFA has one start state and one accepting state
#      the accepting state has no outgoing transitions, and the start state has no incoming transitions
#   2. DFA has at most twice as many states as there are operators and operands in the regular expression
#   3. each state of DFA other than the accepting state has either one outgoing transition on an input symbol
#      or two outgoing transitions, both on epsilon
# thus, the transition matrix is sparse so I decided to leave out the empty transitions and implement every state as
# a list of tuples whose first element is the input symbol of the transition, while the other elements (one or two) are
# the outgoing states
# first row of the matrix always represents the starting state of the NFA, while the last row represents the
# accepting state
#
# [1] The Dragon Book, 2nd Ed, p. 161


# helper function which visualizes the graph
def visualize_graph(mat):
    graph = nx.DiGraph()

    for i in range(0, len(mat)):
        for in_sym in mat[i]:
            if in_sym[0] == 'eps':
                if len(in_sym) == 1:
                    continue
                elif len(in_sym) == 3:
                    graph.add_edge(i, in_sym[2], sym='eps')
                graph.add_edge(i, in_sym[1], sym='eps')
            else:
                graph.add_edge(i, in_sym[1], sym=in_sym[0])

    nx.draw(graph, with_labels=True)
    plt.show()


# helper function which prints the matrix
def print_matrix(mat):
    for state in mat:
        print(state)
    print()


# transform the simplest one-character expression (eg. 'a') to NFA
def transform_simple_expression(expr):
    lexeme = expr.value
    return [
        [[lexeme, 1], ['eps']],
        [['eps']]
    ]


# helper function which offsets the outgoing states of the matrix by the desired value
def offset_outgoing_states(mat, offset):
    for state in mat:
        for in_sym in state:
            if in_sym[0] == 'eps':
                if len(in_sym) == 1:
                    continue
                elif len(in_sym) == 3:
                    in_sym[2] += offset
                in_sym[1] += offset
            else:
                in_sym[1] += offset

    return mat


# create Kleene closure NFA
def transform_kleene(mat):
    # offset all the outgoing states by one, as we are inserting starting state as the first row of the matrix
    mat = offset_outgoing_states(mat, 1)

    # insert new starting and accepting states
    mat.insert(0, [['eps', 1, len(mat) + 1]])
    mat.append([['eps']])

    # correct the old accepting state
    mat[len(mat) - 2][0].append(1)
    mat[len(mat) - 2][0].append(len(mat) - 1)

    return mat


def transform_concat(left, right):
    # offset the outgoing states in the right DFA matrix, as we are removing the first (starting) state from it
    # and appending it to the left NFA matrix
    right = offset_outgoing_states(right, len(left) - 1)

    # remove the starting state from the right NFA matrix
    start_state_right = right[0]
    right.remove(right[0])

    # merge the old right DFA matrix starting state with the old left NFA matrix accepting state
    accept_index_left = len(left) - 1
    left[accept_index_left].clear()
    for in_sym in start_state_right:
        left[accept_index_left].append(in_sym)

    # append the states in the right NFA matrix to the left NFA matrix
    for state in right:
        left.append(state)

    return left


def transform_union(left, right):
    # offset the outgoing states of the left NFA matrix, as we are adding the starting state of the new DFA matrix
    # at the beginning
    left = offset_outgoing_states(left, 1)

    # offset the outgoing states of the right NFA matrix, as we are appending it to the left NFA matrix (and also
    # adding the starting state at the beginning of the left NFA matrix)
    right = offset_outgoing_states(right, len(left) + 1)

    start_state_right = len(left) + 1
    new_accept_state_index = len(left) + len(right) + 1
    # make the old accepting states point to the new accepting state
    left[len(left) - 1][0].append(new_accept_state_index)
    right[len(right) - 1][0].append(new_accept_state_index)

    # append the right NFA matrix to the left NFA matrix
    for state in right:
        left.append(state)

    # add the new starting and accepting state
    left.insert(0, [['eps', 1, start_state_right]])
    left.append([['eps']])

    return left


# regex to NFA transformation driver
# essentially a postorder walk over the regex AST
def regex_to_nfa(root):
    child_nfa = [regex_to_nfa(child) for child in root.children]

    if root.type == NodeType.CHAR:
        return transform_simple_expression(root)
    elif root.type == NodeType.KLEENE:
        return transform_kleene(*child_nfa)
    elif root.type == NodeType.UNION:
        return transform_union(*child_nfa)
    else:
        return transform_concat(*child_nfa)


# since we generally have multiple regex pattern in the input program, describing different lexical categories,
# we need a way to combine all the resulting NFAs into one, which will be transformed to DFA
# we introduce a new starting state for the big NFA which has outgoing transitions on epsilon to starting states of
# all the individual NFAs
# alongside the new NFA transition matrix, function also returns a set of accepting states of all the individual NFAs
def combine_nfas(nfas):
    combined_nfa = [[['eps']]]
    accepting_states = {}

    # if there is only one pattern in the list, don't bother
    if len(nfas) == 1:
        return nfas[0][1],  {len(nfas[0][1]) - 1: nfas[0][0]}

    current_nfa_starting_state = 1
    offset = 1
    for pair in nfas:
        nfa = pair[1]
        nfa = offset_outgoing_states(nfa, offset)
        for state in nfa:
            combined_nfa.append(state)
        combined_nfa[0][0].append(current_nfa_starting_state)
        current_nfa_starting_state += len(nfa)
        offset += len(nfa)
        accepting_states[len(combined_nfa) - 1] = pair[0]

    return combined_nfa, accepting_states


if __name__ == "__main__":
    token_list_1 = tokenize_regex('a')
    token_list_2 = tokenize_regex('b')
    root_1 = parse(token_list_1)
    root_2 = parse(token_list_2)
    mat_1 = regex_to_nfa(root_1)
    print_matrix(mat_1)
    mat_2 = regex_to_nfa(root_2)
    print_matrix(mat_2)
    (mat, acc_states) = combine_nfas([mat_1, mat_2])
    print(mat)
    print(acc_states)
    #visualize_graph(mat)
