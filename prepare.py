# Preparación de la expresión regular para el algoritmo de Thompson

def convertFirst(expresion):
    return expresion.replace('?', '|E')

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
                    lista[i - 1] = lista[i - 1] +lista[i - 1] + '*'
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
    
    while '+' in lista:
        lista.remove('+')

    #vueva epxpresion 
    expr = ''.join(lista)

    return expr, alfabeto

def implicit_to_explicit(regex: str) -> str:
    
    new_regex = ''
    for i in range(len(regex) - 1):
        if regex[i] not in ['(', '|', '.'] and regex[i + 1] not in [')', '|', '*', '.']:
            new_regex += regex[i] + '.'  # Agregar concatenación explícita
        else:
            new_regex += regex[i]  # Agregar el caracter normal

    new_regex += regex[-1]  # Agregar el último caracter

    return new_regex

def infix_postfix(infix):
    caracteres_especiales = {'*': 60, '.': 40, '|': 20}
    exp_postfix, stack = "", ""  

    for c in infix:        
        if c == '(':
            stack = stack + c 
        elif c == ')':
            while stack[-1] != '(':  
                exp_postfix = exp_postfix + stack[-1]  
                stack = stack[:-1]  
            stack = stack[:-1]  
        elif c in caracteres_especiales:
            while stack and caracteres_especiales.get(c, 0) <= caracteres_especiales.get(stack[-1], 0):
                exp_postfix, stack = exp_postfix + stack[-1], stack[:-1]
            stack = stack + c
        else:
            exp_postfix = exp_postfix + c

    while stack:
        exp_postfix, stack = exp_postfix + stack[-1], stack[:-1]

    return exp_postfix
