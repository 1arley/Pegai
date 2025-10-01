import sqlite3 as sql
import bcrypt as bc

def registrar_usuario():
    # FUNC PRA CADASTRAR USUARIO
    print("\n--- Cadastro de Novo Usuário ---")
    nome = input("Nome completo: ")
    email = input("Email: ")
    senha = input("Senha: ")
    tipo_usuario = input("Você é 'passageiro' ou 'motorista'? ").lower()

    if tipo_usuario not in ['passageiro', 'motorista']:
        print("Tipo de usuário inválido. Tente novamente.")
        return
    # SENHA PRA BYTE
    senha_bytes = senha.encode('utf-8')
    # HASH DA SENHA
    hash_senha = bc.hashpw(senha_bytes, bc.gensalt())

    try:
        banco = sql.connect('pegai.db')
        cursor = banco.cursor()

        cursor.execute(
            # INSERIR USUARIO NO BANCO COM SENHA HASHEADA
            "INSERT INTO usuarios (nome, email, senha-hash, tipo_usuario) VALUES (?, ?, ?, ?)",
            (nome, email, hash_senha.decode('utf-8'), tipo_usuario)
        )

    except sql.IntegrityError:
        print("Erro: Este email ja está cadastrado.")
    finally:
        banco.close()

