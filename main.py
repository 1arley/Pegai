import auth
import database


def menu():
    opcao = ""
    while opcao != '0':
        print("\n--- Pegai ---")
        print("[1] Registrar")
        print("[2] Login")
        print("[3] Esqueci a senha")
        print("[0] Sair")

        opcao = input("Escolha uma número: ")
        if opcao == "1":
            auth.registrar_usuario()
            return
        elif opcao == "2":
            auth.login_usuario()
            return
        elif opcao == "3":
            auth.recuperar_senha()
        elif opcao == "0":
            print("Saindo!")
            return
        else:
            print("\nOpção inválida. Tente novamente.")

if __name__ == '__main__':
    menu()