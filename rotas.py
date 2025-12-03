import re
from util import Interface
from database import BancoDeDados
from models import Rota  
from mapas import ServicoMapas
from a2f import ServicoAutenticacao2FA

class ControladorMotorista:
    def __init__(self, motorista_id):
        self.motorista_id = motorista_id
        self.db = BancoDeDados()

    def cadastrar_rota(self):
        """
        Núcleo: Cria uma rota.
        """
        Interface.exibir_cabecalho("Cadastro de rotas")
        mapas = ServicoMapas()

        # Origem
        while True:
            origem = Interface.input_personalizado("Ponto de partida: ").strip()
            if Interface.checar_voltar(origem): return
            if len(origem) > 100 or len(origem) == 0:
                Interface.print_erro("Origem inválida.")
                continue
            break

        # Destino
        while True:
            destino = Interface.input_personalizado("Destino: ").strip()
            if Interface.checar_voltar(destino): return
            if len(destino) > 100 or len(destino) == 0:
                Interface.print_erro("Destino inválido.")
                continue
            break

        # Horário
        while True:
            horario = Interface.input_personalizado("Horário (ex: 13:00): ").strip()
            if Interface.checar_voltar(horario): return
            if not re.match(r"^\d{2}:\d{2}$", horario):
                Interface.print_erro("Formato inválido.")
                continue
            break

        # Dias
        dias_validos = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']
        dias_finais = ""
        
        while True:
            # Atualizei o texto do input para dar o exemplo correto
            entrada_dias = Interface.input_personalizado("Dias (ex: seg, qua, sex): ").strip().lower()
            
            if Interface.checar_voltar(entrada_dias): return
            
            if not entrada_dias:
                Interface.print_erro("O campo dias não pode ser vazio.")
                continue

            # 1. Separa por vírgula
            # 2. Remove espaços em branco de cada item
            # 3. Ignora itens vazios (caso o usuário digite "seg, , ter")
            lista_dias_digitados = [d.strip() for d in entrada_dias.split(',') if d.strip()]

            # Validação: Verifica se TODOS os dias digitados estão na lista de válidos
            dias_incorretos = [d for d in lista_dias_digitados if d not in dias_validos]

            if dias_incorretos:
                # Mostra quais dias estão errados
                msg = f"Dia(s) inválido(s): {', '.join(dias_incorretos)}. Use apenas: {', '.join(dias_validos)}."
                Interface.print_erro(msg)
                continue
            
            # Se passou, formata a string bonitinha para salvar no banco (ex: "seg, qua, sex")
            dias_finais = ", ".join(lista_dias_digitados)
            break

        # Vagas
        while True:
            vagas_str = Interface.input_personalizado("Vagas: ").strip()
            if Interface.checar_voltar(vagas_str): return
            if not vagas_str.isdigit():
                Interface.print_erro("Digite um número.")
                continue
            vagas = int(vagas_str)
            if vagas >= 50:
                Interface.print_erro("Isso não é um ônibus.")
                continue
            break

        print("\nCalculando distância e sugerindo preço...")
        
        distancia = mapas.calcular_distancia_km(origem, destino)
        preco_sugerido = 0.0

        if distancia:
            preco_sugerido = mapas.sugerir_preco(distancia)
            Interface.print_sucesso(f"Distância estimada: {distancia} km")
            Interface.print_aviso(f"Preço sugerido pelo app: R$ {preco_sugerido:.2f}")
        else:
            Interface.print_erro("Não foi possível calcular a distância automaticamente.")

        # Preço (Modificado para aceitar sugestão)
        while True:
            prompt = f"Preço da carona (Enter para aceitar R$ {preco_sugerido}): "
            preco_str = Interface.input_personalizado(prompt).strip().replace(',', '.')
            
            if Interface.checar_voltar(preco_str): return
            
            if preco_str == "":
                preco = preco_sugerido # Aceita a sugestão
                break
            
            try:
                preco = float(preco_str)
                if preco < 0 and preco > 100: raise ValueError
                break
            except ValueError:
                Interface.print_erro("Valor inválido.")

        try:
            with self.db.conectar() as conn:
                cursor = conn.cursor()
                # Atualizado query para incluir preco
                cursor.execute(
                    "INSERT INTO rotas (motorista_id, origem, destino, horario_partida, dias_semana, vagas_disponiveis, preco) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (self.motorista_id, origem, destino, horario, dias_finais, vagas, preco)
                )
                conn.commit()
            Interface.print_sucesso(f"Rota cadastrada! Valor: R$ {preco:.2f}")
        except Exception as e:
            Interface.print_erro(f"Erro: {e}")
        finally:
            Interface.aguardar(2)

    def visualizar_minhas_rotas(self, mostrar_ids=False):
        """
        Núcleo: Exibe todas as rotas existentes.
        """
        Interface.exibir_cabecalho("Minhas Rotas")
        
        rotas_objetos = [] # Lista para guardar OBJETOS Rota

        with self.db.conectar() as conn:
            cursor = conn.cursor()
            # Buscamos os dados crus
            cursor.execute("SELECT id, origem, destino, horario_partida, dias_semana, vagas_disponiveis FROM rotas WHERE motorista_id = ?", (self.motorista_id,))
            tuplas = cursor.fetchall()

            # Conversão de Tupla -> Objeto
            for t in tuplas:
                # t[0]=id, t[1]=origem, etc.
                nova_rota = Rota(t[0], t[1], t[2], t[3], t[4], t[5])
                rotas_objetos.append(nova_rota)

        if not rotas_objetos:
            Interface.print_aviso("Nenhuma rota cadastrada.")
            print("=" * 60)
            Interface.input_personalizado("Pressione Enter para voltar...")
            
            if mostrar_ids: return []
        else:
            for i, rota in enumerate(rotas_objetos):
                # AGORA USAMOS ATRIBUTOS (.origem, .destino)
                label = f" (ID: {rota.id})" if mostrar_ids else ""
                print(f"\n--- Rota {i+1}{label} ---")
                print(f"  {rota.origem} -> {rota.destino}")
                print(f"  {rota.horario_partida} ({rota.dias_semana}) | Vagas: {rota.vagas_disponiveis}")

        if not mostrar_ids:
            print("\n")
            
        
        return rotas_objetos # Retorna lista de objetos

    def deletar_rota(self):
        """
        Núcleo: Deleta rota, se ela existir.
        """
        Interface.exibir_cabecalho("Deletar Rota")
        # Recebe objetos Rota
        rotas = self.visualizar_minhas_rotas(mostrar_ids=True)
        if not rotas:
            
            return

        # Cria lista de IDs válidos usando o atributo .id do objeto
        ids_validos = [str(r.id) for r in rotas]

        while True:
            id_del = Interface.input_personalizado("ID para deletar (ou 'voltar'): ").strip()
            if Interface.checar_voltar(id_del): return

            if id_del in ids_validos:
                try:
                    with self.db.conectar() as conn:
                        conn.execute("DELETE FROM rotas WHERE id = ? AND motorista_id = ?", (id_del, self.motorista_id))
                        conn.commit()
                    Interface.print_sucesso("Rota deletada!")
                    Interface.aguardar(2)
                    return
                except Exception as e:
                    Interface.print_erro(f"Erro: {e}")
            else:
                Interface.print_erro("ID inválido.")

    def _atualizar_status(self, viagem_id, novo_status):
        """
        Núcleo da Regra de Negócio: Valida se a transição de status é permitida.
        """
        with self.db.conectar() as conn:
            # 1. Busca o status atual
            res = conn.execute("SELECT status FROM viagens WHERE id = ?", (viagem_id,)).fetchone()
            if not res:
                Interface.print_erro("Viagem não encontrada.")
                return False
            
            status_atual = res[0]

            # 2. Regras de Transição
            transicoes_validas = {
                'PENDENTE': ['ACEITA', 'RECUSADA'], # Só pode ir para Aceita ou Recusada
                'ACEITA': ['CONCLUÍDA'],            # Só pode ir para Concluída
                'CONCLUÍDA': [],                    # Fim da linha
                'RECUSADA': []                      # Fim da linha
            }

            # 3. Validação do Fluxo de Erro
            if novo_status not in transicoes_validas.get(status_atual, []):
                Interface.print_erro(f"🚫 Ação Bloqueada: Não é possível mudar de '{status_atual}' para '{novo_status}'.")
                if status_atual == 'PENDENTE' and novo_status == 'CONCLUÍDA':
                    Interface.print_aviso("Você precisa ACEITAR a viagem antes de concluí-la.")
                Interface.aguardar(3)
                return False

            # 4. Se passou, atualiza
            try:
                conn.execute("UPDATE viagens SET status = ? WHERE id = ?", (novo_status, viagem_id))
                conn.commit()
                Interface.print_sucesso(f"Status atualizado para: {novo_status}")
                
                # --- NOVO: GATILHO DE EMAIL ---
                # Busca dados do passageiro para notificar
                dados_pass = conn.execute("""
                    SELECT u.email, u.nome, r.origem, r.destino 
                    FROM viagens v
                    JOIN usuarios u ON v.passageiro_id = u.id
                    JOIN rotas r ON v.rota_id = r.id
                    WHERE v.id = ?
                """, (viagem_id,)).fetchone()
                
                if dados_pass:
                    email_p, nome_p, orig, dest = dados_pass
                    email_service = ServicoAutenticacao2FA()
                    print("Enviando notificação ao passageiro...")
                    email_service.enviar_aviso_viagem(email_p, nome_p, novo_status, f"{orig} -> {dest}")
                # ------------------------------

                Interface.aguardar(1)
                return True
            except Exception as e:
                Interface.print_erro(f"Erro ao atualizar: {e}")
                return False
            

    def gerenciar_solicitacoes(self):
        """Lista solicitações PENDENTES e permite aceitar/recusar."""

        Interface.exibir_cabecalho("Solicitações de Carona")
        
        # Busca viagens pendentes nas rotas DESTE motorista
        query = """
            SELECT v.id, u.nome, r.origem, r.destino, v.data_solicitacao
            FROM viagens v
            JOIN rotas r ON v.rota_id = r.id
            JOIN usuarios u ON v.passageiro_id = u.id
            WHERE r.motorista_id = ? AND v.status = 'PENDENTE'
        """
        
        pendentes = []
        with self.db.conectar() as conn:
            pendentes = conn.execute(query, (self.motorista_id,)).fetchall()

        if not pendentes:
            Interface.print_aviso("Nenhuma solicitação pendente.")
            print("="* 60)
            Interface.input_personalizado("Enter para voltar...")
            return

        for p in pendentes:
            print(f"[ID: {p[0]}] Passageiro: {p[1]}")
            print(f"       Rota: {p[2]} -> {p[3]}")
            print(f"       Data: {p[4]}\n")

        escolha = Interface.input_personalizado("Digite o ID para aceitar (ou 'voltar'): ").strip()
        if Interface.checar_voltar(escolha): return

        # Verifica se o ID digitado está na lista exibida (segurança)
        ids_validos = [str(p[0]) for p in pendentes]
        if escolha not in ids_validos:
            Interface.print_erro("ID inválido ou não pertence a você.")
            Interface.aguardar(2)
            return

        # Tenta mudar o status usando a regra de validação
        self._atualizar_status(escolha, 'ACEITA')

    def gerenciar_viagens_ativas(self):
        """Lista viagens ACEITAS e permite concluir."""
        Interface.exibir_cabecalho("Minhas Viagens em Andamento")
        
        query = """
            SELECT v.id, u.nome, r.origem, r.destino
            FROM viagens v
            JOIN rotas r ON v.rota_id = r.id
            JOIN usuarios u ON v.passageiro_id = u.id
            WHERE r.motorista_id = ? AND v.status = 'ACEITA'
        """
        
        ativas = []
        with self.db.conectar() as conn:
            ativas = conn.execute(query, (self.motorista_id,)).fetchall()

        if not ativas:
            Interface.print_aviso("Nenhuma viagem em andamento.")
            print("="* 60)
            Interface.input_personalizado("Enter para voltar...")
            return

        for a in ativas:
            print(f"[ID: {a[0]}] {a[2]} -> {a[3]} (Passageiro: {a[1]})")

        escolha = Interface.input_personalizado("Digite o ID para concluir (ou 'voltar'): ").strip()
        if Interface.checar_voltar(escolha): return
        
        # Tentativa de Erro (Simulação): Se o usuário tentasse algo errado aqui, o _atualizar_status barraria.
        # Fluxo Feliz: ACEITA -> CONCLUÍDA
        self._atualizar_status(escolha, 'CONCLUÍDA')

    def menu(self):
        opcao = ""
        while opcao != '0':
            Interface.exibir_cabecalho("Menu do Motorista")
            print("[1] Cadastrar Nova Rota")
            print("[2] Visualizar Minhas Rotas")
            print("[3] Deletar Rota")
            print("-" * 30)
            print("[4] Solicitações Pendentes (Aceitar)")
            print("[5] Concluir Viagens")
            print("-" * 30)
            print("[0] Deslogar")
            print("\n(Digite 'voltar' para trocar de perfil)")
            
            opcao = Interface.input_personalizado("Opção: ").strip()

            if opcao.lower() == 'voltar': return False

            if opcao == "1": self.cadastrar_rota()
            elif opcao == "2": self.visualizar_minhas_rotas()
            elif opcao == "3": self.deletar_rota()
            elif opcao == "4": self.gerenciar_solicitacoes()
            elif opcao == "5": self.gerenciar_viagens_ativas()
            elif opcao == "0":
                Interface.print_aviso("Deslogando...")
                Interface.aguardar(1)
                return True 
            else:
                Interface.print_erro("Opção inválida.")
                Interface.aguardar()
        return True
