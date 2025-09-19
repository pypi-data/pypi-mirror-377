# Biblioteca com funções para manipulação de strings

def contar_vogais(s):
    #Conta o número de vogais em uma string
    vogais = 'aeiouAEIOU'
    return sum(1 for char in s if char in vogais)

def inverter_string(s):
    #Inverte uma string - Devolve uma string invertida
    return s[::-1]

def contar_palavras(s):
    #Conta o número de palavras em uma string
    return len(s.split())
