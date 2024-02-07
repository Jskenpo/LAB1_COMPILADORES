import graphviz
class estado:
    label = None
    transicion1 = None 
    transicion2 = None 
    id = None


class afn:
    inicial, accept = None, None

    def __init__(self, inicial, accept):
        self.inicial, self.accept = inicial, accept

    def get_all_transitions(self):
        transitions = []
        estados = 0 
        transiciones = []

        def visit(estado):
            nonlocal transitions
            nonlocal estados 
            nonlocal transiciones
            estados += 1
            if estado.transicion1 is not None:
                transition = (estado, estado.label, estado.transicion1)
                transiciones.append((estados,estado.label, estado.transicion1))
                if transition not in transitions:
                    transitions.append(transition)
                    visit(estado.transicion1)
            if estado.transicion2 is not None:
                transition = (estado, estado.label, estado.transicion2)
                transiciones.append((estados,estado.label, estado.transicion2))
                if transition not in transitions:
                    transitions.append(transition)
                    visit(estado.transicion2)
        visit(self.inicial)
        self.transitions = transitions
        self.transiciones = transiciones
        return transiciones
   

def postfix_afn(exp_postfix):
    afnstack = []
    epsilon = 'E'

    for c in exp_postfix:
        if c == '*':
            afn1 = afnstack.pop()
            inicial, accept = estado(), estado()
            inicial.transicion1, inicial.transicion2 = afn1.inicial, accept
            afn1.accept.transicion1, afn1.accept.transicion2 = afn1.inicial, accept
            afnstack.append(afn(inicial, accept))
        elif c == '.':
            afn2, afn1 = afnstack.pop(), afnstack.pop()
            afn1.accept.transicion1 = afn2.inicial
            afnstack.append(afn(afn1.inicial, afn2.accept))
        elif c == '|':
            afn2, afn1 = afnstack.pop(), afnstack.pop()
            inicial = estado()
            inicial.transicion1, inicial.transicion2 = afn1.inicial, afn2.inicial
            accept = estado()
            afn1.accept.transicion1, afn2.accept.transicion1 = accept, accept
            afnstack.append(afn(inicial, accept))
        
        elif c == 'E':
            accept, inicial = estado(), estado()
            inicial.transicion1 = accept
            afnstack.append(afn(inicial, accept))
        else:
            accept, inicial = estado(), estado()
            inicial.label, inicial.transicion1 = c, accept
            afnstack.append(afn(inicial, accept))

    return afnstack.pop()


def graficar_afn(afn):
    dot = graphviz.Digraph(format='png')
    estados = 0  

    def add_estados_edges(node, visited):
        nonlocal estados
        if node in visited:
            return
        visited.add(node)
        estados += 1

        dot.node(str(id(node)), label=f'q{estados}')

        if node.transicion1:
            label = node.transicion1.label if node.transicion1.label else 'ε'
            dot.edge(str(id(node)), str(id(node.transicion1)), label=label)
            add_estados_edges(node.transicion1, visited)
        if node.transicion2:
            label = node.transicion2.label if node.transicion2.label else 'ε'
            dot.edge(str(id(node)), str(id(node.transicion2)), label=label)
            add_estados_edges(node.transicion2, visited)

    add_estados_edges(afn.inicial, set())

    dot.render('afn_graph', view=True)


def seguimiento(estado):
    estados = set()
    estados.add(estado)

    if estado.label is None:
        if estado.transicion1 is not None:
            estados |= seguimiento(estado.transicion1)
        if estado.transicion2 is not None:
            estados |= seguimiento(estado.transicion2)
    return estados

class AFD:
    def __init__(self):
        self.estados = set()
        self.transitions = {}
        self.inicial = None
        self.accept = set()

    def agregar_transicion(self, estado_origen, simbolo, estado_destino):
        if estado_origen not in self.transitions:
            self.transitions[estado_origen] = {}
        self.transitions[estado_origen][simbolo] = estado_destino

    def agregar_estado(self, estado):
        # Convertir el conjunto a una tupla antes de agregarlo
        self.estados.add(tuple(sorted(estado)))

    def establecer_estado_inicial(self, estado):
        self.inicial = tuple(sorted(estado))

    def agregar_estado_aceptacion(self, estado):
        self.accept.add(tuple(sorted(estado)))


def afn_to_afd(afn, alphabet):
    afd = AFD()
    estado_inicial = frozenset(seguimiento(afn.inicial))
    afd.inicial = estado_inicial
    afd.estados.add(estado_inicial)
    stack = [estado_inicial]

    while stack:
        actual_estado = stack.pop()
        for char in alphabet:
            next_estados = set()
            for afn_estado in actual_estado:
                if afn_estado.label == char:
                    next_estados |= seguimiento(afn_estado.transicion1)
            next_estado = frozenset(next_estados)
            if next_estado:
                afd.transitions[(actual_estado, char)] = next_estado
                if next_estado not in afd.estados:
                    afd.estados.add(next_estado)
                    stack.append(next_estado)
    
    for estado in afd.estados:
        if afn.accept in estado:
            afd.accept.add(estado)
    
    return afd


def label_estados(estados):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    estado_labels = {}

    for i, estado in enumerate(estados):
        if i < len(alphabet):
            estado_labels[estado] = alphabet[i]
        else:
            estado_labels[estado] = str(i)

    return estado_labels


def graficar_afd(afd):
    dot = graphviz.Digraph(format='png')
    estado_labels = label_estados(afd.estados)  
  
    for estado in afd.estados:
        label = estado_labels[estado]
        if estado in afd.accept:
            dot.node(label, shape='doublecircle')
        else:
            dot.node(label)

    inicial_label = estado_labels[afd.inicial]
    dot.node('inicial', shape='none')
    dot.edge('inicial', inicial_label)

    for (estado1, char), estado2 in afd.transitions.items():
        dot.edge(estado_labels[estado1], estado_labels[estado2], label=char)

    return dot


def minimizar_afd(afd):
    # Get the alphabet symbols from the transitions
    alfabeto = set([symbol for _, symbol in afd.transitions.keys()])

    P = [afd.accept, afd.estados - afd.accept]
    W = [set(y) for y in P]

    while W:
        A = W.pop()
        for c in alfabeto:
            X = set([s for s in afd.estados if afd.transitions.get((s, c)) in A])
            for Y in P:
                if X.intersection(Y) and (Y - X):
                    P.remove(Y)
                    P.extend([Y.intersection(X), Y - X])
                    if Y in W:
                        W.remove(Y)
                        W.extend([Y.intersection(X), Y - X])
                    else:
                        if len(Y.intersection(X)) < len(Y - X):
                            W.append(Y.intersection(X))
                        else:
                            W.append(Y - X)

    minimized_states = [list(y) for y in P]
    minimized_start_state = [s for s in minimized_states if afd.inicial in s][0]
    minimized_accept_states = [s for s in minimized_states if set(s).intersection(afd.accept)]
    minimized_transitions = {}

    for state in minimized_states:
        for c in alfabeto:
            transition = afd.transitions.get((state[0], c))
            if transition:
                for s in minimized_states:
                    if transition in s:
                        minimized_transitions[(str(state), c)] = str(s)

    minimized_afd = AFD()
    minimized_afd.estados = set([str(state) for state in minimized_states])
    minimized_afd.transitions = minimized_transitions
    minimized_afd.inicial = str(minimized_start_state)
    minimized_afd.accept = set([str(s) for s in minimized_accept_states])

    return minimized_afd

def recorrer_ast(nodo, valores_ast=None):
    if valores_ast is None:
        valores_ast = {}

    if nodo is None:
        return valores_ast

    if nodo.follows != set():
        valores_ast[nodo.id] = {
            'PrimeraPos': nodo.PrimeraPos,
            'UltimaPos': nodo.UltimaPos,
            'nulable': nodo.nulable,
            'follows': nodo.follows
        }

    recorrer_ast(nodo.izquierda, valores_ast)
    recorrer_ast(nodo.derecha, valores_ast)

    # Ordenar el diccionario por el id de manera ascendente
    valores_ast = dict(sorted(valores_ast.items(), key=lambda item: item[0]))


    return valores_ast


def direct_afd(root,alfabeto):

    #eliminar del lfabeto la cadena vacia 

    alfabeto.remove('')

    # Obtener s0
    s0 = root.NodosPP
    
    # Crear el AFD
    afd = AFD()
    afd.agregar_estado(root.PrimeraPos)
    afd.establecer_estado_inicial(root.PrimeraPos)
    labels = [root.PrimeraPos]
    # Dstates es una lista de conjuntos de nodos
    Dstates = [s0]
    marked_states = set()  # Conjunto de estados marcados

    # Mientras haya estados no marcados en Dstates
    while Dstates:
        # Obtener un estado no marcado
        T = Dstates.pop()
        L = labels.pop()
        
        # Marcar el estado
        marked_states.add(tuple(sorted(T)))

        for symbol in alfabeto:
            U = set()
            U_labels = set()

            # Calcular la unión de followpos(p) para todas las posiciones p en T
            for node in T:
                if node.valor == symbol:
                    U |= node.NodosF
                    U_labels |= node.follows

            # Si U no está vacío y no está en Dstates ni en marked_states, agregarlo como estado no marcado a Dstates
            if U and tuple(sorted(U)) not in Dstates and tuple(sorted(U)) not in marked_states:
                afd.agregar_estado(U_labels)
                Dstates.append(U)
                labels.append(U_labels)

            # Establecer la transición desde T con el símbolo 'symbol' a U
            afd.agregar_transicion(tuple(sorted(L)), symbol, tuple(sorted(U_labels)))

    # Establecer los estados de aceptación
    for estado in afd.estados:
        for nodo in estado:
            if nodo in root.follows:
                afd.agregar_estado_aceptacion(estado)
                break
    return afd







def simulacion_afn(string, afn):   
    actual = set()
    siguiente = set()
    actual |= seguimiento(afn.inicial)

    for s in string:
        for c in actual:
            if c.label == s:
                siguiente |= seguimiento(c.transicion1)
        actual = siguiente
        siguiente = set()
    return (afn.accept in actual)


def simulacion_afd(afd, w):
    estado_labels = label_estados(afd.estados)
    actual = afd.inicial

    for char in w:
        actual = afd.transitions[(actual, char)]
    
    return actual in afd.accept


def simulacion_afd_minimizado(afd_minimizado, w):
    actual = afd_minimizado.inicial

    for char in w:
        actual = afd_minimizado.transitions.get((actual, char), None)
        if actual is None:
            return False

    return actual in afd_minimizado.accept

def imprimir_afd(afd):
    print("Estados:")
    for estado in afd.estados:
        print(estado)
    
    print("\nTransiciones:")
    for origen, transiciones in afd.transitions.items():
        for simbolo, destino in transiciones.items():
            print(f"Dtran[{origen}, {simbolo}] = {destino}")

    print("\nEstado inicial:")
    print(afd.inicial)

    print("\nEstados de aceptación:")
    for estado in afd.accept:
        print(estado)
