import sys
from queue import Queue

#class for encoding the NFA
class NFA:
    def __init__(self, number_of_states, final_states, list_of_transitions, alphabet):
        self.number_of_states = number_of_states
        self.final_states = final_states
        self.transition_table = list_of_transitions
        self.alphabet = alphabet

    def printNFA(self):
        print(str(self.number_of_states) + "\n" + convert_list_to_str(self.final_states))
        for (state, transition) in self.transition_table:
            print("step: " + state + "   transition:   " + transition + "   next_step " + convert_list_to_str(
                self.transition_table[(state, transition)]))

#class for encoding the DFA
class DFA:
    def __init__(self, number_of_states, final_states, transition_dict):
        self.number_of_states = number_of_states
        self.final_states = final_states
        self.transition_table = transition_dict

    def printDFA(self, output_file):
        output_file.write(str(self.number_of_states) + "\n" +
                          convert_list_to_str(self.final_states) + "\n")
        for (state, transition) in self.transition_table:
            output_file.write((str(state) + " " + transition + " " +
                               str(self.transition_table[state, transition])) + "\n")
        output_file.close()

#parser for NFA
def generate_NFA():
    input_file = open(sys.argv[1], "r");
    output_file = open(sys.argv[2], "w");
    number_of_states = input_file.readline().strip()
    transition_table = {} # ('state', tr) -> 'next_state'
    final_states = [] # list of final states
    second_argument = input_file.readline().strip()
    final_states.extend(int(item) for item in second_argument.split())
    alphabet = []
    line = input_file.readline()
    while line:
        line = line.split()
        state = line[0]
        transition = line[1]
        if transition not in alphabet:
            alphabet.append(transition)
        list_of_next_states = [int(line[elements]) for elements in range(2, len(line))]
        transition_table[(state, transition)] = list_of_next_states
        line = input_file.readline()
    return output_file, NFA(int(number_of_states), final_states, transition_table, alphabet)

#concatenate the elements of a list (used for printing)
def convert_list_to_str(list):
    string = ""
    for i in list:
        string += str(i) + " "
    return string

# gets all the possible transitions for a specific state of the NFA
def get_list_of_transitions(current_state, transition_table):
    list_of_transitions = []
    #iterate through the transition table to find all the possible symbols where the FA can run next
    for (state, transition) in transition_table:
        if int(state) == int(current_state):
            list_of_transitions.append((state, transition))
    return list_of_transitions

#the set of epsilon enclosure
def get_list_of_epsilon_closure(nfa):
    epsilon_closure = {}
    #for every state of the NFA use a queue to find all the states where it can get through eps-transitions
    for state in range(0, nfa.number_of_states):
        queue = Queue()
        queue.put([state])
        eps_cls = []
        visited_states = []
        while not queue.empty():
            x = queue.get()
            for item in x:
                if item not in visited_states:
                    visited_states.append(int(item))
                    eps_cls.append(int(item))
                    l = get_list_of_transitions(item, nfa.transition_table)
                    for (s, tr) in l:
                        if (item, 'eps') == (int(s), tr):
                            if nfa.transition_table[(s, tr)] not in visited_states:
                                queue.put(nfa.transition_table[(s, tr)])
        epsilon_closure[state] = eps_cls
    return epsilon_closure


def get_dfa_final_states(dict_of_dfa_states, nfa):
    dfa_final_states = []
    for combined_states in dict_of_dfa_states:
        for i in combined_states:
            if i in nfa.final_states:
                dfa_final_states.append(dict_of_dfa_states[combined_states])
                break
    return dfa_final_states

# get the next state for (current_state, current_symbol) => next_state
def calculate_dfa_next_state(current_state, current_symbol, nfa, eps_cls):
    next_state = []
    queue = Queue()
    for state in current_state:
        l = get_list_of_transitions(state, nfa.transition_table)
        for (s, tr) in l:
            if (int(s), tr) == (state, current_symbol):
                if nfa.transition_table[(s, tr)] not in next_state:
                    for el in nfa.transition_table[(s, tr)]:
                        if el not in next_state:
                            next_state.append(el)
                        for n_s in eps_cls[el]:
                            if n_s not in next_state:
                                next_state.append(n_s)
    return frozenset(next_state)

# build the DFA
def generate_DFA(nfa):
    dict_of_dfa_states = {}
    state_index = 0
    queue = Queue()  # implement BFS for building the DFA
    dfa_transition_table = {}
    eps_cls = get_list_of_epsilon_closure(nfa)
    queue.put(frozenset(eps_cls[0]))
    while queue.empty() != True:
        x = queue.get()  # e un frozenset
        if x not in dict_of_dfa_states.keys():
            dict_of_dfa_states[x] = state_index
            state_index += 1
        for letter in nfa.alphabet:
            if letter != 'eps':
                next_state = calculate_dfa_next_state(x, letter, nfa, eps_cls)  # tot un frozenset
                dfa_transition_table[(x, letter)] = next_state
                if next_state not in dict_of_dfa_states.keys():
                    dict_of_dfa_states[next_state] = state_index
                    state_index += 1
                    queue.put(next_state)

    transition_table = {}
    for (s, t) in dfa_transition_table:
        transition_table[(dict_of_dfa_states[s], t)] = dict_of_dfa_states[dfa_transition_table[(s, t)]]
    dfa_final_states = get_dfa_final_states(dict_of_dfa_states, nfa)
    return DFA(state_index, dfa_final_states, transition_table)

#main function
if __name__ == "__main__":
    output_file, nfa = generate_NFA()
    eps_dict = get_list_of_epsilon_closure(nfa)
    dfa = generate_DFA(nfa)
    dfa.printDFA(output_file)
