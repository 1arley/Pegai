import sqlite3 as sql

def inicializar_banco():
    """Cria o banco de dados e as tabelas se não existirem"""
    banco = sql.connect('pegai.db')
    cursor = banco.cursor()

    # Criação da tabela de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            eh_motorista BOOLEAN NOT NULL DEFAULT 0,
            perfil_ativo TEXT NOT NULL DEFAULT 'passageiro' 
                CHECK(perfil_ativo IN ('passageiro', 'motorista'))
        )
    ''')
    
    # Tabela para os veículos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            motorista_id INTEGER NOT NULL UNIQUE, -- 1 veículo por motorista por enquanto
            placa TEXT NOT NULL UNIQUE,
            modelo TEXT NOT NULL,
            cor TEXT NOT NULL,
            FOREIGN KEY (motorista_id) REFERENCES usuarios (id)
        )
    ''')

    # Tabela para criação de rotas pelo motorista
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rotas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            motorista_id INTEGER NOT NULL,
            origem TEXT NOT NULL,
            destino TEXT NOT NULL,
            horario_partida TEXT NOT NULL,
            dias_semana TEXT NOT NULL, -- <<-- CORRIGIDO DE 'dias'
            vagas_disponiveis INTEGER NOT NULL, -- <<-- VÍRGULA ADICIONADA AQUI
            FOREIGN KEY (motorista_id) REFERENCES usuarios (id)       
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