from regex_parser import parse
from regex_lexer import tokenize_regex
from regex_to_nfa import combine_nfas, regex_to_nfa, print_matrix
import copy


# after the creation of a combined NFA, there are two path that could be taken
# we could use the generated NFA and simulate it in order to create a functional lexical analyzer or we could further
# transform the NFA to a DFA and simulate that
# It turns out that the latter choice is faster for generating lexical analyzers [1] as the string processor
# will be executed many times, so the extra time taken for the NFA -> DFA transformation is irrelevant
# the algorithm used for NFA->DFA conversion is "the subset creation algorithm" [2], whose idea is that after reading
# a new input symbol DFA is in the state which corresponds to the set of states that are reachable in the NFA, after
# reading all previous input symbols


# computes every state which is reachable on epsilon transition from the provided set of states
# essentially a DFS algorithm
# states are provided as a list of indexes into the NFA transition matrix
def eps_closure(states, nfa):
    stack = copy.deepcopy(states)
    eps_cl = copy.deepcopy(states)
    while len(stack) > 0:
        # current state
        t = stack.pop()
        t_state = nfa[t]
        # get all of the outgoing states on epsilon transition from the current state
        eps_transition = None
        for in_sym in t_state:
            if in_sym[0] == 'eps':
                eps_transition = in_sym[1:len(in_sym)]
        # since the outgoing states can also have epsilon transitions, push them on the stack to be considered later
        for out_state in eps_transition:
            if out_state not in eps_cl:
                eps_cl.append(out_state)
                stack.append(out_state)
    return eps_cl


# computes every state which is reachable on symbol transition from the provided set of states
def move(states, sym, nfa):
    move_set = []
    for state_index in states:
        nfa_state = nfa[state_index]
        for in_sym in nfa_state:
            if in_sym[0] == sym:
                move_set.append(in_sym[1])
    return move_set


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

    print(eps_closure([4], mat))
    print(move([1], 'a', mat))
