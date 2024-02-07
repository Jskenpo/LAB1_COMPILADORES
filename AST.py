
# Clase para construir el árbol de sintaxis abstracta
from graphviz import Digraph

class NodoAST:
    def __init__(self, valor, identificador ):
        self.id = identificador
        self.valor = valor
        self.izquierda = None
        self.derecha = None
        self.nulable = False 
        self.PrimeraPos = set()
        self.UltimaPos = set()
        self.follows = set()
        self.NodosPP = set()
        self.NodosUP = set()
        self.NodosF = set()

    def __lt__(self,other):
        return self.id < other.id
        

def construir_AST(exp_postfix):
    stack = []
    exp_postfix = exp_postfix + '#.'
    identificador = 1
    for token in exp_postfix:
        if token in ['.', '|', '*', '+', '?']:
            nodo = NodoAST(token,'null')
        else:
            nodo = NodoAST(token,identificador)
            identificador += 1
        if token in ['.', '|', '*', '+', '?']:
            nodo.derecha = stack.pop()
            if token not in ['*', '+', '?']:
                nodo.izquierda = stack.pop()
        stack.append(nodo)

    if len(stack) != 1:
        raise ValueError("Expresión no válida")

    return stack[0]

def dibujar_AST(nodo, dot=None):
    if dot is None:
        dot = Digraph()
    
    dot.node(str(id(nodo)), f"{nodo.valor}\nNulable:{nodo.nulable} \nID: {nodo.id}\nPP: {nodo.PrimeraPos}\nUP: {nodo.UltimaPos}\n FP: {nodo.follows}")
    if nodo.izquierda is not None:
        dot.node(str(id(nodo.izquierda)), nodo.izquierda.valor)
        dot.edge(str(id(nodo)), str(id(nodo.izquierda)))
        dibujar_AST(nodo.izquierda, dot)
    if nodo.derecha is not None:
        dot.node(str(id(nodo.derecha)), nodo.derecha.valor)
        dot.edge(str(id(nodo)), str(id(nodo.derecha)))
        dibujar_AST(nodo.derecha, dot)
    return dot

def calcular_nulabilidad(nodo):
    if nodo is None:
        return

    calcular_nulabilidad(nodo.izquierda)
    calcular_nulabilidad(nodo.derecha)

    if nodo.valor == 'E':
        nodo.nulable = True
    elif nodo.valor == '.':
        nodo.nulable = nodo.izquierda.nulable and nodo.derecha.nulable
    elif nodo.valor == '|':
        nodo.nulable = nodo.izquierda.nulable or nodo.derecha.nulable
    elif nodo.valor == '*':
        nodo.nulable = True

def obtener_nulables(nodo, nulables=None):
    if nulables is None:
        nulables = []

    if nodo is None:
        return

    obtener_nulables(nodo.izquierda, nulables)
    obtener_nulables(nodo.derecha, nulables)

    if nodo.nulable:
        nulables.append(nodo)

    return nulables

def obtener_primera_pos(nodo):
    if nodo is None:
        return set(), set()

    primera_pos = set()
    nodo_PP = set()

    if nodo.valor == '.':
        if nodo.izquierda is not None and nodo.derecha is not None:
            if nodo.izquierda.nulable:
                primera_pos |= nodo.izquierda.PrimeraPos | nodo.derecha.PrimeraPos
                nodo_PP |= nodo.izquierda.NodosPP | nodo.derecha.NodosPP
            else:
                primera_pos |= nodo.izquierda.PrimeraPos
                nodo_PP |= nodo.izquierda.NodosPP

    elif nodo.valor == '|':
        if nodo.izquierda is not None and nodo.derecha is not None:
            primera_pos |= nodo.izquierda.PrimeraPos | nodo.derecha.PrimeraPos
            nodo_PP |= nodo.izquierda.NodosPP | nodo.derecha.NodosPP

    elif nodo.valor == '*':
        if nodo.izquierda is not None:
            primera_pos |= nodo.izquierda.PrimeraPos
            nodo_PP |= nodo.izquierda.NodosPP

    # Regla para hoja con posición i
    elif nodo.id is not None:
        if nodo.valor != 'E':
            primera_pos.add(nodo.id)
            nodo_PP.add(nodo)  # Agregar nodo a la lista de nodos de PrimeraPos

    primera_pos_new, nodo_PP_new = obtener_primera_pos(nodo.izquierda)
    if primera_pos_new is not None and nodo_PP_new is not None:
        primera_pos |= primera_pos_new
        nodo_PP |= nodo_PP_new

    primera_pos_new, nodo_PP_new = obtener_primera_pos(nodo.derecha)
    if primera_pos_new is not None and nodo_PP_new is not None:
        primera_pos |= primera_pos_new
        nodo_PP |= nodo_PP_new

    nodo.PrimeraPos = primera_pos
    nodo.NodosPP = nodo_PP

    # En nodo concatenacion eliminar la primera pos del hijo de la derecha si el nodo izquierdo no es nulable 
    if nodo.valor == '.' and not nodo.izquierda.nulable:
        nodo.PrimeraPos -= nodo.derecha.PrimeraPos
        nodo.NodosPP -= nodo.derecha.NodosPP

    return primera_pos, nodo_PP

def obtener_ultima_pos(nodo):
    if nodo is None:
        return set(),set()

    ultima_pos = set()
    nodos_UP = set()

    if nodo.valor == '.':
        if nodo.izquierda is not None and nodo.derecha is not None:
            if nodo.derecha.nulable:
                ultima_pos |= nodo.izquierda.UltimaPos | nodo.derecha.UltimaPos
                nodos_UP |= nodo.izquierda.NodosUP | nodo.derecha.NodosUP
            else:
                ultima_pos |= nodo.derecha.UltimaPos
                nodos_UP |= nodo.derecha.NodosUP

    elif nodo.valor == '|':
        if nodo.izquierda is not None and nodo.derecha is not None:
            ultima_pos |= nodo.izquierda.UltimaPos | nodo.derecha.UltimaPos
            nodos_UP |= nodo.izquierda.NodosUP | nodo.derecha.NodosUP

    elif nodo.valor == '*':
        if nodo.izquierda is not None:
            ultima_pos |= nodo.izquierda.UltimaPos
            nodos_UP |= nodo.izquierda.NodosUP

    # Regla para hoja con posición i
    elif nodo.id is not None:
        if nodo.valor != 'E':
            ultima_pos.add(nodo.id)
            nodos_UP.add(nodo)

    ultima_pos_new, nodos_UP_new = obtener_ultima_pos(nodo.izquierda)
    if ultima_pos_new is not None and nodos_UP_new is not None:
        ultima_pos |= ultima_pos_new
        nodos_UP |= nodos_UP_new

    ultima_pos_new, nodos_UP_new = obtener_ultima_pos(nodo.derecha)
    if ultima_pos_new is not None and nodos_UP_new is not None:
        ultima_pos |= ultima_pos_new
        nodos_UP |= nodos_UP_new

    nodo.UltimaPos = ultima_pos
    nodo.NodosUP = nodos_UP

     # En nodo concatenacion eliminar la primera pos del hijo de la izquierda  si el nodo derecho  no es nulable 
    if nodo.valor == '.' and not nodo.derecha.nulable:
        nodo.UltimaPos -= nodo.izquierda.UltimaPos
        nodo.NodosUP -= nodo.izquierda.NodosUP
        
    return ultima_pos, nodos_UP

