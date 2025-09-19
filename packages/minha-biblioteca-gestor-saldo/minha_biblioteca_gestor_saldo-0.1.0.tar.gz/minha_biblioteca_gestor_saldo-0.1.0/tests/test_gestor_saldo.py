from minha_biblioteca_gestor_saldo import gestor_saldo as gs

def test_criar_gestor_saldo():
    depositar, levantar = gs.criar_gestor_saldo(100)
    
    # Testar depósito
    depositar(50)  # Saldo deve ser 150
    levantar(30)   # Saldo deve ser 120
    levantar(200)  # Saldo insuficiente, saldo deve permanecer 120
    depositar(80)  # Saldo deve ser 200
    levantar(100)  # Saldo deve ser 100

    # Não há retorno para verificar diretamente, mas podemos observar os prints
    # Para testes mais robustos, seria ideal modificar a função para retornar o saldo atual

