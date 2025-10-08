import sqlite3 as sql

def inicializar_banco():
    """Cria o banco de dados e a tabela de usuários se não existirem"""
    banco = sql.connect('pegai.db')
    cursor = banco.cursor()

    # Criação da tabela base
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            tipo_usuario TEXT NOT NULL CHECK(tipo_usuario IN ('passageiro', 'motorista'))
        )
    ''')

    # Adiciona colunas extras (caso ainda não existam)
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN codigo_2fa TEXT;")
    except sql.OperationalError:
        pass  # coluna já existe

    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN expira_em REAL;")
    except sql.OperationalError:
        pass  # coluna já existe

    banco.commit()
    banco.close()
    print("Banco de dados inicializado com sucesso.")

if __name__ == '__main__':
    inicializar_banco()
