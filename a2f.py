import os
import smtplib
import random
import time
from email.message import EmailMessage
from util import Interface

class ServicoAutenticacao2FA:
    def __init__(self):
        self.email_remetente = os.getenv("EMAIL_REMETENTE", "arthur.iarley@ufrpe.br")
        self.email_senha = os.getenv("EMAIL_SENHA", "xcit nwrc tplg ufu") # xcit nwrc tplg ufum

    def gerar_codigo(self):
        return str(random.randint(100000, 999999))

    def enviar_codigo_email(self, email, codigo):
        msg = EmailMessage()
        msg['Subject'] = 'Código de Verificação - Pegai'
        msg['From'] = self.email_remetente
        msg['To'] = email
        msg.set_content(
            f"Seu código de verificação é: {codigo}\n"
            f"Este código expira em 5 minutos.\n\n"
            f"Equipe Pegai"
        )

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(self.email_remetente, self.email_senha)
                smtp.send_message(msg)
            Interface.print_sucesso("Código de verificação enviado ao e-mail informado.")
        except Exception as e:
            Interface.print_aviso(f"Erro ao enviar e-mail: {e}")
            Interface.print_aviso(f"(Modo Teste: código é {codigo})")

    def verificar_codigo(self, codigo_gerado, expira_em):
        for _ in range(3):
            codigo_digitado = Interface.input_personalizado("Digite o código de 6 dígitos: ")
            if codigo_digitado == codigo_gerado and time.time() < expira_em:
                Interface.print_sucesso("Verificação concluída!")
                return True
            else:
                Interface.print_erro("Código incorreto ou expirado.")
        Interface.print_erro("Falha na verificação.")
        return False