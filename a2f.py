import os
import smtplib
import random
import time
from email.message import EmailMessage
import util

# ---------------------------------------------------------------------------
# Configurações
# ---------------------------------------------------------------------------

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "seu.email@ufrpe.br")
EMAIL_SENHA = os.getenv("EMAIL_SENHA", "senha_de_aplicativo_aqui")

# ---------------------------------------------------------------------------
# Geração e envio de códigos
# ---------------------------------------------------------------------------

def gerar_codigo():
    """Gera um código aleatório de 6 dígitos"""
    return str(random.randint(100000, 999999))

def enviar_codigo_email(email, codigo):
    """Envia um código de verificação por e-mail"""
    msg = EmailMessage()
    msg['Subject'] = 'Código de Verificação - Pegai'
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = email
    msg.set_content(
        f"Seu código de verificação é: {codigo}\n"
        f"Este código expira em 5 minutos.\n\n"
        f"Equipe Pegai 🚗"
    )

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_REMETENTE, EMAIL_SENHA)
            smtp.send_message(msg)
        util.print_sucesso("Código de verificação enviado ao e-mail informado.")
    except Exception as e:
        util.print_aviso(f"Erro ao enviar e-mail: {e}")
        util.print_aviso(f"(Para testes, use o código gerado: {codigo})")

def verificar_codigo(codigo_gerado, expira_em):
    """Valida o código digitado pelo usuário"""
    for tentativa in range(3):
        codigo_digitado = util.entrada_personalizada("Digite o código de 6 dígitos enviado ao seu e-mail: ")
        if codigo_digitado == codigo_gerado and time.time() < expira_em:
            util.print_sucesso("Verificação concluída com sucesso!")
            return True
        else:
            util.print_erro("Código incorreto ou expirado. Tente novamente.")
    util.print_erro("Falha na verificação.")
    return False    