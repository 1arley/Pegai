import sqlite3 as sql

def inicializar_banco():

    #CONECTA AO BANCO DE DADOS
    banco = sql.connect('pegai.db')
    cursor = banco.cursor()

    #CRIA TABELA DE USUARIO
    #GUARDA INFORMACOES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            tipo_usuario TEXT NOT NULL CHECK(tipo_usuario IN ('passageiro', 'motorista'))
        )
    ''')

    banco.commit()
    banco.close()
    print("Banco de dados foi inicializado.")

if __name__ == '__main__':
    inicializar_banco()