from minha_biblioteca_pitagoras import teorema_pitagoras as fm

def test_calcular_hipotenusa():
    assert fm.calcular_hipotenusa(3, 4) == 5
    assert fm.calcular_hipotenusa(5, 12) == 13
    assert fm.calcular_hipotenusa(8, 15) == 17
    assert fm.calcular_hipotenusa(7, 24) == 25
