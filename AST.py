
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

def construir_AST(exp_postfix):
    stack = []
    exp_postfix = exp_postfix + '#.'
    identificador = 1
    for token in exp_postfix:
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
    
    # Agregar nodo con valor e identificador
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
        return set()

    primera_pos = set()

    if nodo.valor == '.':
        if nodo.izquierda is not None and nodo.derecha is not None:
            if nodo.izquierda.nulable:
                primera_pos |= nodo.izquierda.PrimeraPos | nodo.derecha.PrimeraPos
            else:
                primera_pos |= nodo.izquierda.PrimeraPos

    elif nodo.valor == '|':
        if nodo.izquierda is not None and nodo.derecha is not None:
            primera_pos |= nodo.izquierda.PrimeraPos | nodo.derecha.PrimeraPos

    elif nodo.valor == '*':
        if nodo.izquierda is not None:
            primera_pos |= nodo.izquierda.PrimeraPos

    # Regla para hoja con posición i
    elif nodo.id is not None:
        if nodo.valor != 'E':
            primera_pos.add(nodo.id)

    primera_pos |= obtener_primera_pos(nodo.izquierda)
    primera_pos |= obtener_primera_pos(nodo.derecha)

    nodo.PrimeraPos = primera_pos

    # En nodo concatenacion eliminar la primera pos del hijo de la derecha si el nodo izquierdo no es nulable 
    if nodo.valor == '.' and not nodo.izquierda.nulable:
        nodo.PrimeraPos -= nodo.derecha.PrimeraPos


    return primera_pos

def obtener_ultima_pos(nodo):
    if nodo is None:
        return set()

    ultima_pos = set()

    if nodo.valor == '.':
        if nodo.izquierda is not None and nodo.derecha is not None:
            if nodo.derecha.nulable:
                ultima_pos |= nodo.izquierda.UltimaPos | nodo.derecha.UltimaPos
            else:
                ultima_pos |= nodo.derecha.UltimaPos

    elif nodo.valor == '|':
        if nodo.izquierda is not None and nodo.derecha is not None:
            ultima_pos |= nodo.izquierda.UltimaPos | nodo.derecha.UltimaPos

    elif nodo.valor == '*':
        if nodo.izquierda is not None:
            ultima_pos |= nodo.izquierda.UltimaPos

    # Regla para hoja con posición i
    elif nodo.id is not None:
        if nodo.valor != 'E':
            ultima_pos.add(nodo.id)

    ultima_pos |= obtener_ultima_pos(nodo.izquierda)
    ultima_pos |= obtener_ultima_pos(nodo.derecha)

    nodo.UltimaPos = ultima_pos

     # En nodo concatenacion eliminar la primera pos del hijo de la izquierda  si el nodo derecho  no es nulable 
    if nodo.valor == '.' and not nodo.derecha.nulable:
        nodo.UltimaPos -= nodo.izquierda.UltimaPos
        
    return ultima_pos

