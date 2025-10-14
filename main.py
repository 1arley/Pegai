import auth
import util

def menu():
    opcao = ""
    while opcao != '0':
        util.limpar_tela()
        LARGURA = 30
        print("=" * LARGURA)
        print("Pegai".center(LARGURA))
        print("=" * LARGURA)
        
        # Adiciona um espaço simples para respirar
        print() 
        
        print("[1] Registrar")
        print("[2] Login")
        print("[3] Esqueci a senha")
        print("[0] Sair")

        # Adiciona um espaço antes do prompt de entrada
        print()
        opcao = util.input_personalizado("Escolha uma opção: ").strip()
        
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