import os
import time

class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    ROSA = '\033[95m'
    FIM = '\033[0m'

class Interface:
    @staticmethod
    def limpar_tela():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def aguardar(segundos=1):
        time.sleep(segundos)

    @staticmethod
    def exibir_cabecalho(titulo):
        Interface.limpar_tela()
        largura = 60
        print("=" * largura)
        print(titulo.center(largura))
        print("=" * largura)

    @staticmethod
    def print_sucesso(mensagem):
        print(f"{Cores.VERDE}✅ {mensagem}{Cores.FIM}")

    @staticmethod
    def print_erro(mensagem):
        print(f"{Cores.VERMELHO}❌ {mensagem}{Cores.FIM}")

    @staticmethod
    def print_aviso(mensagem):
        print(f"{Cores.AMARELO}⚠️ {mensagem}{Cores.FIM}")

    @staticmethod
    def input_personalizado(prompt):
        return input(f"{Cores.ROSA}{prompt}{Cores.FIM}")

    @staticmethod
    def checar_voltar(valor: str) -> bool:
        if isinstance(valor, str) and valor.lower().strip() == 'voltar':
            Interface.print_aviso("Operação cancelada pelo usuário.")
            Interface.aguardar(1)
            return True
        return False