import os
import sqlite3 as sql
import bcrypt as bc

import database
import re
import time
import a2f
import util  # Importa o módulo util atualizado

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

def validar_nome(nome: str) -> bool:
    return len(nome.strip()) > 0

def validar_email(email: str) -> bool:
    return bool(email_regex.fullmatch(email.strip()))

def validar_senha(senha: str) -> bool:
    if len(senha) < senha_minima:
        util.print_erro(f"A senha deve ter no mínimo {senha_minima} caracteres.")
        util.aguardar()
        return False
    if any(c in senha_caracteres_proibidos for c in senha):
        util.print_erro("A senha contém caracteres proibidos.")
        util.aguardar()
        return False
    if not any(c.isalpha() for c in senha):
        util.print_erro("A senha deve conter pelo menos uma letra.")
        util.aguardar()
        return False
    if not any(c.isdigit() for c in senha):
        util.print_erro("A senha deve conter pelo menos um número.")
        util.aguardar()
        return False
    return True

# ---------------------------------------------------------------------------
# Cadastro com verificação 2FA
# ---------------------------------------------------------------------------

def registrar_usuario():
    util.exibir_cabecalho("Cadastro de Novo Usuário")
    
    while True:
        nome = util.input_personalizado("Nome completo: ")
        if validar_nome(nome):
            break
        util.print_erro("Nome inválido.")
        util.aguardar()

    while True:
        email = util.input_personalizado("Email (fulano.sobrenome@ufrpe.br): ")
        if validar_email(email):
            break
        util.print_erro("Formato de email inválido.")
        util.aguardar()

    while True:
        senha = util.input_personalizado("Senha: ")
        if validar_senha(senha):
            break

    while True:
        tipo_usuario = util.input_personalizado("Você é 'passageiro' ou 'motorista'? ").lower()
        if tipo_usuario in ['passageiro', 'motorista']:
            break
        util.print_erro("Opção inválida.")
        util.aguardar()

    codigo = a2f.gerar_codigo()
    a2f.enviar_codigo_email(email, codigo)
    expira_em = time.time() + 300

    if not a2f.verificar_codigo(codigo, expira_em):
        util.print_erro("Cadastro cancelado.")
        util.aguardar(3)
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
        util.print_sucesso("Usuário cadastrado com sucesso!")
        util.aguardar(3)
    except sql.IntegrityError:
        util.print_erro("Este e-mail já está cadastrado.")
        util.aguardar(3)
    finally:
        banco.close()

# ---------------------------------------------------------------------------
# Login com verificação 2FA
# ---------------------------------------------------------------------------

def login_usuario():
    util.exibir_cabecalho("Login")
    email = util.input_personalizado("Email: ")
    senha = util.input_personalizado("Senha: ")

    banco = sql.connect('pegai.db')
    cursor = banco.cursor()
    cursor.execute("SELECT senha_hash, tipo_usuario FROM usuarios WHERE email = ?", (email,))
    resultado = cursor.fetchone()
    banco.close()

    if not resultado:
        util.print_erro("Email não encontrado.")
        util.aguardar()
        return False

    senha_hash_armazenada, tipo_usuario = resultado
    if not bc.checkpw(senha.encode('utf-8'), senha_hash_armazenada.encode('utf-8')):
        util.print_erro("Senha incorreta.")
        util.aguardar()
        return False

    codigo = a2f.gerar_codigo()
    a2f.enviar_codigo_email(email, codigo)
    expira_em = time.time() + 300

    if not a2f.verificar_codigo(codigo, expira_em):
        util.print_erro("Login cancelado.")
        util.aguardar(3)
        return False
    
    util.print_sucesso("Login realizado com sucesso!")
    util.aguardar(2) # Aguarda 2 segundos para o usuário ler a mensagem
    
    return True # Retorna True para indicar que o login foi bem-sucedido

# ---------------------------------------------------------------------------
# Recuperar senha
# ---------------------------------------------------------------------------

def recuperar_senha():
    util.exibir_cabecalho("Recuperação de Senha")
    email = util.input_personalizado("Digite o e-mail cadastrado: ")

    banco = sql.connect('pegai.db')
    cursor = banco.cursor()
    cursor.execute("SELECT nome FROM usuarios WHERE email = ?", (email,))
    resultado = cursor.fetchone()
    banco.close()

    if not resultado:
        util.print_erro("Email não encontrado.")
        util.aguardar()
        return False

    codigo = a2f.gerar_codigo()
    a2f.enviar_codigo_email(email, codigo)
    expira_em = time.time() + 300

    if not a2f.verificar_codigo(codigo, expira_em):
        util.print_erro("Falha na verificação. Operação cancelada.")
        util.aguardar(3)
        return False

    nova_senha = util.input_personalizado("Nova senha: ")
    if not validar_senha(nova_senha):
        util.print_erro("Senha inválida.")
        util.aguardar()
        return False

    hash_senha = bc.hashpw(nova_senha.encode('utf-8'), bc.gensalt())

    banco = sql.connect('pegai.db')
    cursor = banco.cursor()
    cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE email = ?", (hash_senha.decode('utf-8'), email))
    banco.commit()
    banco.close()

    util.print_sucesso("Senha redefinida com sucesso!")
    util.aguardar(3)
    return True