import os
import sqlite3 as sql
import bcrypt as bc
import jwt
import database
import re
import time
import a2f

# ---------------------------------------------------------------------------
# Inicialização e configuração
# ---------------------------------------------------------------------------

database.inicializar_banco()
JWT_SECRET = os.getenv("JWT_SECRET", "chave_insegura_trocar_isto")

email_regex = re.compile(r"^[A-Za-z]+\.{1}[A-Za-z]+@ufrpe\.br$")
senha_minima = 8
senha_caracteres_proibidos = set(' \'"`;')

# ---------------------------------------------------------------------------
# Funções utilitárias
# ---------------------------------------------------------------------------

def gerar_token(email, tipo_usuario):
    """Cria um token JWT"""
    payload = {"email": email, "tipo_usuario": tipo_usuario}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def validar_email(email: str) -> bool:
    return bool(email_regex.fullmatch(email.strip()))

def validar_senha(senha: str) -> bool:
    if len(senha) < senha_minima:
        print(f"Erro: A senha deve ter no mínimo {senha_minima} caracteres.")
        return False
    if any(c in senha_caracteres_proibidos for c in senha):
        print("Erro: A senha contém caracteres proibidos.")
        return False
    if not any(c.isalpha() for c in senha):
        print("Erro: A senha deve conter pelo menos uma letra.")
        return False
    if not any(c.isdigit() for c in senha):
        print("Erro: A senha deve conter pelo menos um número.")
        return False
    return True

# ---------------------------------------------------------------------------
# Cadastro com verificação 2FA
# ---------------------------------------------------------------------------

def registrar_usuario():
    print("\n--- Cadastro de Novo Usuário ---")
    nome = input("Nome completo: ")

    while True:
        email = input("Email (fulano.sobrenome@ufrpe.br): ")
        if validar_email(email):
            break
        print("Formato de email inválido.")

    while True:
        senha = input("Senha: ")
        if validar_senha(senha):
            break

    while True:
        tipo_usuario = input("Você é 'passageiro' ou 'motorista'? ").lower()
        if tipo_usuario in ['passageiro', 'motorista']:
            break
        print("Opção inválida.")

    # Envio e verificação do código 2FA
    codigo = a2f.gerar_codigo()
    a2f.enviar_codigo_email(email, codigo)
    expira_em = time.time() + 300

    if not a2f.verificar_codigo(codigo, expira_em):
        print("Cadastro cancelado.")
        return False

    senha_bytes = senha.encode('utf-8')
    hash_senha = bc.hashpw(senha_bytes, bc.gensalt())

    try:
        banco = sql.connect('pegai.db')
        cursor = banco.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario) VALUES (?, ?, ?, ?)",
            (nome, email, hash_senha.decode('utf-8'), tipo_usuario)
        )
        banco.commit()
        print("🎉 Usuário cadastrado com sucesso!")
    except sql.IntegrityError:
        print("Erro: Este e-mail já está cadastrado.")
    finally:
        banco.close()

# ---------------------------------------------------------------------------
# Login com verificação 2FA
# ---------------------------------------------------------------------------

def login_usuario():
    print("\n--- Login ---")
    email = input("Email: ")
    senha = input("Senha: ")

    banco = sql.connect('pegai.db')
    cursor = banco.cursor()
    cursor.execute("SELECT senha_hash, tipo_usuario FROM usuarios WHERE email = ?", (email,))
    resultado = cursor.fetchone()
    banco.close()

    if not resultado:
        print("Email não encontrado.")
        return False

    senha_hash_armazenada, tipo_usuario = resultado
    if not bc.checkpw(senha.encode('utf-8'), senha_hash_armazenada.encode('utf-8')):
        print("Senha incorreta.")
        return False

    codigo = a2f.gerar_codigo()
    a2f.enviar_codigo_email(email, codigo)
    expira_em = time.time() + 300

    if not a2f.verificar_codigo(codigo, expira_em):
        print("Login cancelado.")
        return False

    token = gerar_token(email, tipo_usuario)
    print("✅ Login bem-sucedido!")
    print(f"Bem-vindo, {tipo_usuario}.")
    print(f"Token JWT: {token}")
    return token

# ---------------------------------------------------------------------------
# Recuperar senha
# ---------------------------------------------------------------------------

def recuperar_senha():
    print("\n--- Recuperação de Senha ---")
    email = input("Digite o e-mail cadastrado: ")

    banco = sql.connect('pegai.db')
    cursor = banco.cursor()
    cursor.execute("SELECT nome FROM usuarios WHERE email = ?", (email,))
    resultado = cursor.fetchone()
    banco.close()

    if not resultado:
        print("Email não encontrado.")
        return False

    codigo = a2f.gerar_codigo()
    a2f.enviar_codigo_email(email, codigo)
    expira_em = time.time() + 300

    if not a2f.verificar_codigo(codigo, expira_em):
        print("Falha na verificação. Operação cancelada.")
        return False

    nova_senha = input("Nova senha: ")
    if not validar_senha(nova_senha):
        print("Senha inválida.")
        return False

    hash_senha = bc.hashpw(nova_senha.encode('utf-8'), bc.gensalt())

    banco = sql.connect('pegai.db')
    cursor = banco.cursor()
    cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE email = ?", (hash_senha.decode('utf-8'), email))
    banco.commit()
    banco.close()

    print("✅ Senha redefinida com sucesso!")
    return True
