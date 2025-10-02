import sqlite3 as sql
import bcrypt as bc
import jwt

def gerar_token(email, tipo_usuario):
    secret = "sua_chave_secreta"
    payload = {"email": email, "tipo_usuario": tipo_usuario}
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

def registrar_usuario():
    """FUNC PRA CADASTRAR USUARIO"""
    print("\n--- Cadastro de Novo Usuário ---")
    nome = input("Nome completo: ")
    email = input("Email: ")
    senha = input("Senha: ")
    #tipo_usuario = input("Você é 'passageiro' ou 'motorista'? ").lower()
    #TESTANDO WHILE LOOP ->
    
    while tipo_usuario not in ['passageiro', 'motorista']:
        tipo_usuario = input("Você é 'passageiro' ou 'motorista'? ").lower()
        
            if tipo_usuario not in ['passageiro', 'motorista']:
                print("Opção inválida. Por favor, digite 'passageiro' ou 'motorista'.")
        return
    # SENHA PRA BYTE
    senha_bytes = senha.encode('utf-8')
    # HASH DA SENHA
    hash_senha = bc.hashpw(senha_bytes, bc.gensalt())

    try:
        banco = sql.connect('pegai.db')
        cursor = banco.cursor()

        cursor.execute(
            # INSERIR USUARIO NO BANCO COM SENHA HASHEADA
            "INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario) VALUES (?, ?, ?, ?)",
            (nome, email, hash_senha.decode('utf-8'), tipo_usuario)
        )

    except sql.IntegrityError:
        print("Erro: Este email ja está cadastrado.")
    finally:
        banco.close()

def login_usuario():
    """Login do usuário no sistema"""
    print("\n--- Login ---")
    email = input("Email: ")
    senha = input("Senha: ")

    banco = sql.connect('pegai.db')
    cursor = banco.cursor()

    # BUSCA USUARIO PELO EMAIL
    cursor.execute("SELECT senha_hash, tipo_usuario FROM usuarios WHERE email = ?", (email,))
    resultado = cursor.fetchone()

    banco.close()

    tipo_usuario = None
    
    if resultado:
        senha_hash_armazenada = resultado[0].encode('utf-8')
        senha_digitada_bytes = senha.encode('utf-8')
        tipo_usuario = resultado[1]
        # COMPARA A SENHA DIGITADA COM O HASH ARMAZENADO
        if bc.checkpw(senha_digitada_bytes, senha_hash_armazenada):
            global usuario_atual
            usuario_atual = email
            print(f"Login bem sucedido! Bem vindo, {tipo_usuario}.")
            return True
        else:
            print("Email ou senha incorretos.")
        return False # FALHA
        
    def recuperar_senha():
        """Recuperar senha após esquecer ou sla"""
        email = input("Digite o email cadastrado: ")
        banco = sql.connect('pegai.db')
        cursor = banco.cursor()
        cursor.execute("SELECT nome FROM usuarios WHERE email = ?")
        resultado = cursor.fetchone()
        banco.close()
        if resultado = True:
            print("Email encontrado. Redefina sua senha.")
            nova_senha = input("Nova senha: ")
            hash_senha = bc.hashpw(nova_senha.encode('utf-8'), bc.gensalt())
            banco = sql.connect('pegai.db')
            cursor = banco.cursor()
            cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE email = ?", (hash_senha.decode('utf-8'), email))
            banco.commit()
            banco.close()
            print("Senha redefinida com sucesso!")
        else:
            print("Email não encontrado")

