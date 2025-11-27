from auth import ControladorAutenticacao
from util import Interface

class PegaiApp:
    def __init__(self):
        self.auth = ControladorAutenticacao()

    def executar(self):
        opcao = ""
        while opcao != '0':
            Interface.exibir_cabecalho("Pegai - Caronas UFRPE")
            print("\n[1] Registrar")
            print("[2] Login")
            print("[3] Esqueci a senha")
            print("[0] Sair\n")
            
            opcao = Interface.input_personalizado("Escolha uma opção: ").strip()
            
            if opcao == "1": self.auth.registrar()
            elif opcao == "2": self.auth.login()
            elif opcao == "3": self.auth.recuperar_senha()
            elif opcao == "0":
                print("Saindo...")
                Interface.aguardar(1)
                Interface.limpar_tela()
            else:
                Interface.print_erro("Opção inválida.")
                Interface.aguardar()

if __name__ == '__main__':
    app = PegaiApp()
    app.executar()