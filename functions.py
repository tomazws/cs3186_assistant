from automathon import NFA
from automathon import DFA
import graphviz
import pydot

################################################################################
##                        CUSTOM FUNCTIONS FOR OPENAI                         ##
################################################################################
def removeAutomathonFormat(string):
    return string.replace('[', '').replace(']', '').replace('\'', '').replace(', ', '')

def nfa_to_dfa(dot_script):
    # # Create NFA from dot script
    # nfa = pydot.graph_from_dot_data(dot_script)[0]

    # # Get all edges from NFA
    # edges = nfa.get_edges()

    # # Get all states
    # states = set()
    # for node in nfa.get_nodes():
    #     if node.get_attributes() == {} and '\n' not in node.get_name():
    #         states.add(node.get_name())

    # # Get final states
    # finals = set()
    # dot_script_lines = dot_script.splitlines()
    # for line in dot_script_lines:
    #     if 'doublecircle' in line:
    #         nodes = line.split(';')[1].strip().split(' ')
    #         for node in nodes:
    #             finals.add(node)

    # # Get initial state
    # initial_state = ''
    # for i in range(len(edges)):
    #     if edges[i].get_source() == 'start':
    #         initial_state = edges[i].get_destination()
    #         edges.pop(i)
    #         break

    # # Get all sigma and delta
    # sigma = set()
    # delta = dict()
    # for edge in edges:
    #     if edge.get_source() not in delta:
    #         delta[edge.get_source()] = dict()
    #     labels = edge.get_label().split(',')
    #     for label in labels:
    #         label = label.replace('"', '').strip()
    #         if label == 'λ':
    #             label = ''
    #         if label not in delta[edge.get_source()]:
    #             delta[edge.get_source()][label] = set()
    #         delta[edge.get_source()][label].add(edge.get_destination())
    #         if label not in sigma:
    #             sigma.add(label)

    # # Create NFA object and convert to DFA
    # automathonNFA = NFA(states, sigma, delta, initial_state, finals)
    # automathonDFA = automathonNFA.get_dfa()

    # # Parse DFA objects to convert to dot script
    # states = {removeAutomathonFormat(state) for state in automathonDFA.q}
    # final_states = {removeAutomathonFormat(final_state) for final_state in automathonDFA.f}
    # states = states - final_states

    # edges = ''
    # for source, delta in automathonDFA.delta.items():
    #     for label, destination in delta.items():
    #         edges += f'{removeAutomathonFormat(source)} -> {removeAutomathonFormat(destination)} [label = "{label}"];\n'

    # dot_script = f'''
    # digraph DFA {{
    #     rankdir=LR;
    #     node [shape = circle]; {' '.join(states)};
    #     node [shape = doublecircle]; {' '.join(final_states)};
    #     start [shape = none, label=""];
    #     start -> {removeAutomathonFormat(automathonDFA.initial_state)};
    #     {edges}
    # }}
    # '''

    return dot_script