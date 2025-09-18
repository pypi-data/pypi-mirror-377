def contar_vogais(texto):
    #Conta o nº de vogais na string (maiúsculas e minúsculas).
    vogais = "aeiouAEIOU"
    return sum(1 for letra in texto if letra in vogais)


def inverter(texto):
    #Devolve a string invertida.
    return texto[::-1]


def contar_palavras(texto):
    #Conta o nº de palavras na string, separadas por espaços.
    return len(texto.split())
