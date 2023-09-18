import graphviz
import re


def convert_optional(regex):
    return regex.replace('?', '|E')


def convertir_expresion(expresion):
    lista = list(expresion)
    alfabeto = []
    operandos = ['+','.','*','|','(',')','[',']','{','}','?']

    for i in lista:
        if i not in operandos:
            if i not in alfabeto:
                alfabeto.append(i)

    alfabeto.append('')
    

        
    for i in range(len(lista)):
        if i > 0:
            before = lista[i - 1]
            if lista[i] == '+':
                if before not in ')]}':
                    lista[i - 1] = lista[i - 1] + lista[i - 1] + '*'
                else:
                    almacen = []
                    aperturas = 0
                    for j in range(i - 1, -1, -1):
                        if lista[j] in ')]}':
                            aperturas += 1
                            almacen.append(lista[j])
                        elif lista[j] in '([{':
                            aperturas -= 1
                            almacen.append(lista[j])
                        else:
                            almacen.append(lista[j])
                        if aperturas == 0:
                            break
                    almacen.reverse()
                    lista[i] = ''.join(almacen) + '*'
    if '+' in lista:
        lista.remove('+')
    return ''.join(lista), alfabeto


def shunt(infix):
    
    specials = {'*': 60, '.': 40, '|': 20}

    pofix, stack = "", ""  

    for c in infix:
        
        if c == '(':
            stack = stack + c 

        elif c == ')':
           
            while stack[-1] != '(':  
                pofix = pofix + stack[-1]  
                stack = stack[:-1]  
            stack = stack[:-1]  
        
        elif c in specials:
            while stack and specials.get(c, 0) <= specials.get(stack[-1], 0):
                pofix, stack = pofix + stack[-1], stack[:-1]
            stack = stack + c

        else:
            pofix = pofix + c

    while stack:
        pofix, stack = pofix + stack[-1], stack[:-1]

    return pofix


class state:
    # Note that each variable have been
    # set to none to assign no value to each.
    label, edge1, edge2, id= None, None, None, None


class nfa:
    initial, accept = None, None

    def __init__(self, initial, accept):
        self.initial, self.accept = initial, accept

    def get_all_transitions(self):
        transitions = []
        estados = 0 # Contador de estados
        transiciones = []

        def visit(state):
            nonlocal transitions
            nonlocal estados 
            nonlocal transiciones
            estados += 1
            if state.edge1 is not None:
                transition = (state, state.label, state.edge1)
                transiciones.append((estados,state.label, state.edge1))
                if transition not in transitions:
                    transitions.append(transition)
                    visit(state.edge1)
            if state.edge2 is not None:
                transition = (state, state.label, state.edge2)
                transiciones.append((estados,state.label, state.edge2))
                if transition not in transitions:
                    transitions.append(transition)
                    visit(state.edge2)
        visit(self.initial)
        self.transitions = transitions
        self.transiciones = transiciones
        return transiciones
   

def compile(pofix):
    nfaStack = []

    for c in pofix:
        if c == '*':
            nfa1 = nfaStack.pop()
            initial, accept = state(), state()
            initial.edge1, initial.edge2 = nfa1.initial, accept
            nfa1.accept.edge1, nfa1.accept.edge2 = nfa1.initial, accept
            nfaStack.append(nfa(initial, accept))
        elif c == '.':
            nfa2, nfa1 = nfaStack.pop(), nfaStack.pop()
            nfa1.accept.edge1 = nfa2.initial
            nfaStack.append(nfa(nfa1.initial, nfa2.accept))
        elif c == '|':
            nfa2, nfa1 = nfaStack.pop(), nfaStack.pop()
            initial = state()
            initial.edge1, initial.edge2 = nfa1.initial, nfa2.initial
            accept = state()
            nfa1.accept.edge1, nfa2.accept.edge1 = accept, accept
            nfaStack.append(nfa(initial, accept))
        else:
            accept, initial = state(), state()
            initial.label, initial.edge1 = c, accept
            nfaStack.append(nfa(initial, accept))

    return nfaStack.pop()


def visualize_nfa(nfa):
    dot = graphviz.Digraph(format='png')

    estados = 0  # Contador de estados

    def add_states_edges(node, visited):
        nonlocal estados
        if node in visited:
            return
        visited.add(node)
        estados += 1

        dot.node(str(id(node)), label=f'q{estados}')

        if node.edge1:
            label = node.edge1.label if node.edge1.label else 'ε'
            dot.edge(str(id(node)), str(id(node.edge1)), label=label)
            add_states_edges(node.edge1, visited)
        if node.edge2:
            label = node.edge2.label if node.edge2.label else 'ε'
            dot.edge(str(id(node)), str(id(node.edge2)), label=label)
            add_states_edges(node.edge2, visited)

    add_states_edges(nfa.initial, set())

    dot.render('nfa_graph', view=True)


def followes(state):
    states = set()
    states.add(state)

    if state.label is None:

        if state.edge1 is not None:
            states |= followes(state.edge1)
        
        if state.edge2 is not None:
            states |= followes(state.edge2)

    return states


class DFA:
    def __init__(self):
        self.states = set()
        self.transitions = {}
        self.initial = None
        self.accept = set()


def nfa_to_dfa(nfa, alphabet):
    dfa = DFA()
    initial_state = frozenset(followes(nfa.initial))
    dfa.initial = initial_state
    dfa.states.add(initial_state)

    stack = [initial_state]

    while stack:
        current_state = stack.pop()
        for char in alphabet:
            next_states = set()
            for nfa_state in current_state:
                if nfa_state.label == char:
                    next_states |= followes(nfa_state.edge1)
            next_state = frozenset(next_states)
            if next_state:
                dfa.transitions[(current_state, char)] = next_state
                if next_state not in dfa.states:
                    dfa.states.add(next_state)
                    stack.append(next_state)
    
    for state in dfa.states:
        if nfa.accept in state:
            dfa.accept.add(state)
    
    return dfa


def label_states(states):
    # Crear una lista de letras del alfabeto para asignar a los estados
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    state_labels = {}

    # Asignar una letra a cada estado
    for i, state in enumerate(states):
        if i < len(alphabet):
            state_labels[state] = alphabet[i]
        else:
            # Si se agota el alfabeto, usa números
            state_labels[state] = str(i)

    return state_labels


def draw_dfa(dfa):
    dot = graphviz.Digraph(format='png')
  
    state_labels = label_states(dfa.states)  # Obtener el mapeo de estados a letras
  
    for state in dfa.states:
        label = state_labels[state]
        if state in dfa.accept:
            dot.node(label, shape='doublecircle')
        else:
            dot.node(label)

    initial_label = state_labels[dfa.initial]
    dot.node('initial', shape='none')
    dot.edge('initial', initial_label)

    for (state1, char), state2 in dfa.transitions.items():
        dot.edge(state_labels[state1], state_labels[state2], label=char)

    return dot


def match(string, nfa):
   
    current = set()
    nexts = set()

    current |= followes(nfa.initial)

    for s in string:
        
        for c in current:
            if c.label == s:
                nexts |= followes(c.edge1)
        current = nexts
        nexts = set()
    return (nfa.accept in current)


def match_dfa(dfa, w):

  # Asignar nombres a los estados
  state_labels = label_states(dfa.states)

  # Estado inicial
  current = dfa.initial

  # Simular AFD con la cadena w
  for char in w:
    current = dfa.transitions[(current, char)]

  # Verificar si está en un estado de aceptación
  return current in dfa.accept



# Ejemplo de uso
exp = '(b|b)*.a.b.b.(a|b)*'
#exp = '(a|b)*.a.b.b'
infix = convert_optional(exp)
infix,alfabeto = convertir_expresion(infix)
postfix = shunt(infix)
nfa = compile(postfix)
#visualize_nfa(nfa)
dfa = nfa_to_dfa(nfa, alfabeto)
state_labels = label_states(dfa.states)
#draw_dfa(dfa).render('dfa_graph', view=True)
#print('el resultado de la simulación del afn  es: ',match('bbabba', nfa))
#print('el resultado de la simulación del afd  es: ',match_dfa(dfa, 'bbabba'))