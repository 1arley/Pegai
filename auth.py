import os
import sqlite3 as sql
import bcrypt as bc
import jwt #Criação de Token
import database #Inicialização do banco com inicializar_banco()
import sys
import re #RegEx

# SQLITE -> BANCO DE DADOS
# BCRYPT -> ENCRIPTAR DADOS (SENHA) EM FORMATO DE HASH PRO CASO DE VAZAMENTO DE DADOS

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

database.inicializar_banco()

def gerar_token(email, tipo_usuario):
    secret = "sua_chave_secreta"
    payload = {"email": email, "tipo_usuario": tipo_usuario}
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

# ------- Configurações de validação -------

email_regex = re.compile(r"^[A-Za-z]+\.{1}[A-Za-z]+@ufrpe\.br$")
"""Email só pode ser escrito no modelo fulano.detal@ufrpe.br"""
# Explicação: exige exatamente um ponto no local-part e domínio ufrpe.br
# Não sei se a ufrpe aceita outro tipo de formato (Meu é assim), se sim, quiser aceitar números/underscores/acentos, muda a classe [A-Za-z] conforme necessário.
senha_minima = 8
senha_caracteres_proibidos = set(' \'"`;')

# ---------------------------------------------------------------------

def validar_email(email: str) -> bool:
    """Retorna bool (True ou False) se o email é ou não no formato declarado acima"""
    return bool(email_regex.fullmatch(email.strip()))

def validar_senha:

def registrar_usuario():
    """FUNC PRA CADASTRAR USUARIO"""
    print("\n--- Cadastro de Novo Usuário ---")
    nome = input("Nome completo: ")
    email = input("Email: ")
    senha = input("Senha: ")
    tipo_usuario = input("Você é 'passageiro' ou 'motorista'? ").lower()
    
    while True:
        if tipo_usuario in ['passageiro', 'motorista']:
            break  # Se a entrada for válida, o loop é interrompido e o código continua.
        else:
            # Se não for válida, mostra o erro e o loop pede a informação novamente.
            print("Opção inválida. Por favor, digite    'passageiro' ou 'motorista'.")
    # SENHA PRA BYTE
    senha_bytes = senha.encode('utf-8')
    # HASH DA SENHA
    hash_senha = bc.hashpw(senha_bytes, bc.gensalt())

    try:
        banco = sql.connect('pegai.db')
        cursor = banco.cursor()

        cursor.execute("INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario) VALUES (?, ?, ?, ?)", (nome, email, hash_senha.decode('utf-8'), tipo_usuario))
        banco.commit() # SALVANDO DADOS ACIMA
    except sql.IntegrityError:
        print("Erro: Este email ja está cadastrado.")
    finally:
        banco.close() # FECHANDO O BD APOS PEGAR INFORMAÇÕES

def login_usuario():
    """Login do usuário no sistema"""
    print("\n--- Login ---")
    email = input("Email: ")
    senha = input("Senha: ")

    banco = sql.connect('pegai.db')
    cursor = banco.cursor()
    # BUSCA USUARIO PELO EMAIL
    cursor.execute("SELECT senha_hash, tipo_usuario FROM usuarios WHERE email = ?", (email,))
    resultado = cursor.fetchone()
    banco.close()
    
    if resultado:
        senha_hash_armazenada = resultado[0].encode('utf-8')
        senha_digitada_bytes = senha.encode('utf-8')
        tipo_usuario = resultado[1]
        # COMPARA A SENHA DIGITADA COM O HASH ARMAZENADO
        if bc.checkpw(senha_digitada_bytes, senha_hash_armazenada):
            global usuario_atual
            usuario_atual = email
            print(f"Login bem sucedido! Bem vindo, {tipo_usuario}.")
            return True
        else:
            print("Email ou senha incorretos.")
            return False 

def recuperar_senha():
    """Recuperar senha após esquecer ou algo assim"""
    email = input("Digite o email cadastrado: ")

    # Verifica se o email existe no banco
    banco = sql.connect('pegai.db')
    cursor = banco.cursor()
    cursor.execute("SELECT nome FROM usuarios WHERE email = ?", (email,))
    resultado = cursor.fetchone()
    banco.close()

    if resultado:  # se encontrou algo
        print("Email encontrado. Redefina sua senha.")
        nova_senha = input("Nova senha: ")

        # Criptografa a senha
        hash_senha = bc.hashpw(nova_senha.encode('utf-8'), bc.gensalt())

        # Atualiza a senha no banco
        banco = sql.connect('pegai.db')
        cursor = banco.cursor()
        cursor.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE email = ?",
            (hash_senha.decode('utf-8'), email)
        )
        banco.commit()
        banco.close()

        print("Senha redefinida com sucesso!")
        return True
    else:
        print("Email não encontrado.")

        