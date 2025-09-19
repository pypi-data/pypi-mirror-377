"""
Esta biblioteca tem a funcaocriar_gestor_saldo( que devolve as funcoes depositar(valor) e levantar(valor, se houver saldo suficiente).

o utilizador indica o saldo inicial, quantas operacoes quer fazer e, para cada operacao, se é deposito ou levantamento e o valor.

- o saldo deve ser guardado numa variavel nao global
- utilizar funcoes dentro de funcoes
- utilizar palavra-chave nonlocal para modificar o saldo
- iteracao com o utilizador atraves de input().
"""
def criar_gestor_saldo(saldo_inicial):
    saldo = saldo_inicial

    def depositar(valor):
        nonlocal saldo
        saldo += valor
        print(f"Depósito de {valor} realizado. Saldo atual: {saldo}")

    def levantar(valor):
        nonlocal saldo
        if saldo >= valor:
            saldo -= valor
            print(f"Levantamento de {valor} realizado. Saldo atual: {saldo}")
        else:
            print(f"Levantamento de {valor} não realizado. Saldo insuficiente.")

    return depositar, levantar

