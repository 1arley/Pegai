import sqlite3 as sql

class BancoDeDados:
    def __init__(self, nome_arquivo='pegai.db'):
        self.nome_arquivo = nome_arquivo

    def conectar(self):
        """Retorna uma nova conexão com o banco."""
        return sql.connect(self.nome_arquivo)

    def inicializar(self):
        """Cria tabelas se não existirem."""
        with self.conectar() as banco:
            cursor = banco.cursor()
            
            # Tabela Usuários
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
            
            # Tabela Veículos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS veiculos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    motorista_id INTEGER NOT NULL,
                    placa TEXT NOT NULL UNIQUE,
                    modelo TEXT NOT NULL,
                    cor TEXT NOT NULL,
                    FOREIGN KEY (motorista_id) REFERENCES usuarios (id)
                )
            ''')

            # Tabela Rotas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rotas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    motorista_id INTEGER NOT NULL,
                    origem TEXT NOT NULL,
                    destino TEXT NOT NULL,
                    horario_partida TEXT NOT NULL,
                    dias_semana TEXT NOT NULL,
                    vagas_disponiveis INTEGER NOT NULL,
                    preco REAL NOT NULL DEFAULT 0.0,
                    FOREIGN KEY (motorista_id) REFERENCES usuarios (id)       
                )
            ''')
            # Tabela de Viagens (Pra poder ver o histórico dps)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS viagens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    passageiro_id INTEGER NOT NULL,
                    rota_id INTEGER NOT NULL,
                    data_solicitacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'PENDENTE',
                    FOREIGN KEY (passageiro_id) REFERENCES usuarios (id),
                    FOREIGN KEY (rota_id) REFERENCES rotas (id)
                )
            ''')

            # Tabela de avaliações de perfis
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS avaliacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    viagem_id INTEGER NOT NULL,
                    autor_id INTEGER NOT NULL,  -- Quem avaliou
                    alvo_id INTEGER NOT NULL,   -- Quem foi avaliado
                    nota INTEGER NOT NULL CHECK(nota BETWEEN 1 AND 5),
                    comentario TEXT,
                    FOREIGN KEY (viagem_id) REFERENCES viagens (id),
                    FOREIGN KEY (autor_id) REFERENCES usuarios (id),
                    FOREIGN KEY (alvo_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Migrações seguras (caso colunas não existam)
            try: cursor.execute("ALTER TABLE usuarios ADD COLUMN codigo_2fa TEXT;")
            except sql.OperationalError: pass
            try: cursor.execute("ALTER TABLE usuarios ADD COLUMN expira_em REAL;")
            except sql.OperationalError: pass

            print("Banco de dados inicializado com sucesso.")