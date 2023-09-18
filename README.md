# PROYECTO 1 TEORÍA DE LA COMPUTACIÓN 

## Creacion de Máquinas de estado finito
En este repositorio se puede observar la construcción autómatas finitos no deterministas y deterministas mediante una expresión regular. Asimismso se generan graficas en forma de imágenes para poder visualizar los diferentes autómatas de mejor manera, finalmente se puede probar si una cadena w  pertenece al lenguaje del autómta.

## Consideraciones
El linput que se realiza para la construcción de los autómatas tiene que tener una concatenación explícita, es decir:
<br>
<br>
Si tu expresión regular es -> (b|b)*abb(a|b)*
<br>
Concatenala explícitamente de la siguiente manera -> (b|b)*.a.b.b.(a|b)*
<br>
<br>
De esta manera el programa reconocerá cada carácter por separado para generar las transiciones correctamente

## Autores 
José Pablo Santisteban - 21153
<br>
<br>
Sebastián Solorzano - 21826
<br>
<br>
Manuel Rodas - 21509
