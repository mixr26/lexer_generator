# a class gathering all necessary information about a regex pattern
# with every user defined pattern, we associate a name, a block of code which should execute if the pattern is
# recognized, an NFA transition matrix for this pattern, an accepting state in the combined NFA,
# as well as the list of DFA accepting states which recognize this pattern


class PatternDesc:
    def __init__(self, pat, code, nfa):
        self.name = pat
        self.code = code
        self.nfa = nfa
        self.nfa_acc_state = 0
        self.dfa_acc_states = []

    def __str__(self):
        ret = self.name + '\n' + "NFA acc state: " + str(self.nfa_acc_state) + '\n' + "DFA acc states: "
        for acc_state in self.dfa_acc_states:
            ret += str(acc_state) + ' '
        ret += '\n'
        return ret
