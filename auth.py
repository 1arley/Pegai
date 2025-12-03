import sqlite3 as sql
import bcrypt as bc
import re
import time

from database import BancoDeDados
from util import Interface
from a2f import ServicoAutenticacao2FA
from rotas import ControladorMotorista
from passageiro import ControladorPassageiro
from models import Usuario

class ControladorAutenticacao:
    def __init__(self):
        self.db = BancoDeDados()
        self.a2f = ServicoAutenticacao2FA()
        self.db.inicializar() # Garante que tabelas existam

    # --- Métodos Auxiliares ---
        # --- COLA REGEX --- 
        # ^                 : Início da string
        # (?=.*[A-Z])       : Lookahead positivo - verifica se há pelo menos uma letra MAIÚSCULA
        # (?=.*\d)          : Lookahead positivo - verifica se há pelo menos um NÚMERO
        # .{9,}             : Aceita qualquer caractere, desde que tenha 9 ou mais repetições (mais de 8)
        # $                 : Fim da string

    @staticmethod
    def validar_email(email):
        return re.match(r"^[A-Za-z]+\.{1}[A-Za-z]+@ufrpe\.br$", email.strip())
    
    @staticmethod
    def validar_senha(senha):
        erros = []
        
        # Verifica tamanho
        if len(senha) < 8:
            erros.append("ter no mínimo 8 caracteres")
            
        # Verifica letra maiúscula 
        if not re.search(r"[A-Z]", senha):
            erros.append("ter pelo menos uma letra maiúscula")
            
        # Verifica número 
        if not re.search(r"\d", senha):
            erros.append("ter pelo menos um número")
            
        return erros 

    @staticmethod
    def completar_cadastro_motorista(urio_id):
        Interface.exibir_cabecalho("Cadastro de Veículo")
        
        while True:
            placa = Interface.input_personalizado("Placa (ex: ABC1D23): ").strip().upper()
            # Se digitar voltar, retorna False para não deslogar
            if Interface.checar_voltar(placa): return False 

            if not re.match(r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$", placa):
                Interface.print_erro("Placa inválida.")
                continue
            break

        modelo = Interface.input_personalizado("Modelo: ").strip()
        if Interface.checar_voltar(modelo): return False

        cor = Interface.input_personalizado("Cor: ").strip()
        if Interface.checar_voltar(cor): return False
        
        db = BancoDeDados()
        try:
            with db.conectar() as conn:
                # Tenta inserir o veículo
                conn.execute("INSERT INTO veiculos (motorista_id, placa, modelo, cor) VALUES (?, ?, ?, ?)", (urio_id, placa, modelo, cor))
                # Garante que o urio está marcado como motorista
                conn.execute("UPDATE urios SET eh_motorista = 1 WHERE id = ?", (urio_id,))
                conn.commit()
            
            Interface.print_sucesso("Veículo cadastrado com sucesso!")
            return True # Retorna True indicando sucesso
        
        except sql.IntegrityError as e:
            # Tratamento de erro amigável
            erro_str = str(e).lower()
            if "placa" in erro_str or "unique constraint failed: veiculos.placa" in erro_str:
                Interface.print_erro("Erro: Esta placa já está cadastrada no sistema.")
            elif "motorista_id" in erro_str or "unique constraint failed: veiculos.motorista_id" in erro_str:
                Interface.print_erro("Erro: Você já possui um veículo cadastrado.")
            else:
                Interface.print_erro(f"Erro de integridade no banco: {e}")
            return False # Retorna False pois falhou
                
        except Exception as e:
            Interface.print_erro(f"Erro inesperado: {e}")
            return False
        finally:
            Interface.aguardar(3)

    # --- Fluxos Principais ---

    def registrar(self):
        Interface.exibir_cabecalho("Cadastro")
        nome = Interface.input_personalizado("Nome: ").strip()
        if Interface.checar_voltar(nome): return

        email = Interface.input_personalizado("Email (@ufrpe.br): ").strip()
        if Interface.checar_voltar(email): return
        if not self.validar_email(email):
            Interface.print_erro("Email inválido.")
            Interface.aguardar(2); return

        senha = ""
        while True:
            # 1. Pede a senha original
            senha = Interface.input_personalizado("Senha: ")
            if Interface.checar_voltar(senha): return

            # 2. Verifica se a senha cumpre os requisitos (Letra, Número, Tamanho)
            lista_erros = self.validar_senha(senha)
            if lista_erros:
                msg_erro = "Senha inválida. Faltam: " + ", ".join(lista_erros) + "."
                Interface.print_erro(msg_erro)
                continue # Volta para o início do loop (pede a senha de novo)

            # 3. Pede a confirmação
            confirma_senha = Interface.input_personalizado("Confirme a senha: ")
            if Interface.checar_voltar(confirma_senha): return

            # 4. Verifica se são iguais
            if senha == confirma_senha:
                break # Tudo certo! Sai do loop.
            else:
                Interface.print_erro("As senhas não coincidem. Por favor, digite ambas novamente.")
                Interface.aguardar(1)
        
        # 2FA
        cod = self.a2f.gerar_codigo()
        self.a2f.enviar_codigo_email(email, cod)
        if not self.a2f.verificar_codigo(cod, time.time() + 300):
            return

        hash_senha = bc.hashpw(senha.encode('utf-8'), bc.gensalt())

        try:
            with self.db.conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO urios (nome, email, senha_hash) VALUES (?, ?, ?)", (nome, email, hash_senha.decode('utf-8')))
                uid = cursor.lastrowid
                conn.commit()
            Interface.print_sucesso("Cadastrado!")
            
            resp = Interface.input_personalizado("Cadastrar como motorista? (s/n): ").lower()
            if resp == 's': self.completar_cadastro_motorista(uid)
            
        except sql.IntegrityError:
            Interface.print_erro("Email já existe.")
            Interface.aguardar(2)

    def login(self):
        Interface.exibir_cabecalho("Login")
        email = Interface.input_personalizado("Email: ").strip()
        if Interface.checar_voltar(email): return
        senha = Interface.input_personalizado("Senha: ")
        if Interface.checar_voltar(senha): return

        # Busca dados no banco
        res = None
        with self.db.conectar() as conn:
            res = conn.execute("SELECT id, nome, email, senha_hash, eh_motorista FROM urios WHERE email = ?", (email,)).fetchone()

        if not res:
            Interface.print_erro("Urio não encontrado.")
            Interface.aguardar(2); return

        uid, nome, email_db, senha_hash, eh_motorista = res
        
        if not bc.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
            Interface.print_erro("Senha incorreta.")
            Interface.aguardar(2); return

        # 2FA
        cod = self.a2f.gerar_codigo()
        self.a2f.enviar_codigo_email(email, cod)
        if not self.a2f.verificar_codigo(cod, time.time() + 300):
            return
        
        urio_logado = Urio(uid, nome, email_db, eh_motorista)
        Interface.print_sucesso(f"Bem-vindo, {urio_logado.nome}!")
        Interface.aguardar(1)

        # --- LÓGICA DE NAVEGAÇÃO CORRIGIDA --- ps obrigado revisores
        
        if urio_logado.eh_motorista:
            while True:
                Interface.exibir_cabecalho("Escolha o Perfil")
                print("[1] Passageiro")
                print("[2] Motorista")
                
                # Tratamento do input: prompt limpo, input normalizado
                op = Interface.input_personalizado("Opção: ").strip().lower()
                
                deslogar = False # Variável de controle

                if op == '1': 
                    # Captura o retorno: True (sair) ou False (voltar)
                    deslogar = ControladorPassageiro(urio_logado).menu()
                elif op == '2': 
                    deslogar = ControladorMotorista(urio_logado.id).menu() 
                else: 
                    Interface.print_erro("Inválido")
                    Interface.aguardar(1)
                    continue

                # Se o menu retornou True (Deslogar), encerra o login
                if deslogar:
                    return 
                
                # Se deslogar for False (digitou 'voltar'), o loop repete e mostra as opções de perfil
        else:
            # Urio apenas passageiro não tem escolha de perfil, sai direto ao terminar
            ControladorPassageiro(urio_logado).menu()
            return
        
    def recuperar_senha(self):
        Interface.exibir_cabecalho("Recuperação de Senha")
        email = Interface.input_personalizado("Email cadastrado: ").strip()
        if Interface.checar_voltar(email): return

        # 1. Verifica se o email existe antes de pedir código
        with self.db.conectar() as conn:
            exists = conn.execute("SELECT id FROM urios WHERE email = ?", (email,)).fetchone()
        
        if not exists:
            Interface.print_erro("Email não encontrado no sistema.")
            Interface.aguardar(2); return

        # 2. Verificação em Duas Etapas (2FA)
        cod = self.a2f.gerar_codigo()
        self.a2f.enviar_codigo_email(email, cod)
        if not self.a2f.verificar_codigo(cod, time.time() + 300):
            return

        # 3. Definição da Nova Senha (COM VALIDAÇÃO)
        nova_senha = ""
        while True:
            nova_senha = Interface.input_personalizado("Nova senha: ")
            if Interface.checar_voltar(nova_senha): return

            # Valida os requisitos (Maiúscula, Número, Tamanho)
            erros = self.validar_senha(nova_senha)
            if erros:
                msg = "Senha fraca. Faltam: " + ", ".join(erros) + "."
                Interface.print_erro(msg)
                continue # Pede a senha novamente

            confirma = Interface.input_personalizado("Confirme a nova senha: ")
            if Interface.checar_voltar(confirma): return

            if nova_senha == confirma:
                break # Sai do loop se tudo estiver correto
            else:
                Interface.print_erro("As senhas não coincidem. Tente novamente.")
                # Loop reinicia pedindo a senha original

        h_nova = bc.hashpw(nova_senha.encode('utf-8'), bc.gensalt())
        
        try:
            with self.db.conectar() as conn:
                conn.execute("UPDATE usuarios SET senha_hash = ? WHERE email = ?", (h_nova.decode('utf-8'), email))
                conn.commit()
            Interface.print_sucesso("Senha alterada com sucesso!")
        except Exception as e:
            Interface.print_erro(f"Erro ao atualizar senha: {e}")
            
        Interface.aguardar(2)
