from minha_biblioteca import cumprimentar

def test_cumprimentar():
    assert cumprimentar("Marcelo") == "Olá, Marcelo! Bem vindo à UFCD 10794"
    assert cumprimentar("Alice") == "Olá, Alice! Bem vindo à UFCD 10794"
    assert cumprimentar("") == "Olá, ! Bem vindo à UFCD 10794"
    assert cumprimentar("123") == "Olá, 123! Bem vindo à UFCD 10794"
    assert cumprimentar("!@#") == "Olá, !@#! Bem vindo à UFCD 10794"