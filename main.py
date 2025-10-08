import auth
import util

def menu():
    opcao = ""
    while opcao != '0':
        util.limpar_tela()
        print("\n--- Pegai ---")
        print("[1] Registrar")
        print("[2] Login")
        print("[3] Esqueci a senha")
        print("[0] Sair")

        opcao = util.entrada_personalizada("Escolha uma opção: ")
        if opcao == "1":
            auth.registrar_usuario()
        elif opcao == "2":
            auth.login_usuario()
        elif opcao == "3":
            auth.recuperar_senha()
        elif opcao == "0":
            print("Saindo...")
            util.aguardar(1)
            util.limpar_tela()
            return
        else:
            util.print_erro("Opção inválida. Tente novamente.")
            util.aguardar()

if __name__ == '__main__':
    menu()