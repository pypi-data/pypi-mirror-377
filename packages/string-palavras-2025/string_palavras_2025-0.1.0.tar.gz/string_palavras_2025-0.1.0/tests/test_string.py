from string_utils import contar_vogais, inverter, contar_palavras

def test_contar_vogais():
    assert contar_vogais("A cidade de Lisboa") == 8
    assert contar_vogais("BCDFG") == 0
    assert contar_vogais("") == 0

def test_inverter():
    assert inverter("Lisboa") == "aobsiL"
    assert inverter("abc") == "cba"
    assert inverter("") == ""

def test_contar_palavras():
    assert contar_palavras("Lisboa a capital de Portugal") == 5
    assert contar_palavras("  Muitos   espaços   ") == 2
    assert contar_palavras("") == 0
