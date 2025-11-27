import unittest
import sqlite3
import os
from unittest.mock import patch, MagicMock

# Importa as classes do projeto
from database import BancoDeDados
from auth import ControladorAutenticacao
from rotas import ControladorMotorista
from passageiro import ControladorPassageiro

class TestPegai(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Configura o ambiente antes de todos os testes."""
        cls.db_name = "pegai_test.db"
        # Limpeza inicial para garantir um estado limpo
        if os.path.exists(cls.db_name):
            os.remove(cls.db_name)
        
        # Inicializa o banco de teste (Cria as tabelas)
        cls.db = BancoDeDados(cls.db_name)
        cls.db.inicializar()

    @classmethod
    def tearDownClass(cls):
        """Limpa o ambiente após os testes."""
        if os.path.exists(cls.db_name):
            os.remove(cls.db_name)

    def setUp(self):
        """Configuração executada antes de CADA teste individual."""
        self.auth = ControladorAutenticacao()
        # Força a instância do controlador a usar o banco de teste
        self.auth.db = BancoDeDados(self.db_name)
        
        # --- CORREÇÃO DEFINITIVA DO PATCH ---
        # Intercepta a classe BancoDeDados DENTRO do módulo auth.py.
        # Isso garante que quando auth.py fizer "db = BancoDeDados()", 
        # ele receba uma instância conectada ao 'pegai_test.db'.
        self.patcher_db = patch('auth.BancoDeDados', side_effect=lambda: BancoDeDados(self.db_name))
        self.patcher_db.start()
        
        # Mock do sistema de 2FA para aceitar qualquer código e não enviar email
        self.auth.a2f = MagicMock()
        self.auth.a2f.verificar_codigo.return_value = True
        self.auth.a2f.gerar_codigo.return_value = "123456"

    def tearDown(self):
        """Limpeza pós-teste."""
        # Para o patch para não afetar outros processos
        self.patcher_db.stop()

    # --- TESTES DE AUTENTICAÇÃO ---

    @patch('util.Interface.input_personalizado')
    @patch('util.Interface.limpar_tela') 
    @patch('util.Interface.aguardar')    
    def test_01_registrar_passageiro(self, mock_aguardar, mock_limpar, mock_input):
        """Testa o registro de um passageiro comum."""
        mock_input.side_effect = [
            "Passageiro Teste", 
            "passageiro.teste@ufrpe.br", 
            "senha123", 
            "senha123", 
            "n" 
        ]
        
        self.auth.registrar()

        with self.auth.db.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nome, eh_motorista FROM usuarios WHERE email='passageiro.teste@ufrpe.br'")
            user = cursor.fetchone()
        
        self.assertIsNotNone(user, "Erro: Passageiro não foi criado no banco de teste.")
        self.assertEqual(user[0], "Passageiro Teste")
        self.assertEqual(user[1], 0)

    @patch('util.Interface.input_personalizado')
    @patch('util.Interface.limpar_tela')
    @patch('util.Interface.aguardar')
    def test_02_registrar_motorista(self, mock_aguardar, mock_limpar, mock_input):
        """Testa o registro de um motorista com veículo."""
        # Nota: O patch do BancoDeDados já está aplicado via setUp()

        mock_input.side_effect = [
            "Motorista Teste", 
            "motorista.teste@ufrpe.br", 
            "senha123", 
            "senha123", 
            "s",
            "ABC1D23",
            "Fusca",
            "Azul"
        ]
        
        self.auth.registrar()

        with self.auth.db.conectar() as conn:
            cursor = conn.cursor()
            # Verifica Motorista
            cursor.execute("SELECT id, eh_motorista FROM usuarios WHERE email='motorista.teste@ufrpe.br'")
            user = cursor.fetchone()
            self.assertIsNotNone(user, "Erro: Motorista não encontrado no banco de teste.")
            
            # Verifica Veículo
            cursor.execute("SELECT modelo, placa FROM veiculos WHERE motorista_id=?", (user[0],))
            veiculo = cursor.fetchone()

        self.assertEqual(user[1], 1, "Flag eh_motorista incorreta.")
        self.assertIsNotNone(veiculo, "Erro: Veículo não salvo. O patch do DB falhou.")
        self.assertEqual(veiculo[0], "Fusca")
        self.assertEqual(veiculo[1], "ABC1D23")

    @patch('util.Interface.print_sucesso')
    @patch('util.Interface.input_personalizado')
    @patch('util.Interface.limpar_tela')
    @patch('util.Interface.aguardar')
    def test_03_login_sucesso(self, mock_aguardar, mock_limpar, mock_input, mock_print):
        """Testa o login com credenciais corretas."""
        mock_input.side_effect = ["passageiro.teste@ufrpe.br", "senha123"]
        
        # Mock para evitar entrar no loop do menu
        with patch('passageiro.ControladorPassageiro.menu', return_value=True): 
             self.auth.login()
        
        calls = [str(c) for c in mock_print.mock_calls]
        msg_encontrada = any("Bem-vindo" in c or "Logado" in c for c in calls)
        self.assertTrue(msg_encontrada, f"Login falhou ou mensagem mudou. Output: {calls}")

    # --- TESTES DE MOTORISTA ---

    @patch('util.Interface.input_personalizado')
    @patch('util.Interface.limpar_tela')
    @patch('util.Interface.aguardar')
    def test_04_cadastrar_rota(self, mock_aguardar, mock_limpar, mock_input):
        """Testa o cadastro de uma rota pelo motorista."""
        # Recupera o ID do motorista criado no test_02
        with self.auth.db.conectar() as conn:
            res = conn.execute("SELECT id FROM usuarios WHERE email='motorista.teste@ufrpe.br'").fetchone()
            if not res:
                self.fail("Motorista do teste 02 não encontrado no teste 04. Ordem de execução ou persistência falhou.")
            uid = res[0]
        
        ctrl_moto = ControladorMotorista(uid)
        ctrl_moto.db = self.auth.db # Injeta o banco de teste

        mock_input.side_effect = ["UFRPE", "Boa Viagem", "13:00", "seg", "3"]
        
        ctrl_moto.cadastrar_rota()

        with self.auth.db.conectar() as conn:
            rota = conn.execute("SELECT origem, destino, motorista_id FROM rotas WHERE motorista_id=?", (uid,)).fetchone()
        
        self.assertIsNotNone(rota, "Erro: Rota não foi cadastrada no banco.")
        self.assertEqual(rota[0], "UFRPE")
        self.assertEqual(rota[1], "Boa Viagem")
        self.assertEqual(rota[2], uid)

    # --- TESTES DE PASSAGEIRO ---

    @patch('builtins.print') 
    @patch('util.Interface.input_personalizado')
    @patch('util.Interface.limpar_tela')
    @patch('util.Interface.aguardar')
    def test_05_buscar_rotas(self, mock_aguardar, mock_limpar, mock_input, mock_print):
        """Testa se o passageiro consegue ver a rota cadastrada."""
        
        # 1. Recupera o Passageiro e verifica integridade dos dados
        with self.auth.db.conectar() as conn:
            res = conn.execute("SELECT id, nome, email, eh_motorista FROM usuarios WHERE email='passageiro.teste@ufrpe.br'").fetchone()
            from models import Usuario
            usuario_logado = Usuario(res[0], res[1], res[2], res[3])

            # Verificação de segurança para debug
            rotas = conn.execute("SELECT * FROM rotas").fetchall()
            veiculos = conn.execute("SELECT * FROM veiculos").fetchall()
            if not rotas or not veiculos:
                self.fail(f"DB incompleto. Rotas: {len(rotas)}, Veículos: {len(veiculos)}. O patch falhou em persistir os dados.")

        ctrl_pass = ControladorPassageiro(usuario_logado)
        ctrl_pass.db = self.auth.db # Injeta o banco de teste

        mock_input.side_effect = ["voltar"]
        
        ctrl_pass.buscar_rotas()

        output = [str(call) for call in mock_print.mock_calls]
        output_str = " ".join(output)
        
        # Verifica se o output contém os dados esperados do JOIN (Rota + Veículo)
        self.assertIn("Boa Viagem", output_str, "Erro: O destino 'Boa Viagem' não apareceu na lista.")
        self.assertIn("Fusca", output_str, "Erro: O veículo 'Fusca' não apareceu na lista.")

if __name__ == '__main__':
    unittest.main()