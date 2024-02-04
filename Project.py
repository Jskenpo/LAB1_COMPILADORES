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

    elif nodo.valor == '*':
        for i in nodo.UltimaPos:
            pos_node = obtener_nodo_por_id(ast, i)
            pos_node.follows |= nodo.PrimeraPos

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



nombre_archivo = 'expresion_cadena.txt'
expresion, cadena = leer_expresion_y_cadena(nombre_archivo)
print('La expresión regular es:', expresion)
expresion = convertFirst(expresion)
infix,alfabeto = convertir_expresion(expresion)
explicit = implicit_to_explicit(infix)
print('La expresión regular en notación infix es:', explicit)
postfix = infix_postfix(explicit)
ast = construir_AST(postfix)
calcular_nulabilidad(ast)
nulables = obtener_nulables(ast)
obtener_primera_pos(ast)
obtener_ultima_pos(ast)
calcular_followpos(ast)
dot = dibujar_AST(ast)
dot.render('ast', format='png', view=True)
print('La expresión regular en notación postfix es:', postfix)
afn = postfix_afn(postfix)
graficar_afn(afn)
afd = afn_to_afd(afn, alfabeto)
estado_labels = label_estados(afd.estados)
graficar_afd(afd).render('afd_graph', view=True)
afd_min = minimizar_afd(afd)
graficar_afd(afd_min).render('afd_minimizado_graph', view=True)
print('el resultado de la simulación del afn  es:',simulacion_afn(cadena, afn))
print('el resultado de la simulación del afd  es:',simulacion_afd(afd, cadena))
print('El resultado de la simulación del AFD minimizado es:', simulacion_afd_minimizado(afd_min, cadena))

