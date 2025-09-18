from biblioteca_calculadora_simples import calculadora_simples as fm

def test_somar():
    assert fm.somar(2, 3) == 5
    assert fm.somar(-1, 1) == 0
    assert fm.somar(0, 0) == 0
    assert fm.somar(-2, -3) == -5

def test_subtrair():
    assert fm.subtrair(5, 3) == 2
    assert fm.subtrair(0, 0) == 0
    assert fm.subtrair(-1, -1) == 0
    assert fm.subtrair(-2, -3) == 1

def test_multiplicar():
    assert fm.multiplicar(2, 3) == 6
    assert fm.multiplicar(-1, 1) == -1
    assert fm.multiplicar(0, 5) == 0
    assert fm.multiplicar(-2, -3) == 6

def test_dividir(): 
    assert fm.dividir(6, 3) == 2
    assert fm.dividir(-6, 3) == -2
    assert fm.dividir(5, 2) == 2.5
    try:
        fm.dividir(5, 0)
        assert False, "Deveria ter levantado ValueError"
    except ValueError as e:
        assert str(e) == "Divisão por zero não é permitida."

# Testes adicionais para cobrir mais casos
def test_somar_float():
    assert fm.somar(2.5, 3.5) == 6.0
    assert fm.somar(-1.5, 1.5) == 0.0

def test_subtrair_float():
    assert fm.subtrair(5.5, 3.5) == 2.0
    assert fm.subtrair(-1.5, -1.5) == 0.0

def test_multiplicar_float():
    assert fm.multiplicar(2.5, 4) == 10.0
    assert fm.multiplicar(-1.5, -2) == 3.0

def test_dividir_float():
    assert fm.dividir(7.5, 2.5) == 3.0
    assert fm.dividir(-7.5, -2.5) == 3.0