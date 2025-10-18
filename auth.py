import os
import sqlite3 as sql
import bcrypt as bc

import database
import re
import time
import a2f
import util
import rotas
import passageiro

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
    return len(nome.strip()) > 3 and len(nome.strip()) < 30 and not any(char.isdigit() for char in nome)

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
    
def checar_voltar(valor: str) -> bool:
    if isinstance(valor, str) and valor.lower().strip() == 'voltar':
        util.print_aviso("Operação cancelada pelo usuário.")
        util.aguardar(1)
        return True
    return False

# ---------------------------------------------------------------------------
# Cadastro de Motorista (Função Auxiliar)
# ---------------------------------------------------------------------------

def completar_cadastro_motorista(usuario_id):
    """Função interna para adicionar dados de motorista e veículo."""
    util.exibir_cabecalho("Cadastro de Motorista - Dados do Veículo")
    
    while True:
        placa = util.input_personalizado("Placa do Veículo (ex: ABC1234): ").strip().upper()
        if not re.match(r"^[A-Z][0-9]{7}$", placa):
            print("Modelo de placa inválido")
        else:
            break
        if util.checar_voltar(placa):
            break

    while True:
        modelo = util.input_personalizado("Modelo do Veículo (ex: Fiat Uno): ").strip()
        if len(modelo) > 30:
            print("Vocẽ excedeu o numero máximo de caracteres.")
        if util.checar_voltar(modelo):
            break
    
    while True:
        cor = util.input_personalizado("Cor do Veículo (ex: Prata): ").strip()
        if len(cor) > 30:
            print("Vocẽ excedeu o numero máximo de caracteres.")
            break
        elif cor.isnumeric():
            print("A cor não pode conter números")
        elif len(cor) <= 0:
            print("A cor nao pode ser vazia")
        if util.checar_voltar(cor):
            break

    try:
        banco = sql.connect('pegai.db')
        cursor = banco.cursor()
        
        # Insere o veículo
        cursor.execute(
            "INSERT INTO veiculos (motorista_id, placa, modelo, cor) VALUES (?, ?, ?, ?)",
            (usuario_id, placa, modelo, cor)
        )
        
        # Atualiza o status do usuário para motorista
        cursor.execute("UPDATE usuarios SET eh_motorista = 1 WHERE id = ?", (usuario_id,))
        
        banco.commit()
        util.print_sucesso("Dados do veículo cadastrados! Você agora é um motorista.")
        
    except sql.IntegrityError:
        util.print_erro("Erro: A placa ou o motorista já possui um veículo cadastrado.")
    except Exception as e:
        util.print_erro(f"Um erro inesperado ocorreu: {e}")
    finally:
        banco.close()
        util.aguardar(2)

# ---------------------------------------------------------------------------
# Cadastro (Fluxo Principal)
# ---------------------------------------------------------------------------

def registrar_usuario():
    util.exibir_cabecalho("Cadastro de Novo Usuário, digite 'voltar' p/ sair.")

    while True:
        nome = util.input_personalizado("Nome completo: ").strip()
        if checar_voltar(nome): return False
        if validar_nome(nome): break
        else:
            util.print_erro("Nome inválido")
            util.aguardar()

    while True:
        email = util.input_personalizado("Email (fulano.sobrenome@ufrpe.br): ").strip()
        if checar_voltar(email): return False
        if validar_email(email): break
        else:
            util.print_erro("Formato de email inválido.")
            util.aguardar()

    while True:
        senha = util.input_personalizado("Senha: ")
        if checar_voltar(senha): return False
        if validar_senha(senha): break

    while True:
        confirma_senha = util.input_personalizado("Confirme a senha: ")
        if checar_voltar(confirma_senha): return False
        if senha == confirma_senha: break
        else:
            util.print_erro("As senhas não coincidem.")
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
    
    usuario_id_criado = None
    try:
        banco = sql.connect('pegai.db')
        cursor = banco.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
            (nome, email, hash_senha.decode('utf-8'))
        )
        usuario_id_criado = cursor.lastrowid
        banco.commit()
        util.print_sucesso("Usuário cadastrado com sucesso!")
        util.aguardar(1)
        
    except sql.IntegrityError:
        util.print_erro("Este e-mail já está cadastrado.")
        util.aguardar(3)
        return False
    except Exception as e:
        util.print_erro(f"Um erro ocorreu: {e}")
        util.aguardar(3)
        return False
    finally:
        banco.close()

    if usuario_id_criado:
        while True:
            resposta = util.input_personalizado("Deseja se cadastrar também como motorista? (s/n): ").lower().strip()
            if checar_voltar(resposta): break
            if resposta == 's':
                completar_cadastro_motorista(usuario_id_criado)
                break
            elif resposta == 'n':
                util.print_aviso("Cadastro finalizado como passageiro.")
                util.aguardar(2)
                break
            else:
                util.print_erro("Opção inválida. Digite 's' ou 'n'.")

# ---------------------------------------------------------------------------
# Login (com seleção de perfil)
# ---------------------------------------------------------------------------

def login_usuario():
    util.exibir_cabecalho("Login de Usuário, digite 'voltar' p/ sair.")
    email = util.input_personalizado("Email: ")
    if checar_voltar(email): return False
    senha = util.input_personalizado("Senha: ")
    if checar_voltar(senha): return False

    banco = sql.connect('pegai.db')
    cursor = banco.cursor()
    cursor.execute("SELECT id, senha_hash, eh_motorista FROM usuarios WHERE email = ?", (email,))
    resultado = cursor.fetchone()
    banco.close()

    if not resultado:
        util.print_erro("Email não encontrado.")
        util.aguardar()
        return False

    usuario_id, senha_hash_armazenada, eh_motorista = resultado
    
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
    util.aguardar(1)
    
    # --- LÓGICA DE SELEÇÃO DE PERFIL ---
    
    if eh_motorista:
        while True:
            util.exibir_cabecalho("Escolha seu modo de acesso")
            print("[1] Entrar como Passageiro")
            print("[2] Entrar como Motorista")
            modo = util.input_personalizado("Opção: ").strip()

            if modo == '1':
                passageiro.menu_passageiro(usuario_id) # <-- ALTERADO
                return True
            elif modo == '2':
                rotas.menu_motorista(usuario_id)
                return True
            else:
                util.print_erro("Opção inválida. Tente novamente.")
                util.aguardar()
    else:
        # Usuário é apenas passageiro
        passageiro.menu_passageiro(usuario_id) # <-- ALTERADO
        return True

# ---------------------------------------------------------------------------
# Recuperar senha
# ---------------------------------------------------------------------------

def recuperar_senha():
    util.exibir_cabecalho("Recuperação de Senha de Usuário, digite 'voltar' p/ sair.")
    email = util.input_personalizado("Digite o e-mail cadastrado: ")
    if checar_voltar(email):
        return False

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
    util.aguardar(2)
    return True
