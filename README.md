🚗 Pegai

Pegai é um protótipo de aplicativo de transporte em modo console (CLI) desenvolvido em Python. O projeto simula um sistema de caronas exclusivo para estudantes da UFRPE, exigindo autenticação via email institucional (@ufrpe.br) e verificação em duas etapas (2FA) por email para garantir a segurança.

O sistema é dividido em dois perfis principais: Passageiro, que pode buscar rotas, e Motorista, que pode criar e gerenciar suas próprias rotas.

📌 Funcionalidades Principais

Sistema de Autenticação Seguro:

Cadastro de usuário com validação de email (@ufrpe.br).

Login com hashing de senha seguro (usando bcrypt).

Recuperação de senha.

Verificação em Duas Etapas (2FA):

Envio de código de 6 dígitos por email para cadastro, login e recuperação de senha.

Perfis Duplos (Passageiro e Motorista):

Usuários podem se cadastrar como passageiros e, opcionalmente, adicionar um perfil de motorista a qualquer momento.

Módulo Motorista:

Cadastro, visualização e exclusão de rotas.

Cadastro de veículos associados ao motorista (placa, modelo, cor).

Módulo Passageiro:

Busca por rotas disponíveis (excluindo as do próprio usuário).

Solicitação de viagem (placeholder).

Interface de Console (CLI):

Menus interativos e limpos.

Feedback visual colorido para sucesso, erros e avisos.

Banco de Dados:

Persistência de dados locais usando sqlite3 (usuários, veículos, rotas).

📁 Estrutura de Pastas
Pegai/
│
├── main.py         # Ponto de entrada da aplicação, menu principal
├── auth.py         # Lógica de registro, login, 2FA e cadastro de motorista
├── a2f.py          # Funções para gerar e enviar códigos 2FA por email
├── database.py     # Inicialização do banco de dados e tabelas (SQLite)
├── passageiro.py   # Menu e funções do perfil de passageiro
├── rotas.py        # Menu e funções do perfil de motorista
├── util.py         # Funções utilitárias (limpar tela, cores, cabeçalhos)
├── pegai.db        # Banco de dados (criado na primeira execução)
└── README.md       # Este arquivo

🛠️ Bibliotecas usadas:

bcrypt (para hashing de senha)

sqlite3 (para banco de dados)

smtplib (para envio de emails 2FA)

re (para validação de dados, ex: email e placas)

geopy (localização)

os, time, sys (bibliotecas padrão)

🚀 Como Executar

Requisitos:

Python 3.12+

Biblioteca bcrypt, geopy

Instalação das dependências:

Bash

pip install bcrypt
pip install geopy

Executar o projeto:

Bash

python main.py
🕹️ Controles
Teclado: A interação é feita digitando as opções numéricas apresentadas nos menus (ex: 1, 2, 0).

'voltar': Na maioria das telas de entrada de dados, digitar voltar cancela a operação atual e retorna ao menu anterior.

🎯 Objetivo do Projeto
Criar um sistema de caronas funcional e seguro em modo console, focado na comunidade acadêmica da UFRPE. O projeto visa aplicar conceitos de banco de dados, autenticação de usuários, hashing de senhas e interação modularizada em Python.

👨‍💻 Desenvolvedor: 
Arthur Iarley
Luis Gabriel

Projeto Acadêmico.

🧠 Aprendizados
Este projeto permitiu praticar:

Manipulação de banco de dados relacional com sqlite3 (CRUD, chaves estrangeiras).

Implementação de um sistema de autenticação seguro, incluindo hashing de senhas com bcrypt.

Aplicação de verificação em duas etapas (2FA) usando a biblioteca smtplib.

Estruturação de um projeto em módulos com responsabilidades separadas (auth, database, utils).

Criação de uma interface de usuário (CLI) interativa e organizada.

Validação de entradas do usuário com Expressões Regulares (re).
