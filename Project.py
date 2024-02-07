''' 
Universidad del Valle de Guatemala
Facultad de Ingeniería
Ingeniería en Ciencia de la Computación y Tecnologías de la Información


Autores:
    Jose Santisteban 21553
'''

import graphviz
from graphviz import Digraph
from prepare import *
from AST import *
from Automatas import *


def calcular_followpos(nodo):

    if nodo is None:
        return

    if nodo.valor == '.':
        for i in nodo.izquierda.UltimaPos:
            nodo_izquierda = obtener_nodo_por_id(ast, i)
            nodo_izquierda.follows |= nodo.derecha.PrimeraPos
            nodo_izquierda.NodosF |= nodo.derecha.NodosPP

    elif nodo.valor == '*':
        for i in nodo.UltimaPos:
            pos_node = obtener_nodo_por_id(ast, i)
            pos_node.follows |= nodo.PrimeraPos
            pos_node.NodosF |= nodo.NodosPP

    calcular_followpos(nodo.izquierda)
    calcular_followpos(nodo.derecha)

def obtener_nodo_por_id(nodo, id):
    if nodo is None:
        return None

    if nodo.id == id:
        return nodo

    nodo_izquierda = obtener_nodo_por_id(nodo.izquierda, id)
    if nodo_izquierda is not None:
        return nodo_izquierda

    nodo_derecha = obtener_nodo_por_id(nodo.derecha, id)
    if nodo_derecha is not None:
        return nodo_derecha

    return None

def leer_expresion_y_cadena(nombre_archivo):
    with open(nombre_archivo, 'r') as archivo:
        lineas = archivo.readlines()
        expresion = lineas[0].strip()
        cadena = lineas[1].strip()
    return expresion, cadena


'''
PREPROCESAMIENTO DE LA EXPRESIÓN REGULAR
'''

nombre_archivo = 'expresion_cadena.txt'
expresion, cadena = leer_expresion_y_cadena(nombre_archivo)
print('La expresión regular es:', expresion)
expresion = convertFirst(expresion)
infix,alfabeto = convertir_expresion(expresion)
explicit = implicit_to_explicit(infix)
print('La expresión regular en notación infix es:', explicit)
postfix = infix_postfix(explicit)

'''
CONSTRUCIÓN DE ARBOL SINTÁCTICO ABSTRACTO, NULABILIDAD DE NODOS, PRIMERA POS, ÚLTIMA POS Y FOLLOWPOS
'''

ast = construir_AST(postfix)
calcular_nulabilidad(ast)
nulables = obtener_nulables(ast)
obtener_primera_pos(ast)
obtener_ultima_pos(ast)
calcular_followpos(ast)

dot = dibujar_AST(ast)
dot.render('ast', format='png', view=True)

'''
CONSTRUCCIÓN DE AUTÓMATA FINITO NO DETERMINISTA, AUTÓMATA FINITO DETERMINISTA Y AUTÓMATA FINITO DETERMINISTA MINIMIZADO
'''

print('La expresión regular en notación postfix es:', postfix)
'''
afn = postfix_afn(postfix)
graficar_afn(afn)
afd = afn_to_afd(afn, alfabeto)
estado_labels = label_estados(afd.estados)
graficar_afd(afd).render('afd_graph', view=True)
afd_min = minimizar_afd(afd)
graficar_afd(afd_min).render('afd_minimizado_graph', view=True)

lista_nodos = recorrer_ast(ast)
print(lista_nodos)
'''
afd_directo = direct_afd(ast,alfabeto)
imprimir_afd(afd_directo)


'''
SIMULACIÓN DE AUTÓMATAS


print('el resultado de la simulación del afn  es:',simulacion_afn(cadena, afn))
print('el resultado de la simulación del afd  es:',simulacion_afd(afd, cadena))
print('El resultado de la simulación del AFD minimizado es:', simulacion_afd_minimizado(afd_min, cadena))

'''