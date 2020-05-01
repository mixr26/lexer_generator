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

# [1] The Dragon Book, 2nd edition, p. 165
# [2] The Dragon Book, 2nd edition, p. 154


# helper function which prints the DFA states and transition table
def print_dfa(dstates, dtran, dfa_acc_states):
    i = 0
    for state in dstates:
        print("State " + str(i))
        print(state)
        print(dtran[i])
        if i in dfa_acc_states:
            print("Accepting")
        print()
        i += 1


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


# return the set of input symbols (excluding epsilon) for which the provided NFA states have outgoing transitions
def compute_possible_in_syms(states, nfa):
    syms = []
    for state_index in states:
        state = nfa[state_index]
        for in_sym in state:
            if in_sym[0] != 'eps' and in_sym[0] not in syms:
                syms.append(in_sym[0])
    return syms


# perform NFA to DFA conversion using the subset creation algorithm
# it requires an NFA transition matrix and a list of (regex pattern, accepting state of the NFA for that pattern) pairs
# as input
# returns the set of new DFA states, DFA transition matrix, and the list of accepting DFA states
def nfa_to_dfa(nfa, pattern_acc_states):
    # list of DFA states
    dstates = [eps_closure([0], nfa)]
    # additional list which contains 'marked' flags for each DFA state
    marked = [False]
    # DFA transition matrix
    dtran = []
    # list of accepting DFA states
    acc_states = []
    while True:
        curr_index = 0
        curr_state = None
        # check whether there are unmarked states in the list
        if marked.count(False) > 0:
            curr_index = marked.index(False)
            curr_state = dstates[curr_index]
            marked[curr_index] = True
        else:
            break

        dtran.append([])
        input_syms = compute_possible_in_syms(curr_state, nfa)
        for sym in input_syms:
            new_state = eps_closure(move(curr_state, sym, nfa), nfa)
            if dstates.count(new_state) == 0:
                dstates.append(new_state)
                marked.append(False)
                # if at least one NFA state from the set of NFA states that represent this DFA state is an accepting
                # state, then this DFA state should be marked as accepting too
                for nfa_state in new_state:
                    if nfa_state in pattern_acc_states.keys() and \
                            not dstates.index(new_state) in acc_states:
                        acc_states.append(dstates.index(new_state))
            dtran[curr_index].append([sym, dstates.index(new_state)])

    return dstates, dtran, acc_states


if __name__ == "__main__":
    token_list_1 = tokenize_regex('a')
    token_list_2 = tokenize_regex('abb')
    root_1 = parse(token_list_1)
    root_2 = parse(token_list_2)
    mat_1 = regex_to_nfa(root_1)
    #print_matrix(mat_1)
    mat_2 = regex_to_nfa(root_2)
    #print_matrix(mat_2)
    mat_3 = [[['a', 0], ['b', 1], ['eps']], [['b', 1], ['eps']]]
    #print_matrix(mat_3)
    pattern_dict = [('pat1', mat_1), ('pat2', mat_2), ('pat3', mat_3)]

    (nfa, pattern_acc_states) = combine_nfas(pattern_dict)
    #print_matrix(nfa)

    (dstates, dtran, dfa_acc_states) = nfa_to_dfa(nfa, pattern_acc_states)
    print_dfa(dstates, dtran, dfa_acc_states)
    print(pattern_acc_states)
    print(dfa_acc_states)
