from minha_biblioteca_string_utils import string_utils as su

def test_contar_vogais():
    assert su.contar_vogais("hello") == 2
    assert su.contar_vogais("HELLO") == 2
    assert su.contar_vogais("xyz") == 0
    assert su.contar_vogais("") == 0

def test_inverter_string():
    assert su.inverter_string("hello") == "olleh"
    assert su.inverter_string("12345") == "54321"
    assert su.inverter_string("") == ""

def test_contar_palavras():
    assert su.contar_palavras("hello world") == 2
    assert su.contar_palavras("one two three four") == 4
    assert su.contar_palavras("") == 0
    assert su.contar_palavras("singleword") == 1