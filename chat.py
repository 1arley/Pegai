from database import BancoDeDados
from util import Interface, Cores

class ControladorChat:
    def __init__(self, usuario_logado):
        self.usuario_id = usuario_logado.id
        self.db = BancoDeDados()

    def enviar_mensagem(self, viagem_id, texto):
        if not texto.strip(): return
        
        try:
            with self.db.conectar() as conn:
                conn.execute(
                    "INSERT INTO mensagens (viagem_id, remetente_id, texto) VALUES (?, ?, ?)",
                    (viagem_id, self.usuario_id, texto)
                )
                conn.commit()
        except Exception as e:
            Interface.print_erro(f"Erro ao enviar: {e}")

    def recuperar_mensagens(self, viagem_id):
        mensagens = []
        query = """
            SELECT u.nome, m.texto, m.data_envio, m.remetente_id
            FROM mensagens m
            JOIN usuarios u ON m.remetente_id = u.id
            WHERE m.viagem_id = ?
            ORDER BY m.data_envio ASC
        """
        with self.db.conectar() as conn:
            dados = conn.execute(query, (viagem_id,)).fetchall()
            for d in dados:
                eh_meu = (d[3] == self.usuario_id)
                # Formata dicionario
                mensagens.append({
                    "nome": "VOCÊ" if eh_meu else d[0],
                    "texto": d[1],
                    "hora": d[2][11:16],
                    "eh_meu": eh_meu
                })
        return mensagens

    def abrir_sala_chat(self, viagem_id, detalhes_rota):
        """Loop principal do chat"""
        while True:
            Interface.limpar_tela()
            print(f"{Cores.AMARELO}--- CHAT: {detalhes_rota} ---{Cores.FIM}")
            print("(Digite sua mensagem ou apenas ENTER para atualizar. Digite 'voltar' para sair)\n")

            msgs = self.recuperar_mensagens(viagem_id)
            
            if not msgs:
                print(f"{Cores.ROSA}   Nenhuma mensagem ainda.{Cores.FIM}")
            else:
                for m in msgs:
                    if m['eh_meu']:
                        print(f"{Cores.VERDE}[{m['hora']}] VOCÊ: {m['texto']}{Cores.FIM}")
                    else:
                        print(f"[{m['hora']}] {m['nome']}: {m['texto']}")
            
            print("-" * 60)
            
            # Input serve tanto para digitar quanto para "pausar" o loop de atualização
            texto = input("Mensagem: ").strip()

            if texto.lower() == 'voltar':
                return
            
            if texto:
                self.enviar_mensagem(viagem_id, texto)