import os
import time
import sys

# Define códigos de cores ANSI para personalização do terminal
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    FIM = '\033[0m'  # Reseta a cor para o padrão

def limpar_tela():
    """Limpa o terminal, compatível com Windows, Linux e macOS."""
    os.system('cls' if os.name == 'nt' else 'clear')

def aguardar(segundos=2):
    """Pausa a execução por um determinado número de segundos."""
    time.sleep(segundos)

def exibir_cabecalho(titulo):
    """Exibe um cabeçalho formatado para as seções do menu."""
    limpar_tela()
    print("=" * 30)
    print(f"\n--- {titulo} ---")
    print("=" * 30)

def print_sucesso(mensagem):
    """Imprime uma mensagem de sucesso em verde."""
    print(f"{Cores.VERDE}✅ {mensagem}{Cores.FIM}")

def print_erro(mensagem):
    """Imprime uma mensagem de erro em vermelho."""
    print(f"{Cores.VERMELHO}❌ {mensagem}{Cores.FIM}")

def print_aviso(mensagem):
    """Imprime uma mensagem de aviso em amarelo."""
    print(f"{Cores.AMARELO}⚠️ {mensagem}{Cores.FIM}")

def entrada_personalizada(prompt):
    """Solicita uma entrada do usuário com uma cor amarela."""
    return input(f"{Cores.AMARELO}{prompt}{Cores.FIM}")