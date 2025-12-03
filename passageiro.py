from util import Interface
from database import BancoDeDados
import auth
from models import Rota
from models import Rota, Viagem 
from util import Cores
import time

class ControladorPassageiro:

    def __init__(self, usuario_logado):
        self.usuario = usuario_logado  
        self.usuario_id = usuario_logado.id 
        self.db = BancoDeDados()

    def solicitar_viagem(self, rota_obj):
        Interface.exibir_cabecalho(f"Solicitando Rota {rota_obj.id}")
        print(f"Destino: {rota_obj.destino}")
        print(f"Motorista: {rota_obj.motorista_nome}")
        
        try:
            with self.db.conectar() as conn:
                conn.execute(
                    "INSERT INTO viagens (passageiro_id, rota_id, status) VALUES (?, ?, ?)",
                    (self.usuario_id, rota_obj.id, 'PENDENTE')
                )
                conn.commit()
            
            Interface.print_sucesso("Solicitação registrada no histórico!")
        except Exception as e:
            Interface.print_erro(f"Erro ao salvar solicitação: {e}")
        
        Interface.aguardar(2)

    def buscar_rotas(self):
        Interface.exibir_cabecalho("Rotas Disponíveis")
        
        query = """
            SELECT r.id, u.nome, v.modelo, v.placa, r.origem, r.destino, r.horario_partida, r.dias_semana, r.vagas_disponiveis
            FROM rotas r
            JOIN usuarios u ON r.motorista_id = u.id
            JOIN veiculos v ON r.motorista_id = v.motorista_id
            WHERE r.motorista_id != ? AND r.vagas_disponiveis > 0
        """
        
        rotas_objetos = []
        try:
            with self.db.conectar() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (self.usuario_id,))
                tuplas = cursor.fetchall()

                # TRANSFORMAÇÃO
                for t in tuplas:
                    # t[1] é nome do motorista, t[2] é modelo
                    rota = Rota(
                        id=t[0], 
                        origem=t[4], 
                        destino=t[5], 
                        horario_partida=t[6], 
                        dias_semana=t[7], 
                        vagas_disponiveis=t[8],
                        motorista_nome=t[1],  # Passando os extras
                        veiculo_modelo=t[2]
                    )
                    rotas_objetos.append(rota)

        except Exception as e:
            Interface.print_erro(f"Erro: {e}")

        if not rotas_objetos:
            Interface.print_aviso("Nenhuma rota disponível.")
            print("="*60)
            Interface.input_personalizado("Pressione Enter para voltar...")
            return

        print(f"Encontradas {len(rotas_objetos)} rotas:\n")
        
        # Dicionário mapeia "1", "2" -> Objeto Rota
        mapa_rotas = {} 
        
        for i, rota in enumerate(rotas_objetos):
            idx = str(i + 1)
            mapa_rotas[idx] = rota
            
            print(f"--- Rota {idx} ---")
            # Uso limpo dos atributos
            print(f"  Motorista: {rota.motorista_nome} | Veículo: {rota.veiculo_modelo}")
            print(f"  {rota.origem} -> {rota.destino}")
            print(f"  Horário: {rota.horario_partida} ({rota.dias_semana}) | Vagas: {rota.vagas_disponiveis}\n")

        print("="*60)
        while True:
            esc = Interface.input_personalizado("Número da Rota (ou 'voltar'): ").strip()
            if Interface.checar_voltar(esc): return
            
            if esc in mapa_rotas:
                # Passa o objeto selecionado
                self.solicitar_viagem(mapa_rotas[esc])
                return
            else:
                Interface.print_erro("Opção inválida.")
        
        
    def visualizar_historico(self):
        Interface.exibir_cabecalho("Meu Histórico de Viagens")
        
        viagens_objs = []
        
        query = """
            SELECT 
                v.id, v.data_solicitacao, v.status,
                r.id, r.origem, r.destino, r.horario_partida, r.dias_semana, r.vagas_disponiveis,
                u.nome as nome_motorista, vec.modelo as modelo_veiculo
            FROM viagens v
            JOIN rotas r ON v.rota_id = r.id
            JOIN usuarios u ON r.motorista_id = u.id
            JOIN veiculos vec ON r.motorista_id = vec.motorista_id
            WHERE v.passageiro_id = ?
            ORDER BY v.id DESC
        """

        try:
            with self.db.conectar() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (self.usuario_id,))
                tuplas = cursor.fetchall()
                
                for t in tuplas:
                    # t[0]=viagem_id, t[1]=data, t[2]=status
                    # Cria objeto Rota (t[3] a t[10])
                    rota = Rota(t[3], t[4], t[5], t[6], t[7], t[8], motorista_nome=t[9], veiculo_modelo=t[10])
                    
                    # Cria objeto Viagem
                    viagem = Viagem(t[0], rota, t[1], t[2])
                    viagens_objs.append(viagem)

        except Exception as e:
            Interface.print_erro(f"Erro ao buscar histórico: {e}")
            Interface.aguardar(2)
            return

        if not viagens_objs:
            Interface.print_aviso("Nenhuma viagem encontrada no histórico.")
        else:
            print(f"Histórico de {len(viagens_objs)} viagens:\n")
            for v in viagens_objs:
                print(f"--- Solicitação #{v.id} [{v.status}] ---")
                print(f"  Data: {v.data_solicitacao}")
                print(f"  Rota: {v.rota.origem} -> {v.rota.destino}")
                print(f"  Motorista: {v.rota.motorista_nome} ({v.rota.veiculo_modelo})")
                print(f"  Horário: {v.rota.horario_partida}\n")
        
        print("="*60)
        Interface.input_personalizado("Pressione Enter para voltar...")
    def acompanhar_viagem(self):
        Interface.exibir_cabecalho("Acompanhar Viagem Atual")
        
        # Busca apenas viagens ativas (Pendente ou Aceita)
        query = """
            SELECT 
                v.id, v.status, 
                u.nome, vec.modelo, vec.placa, vec.cor,
                r.origem, r.destino
            FROM viagens v
            JOIN rotas r ON v.rota_id = r.id
            JOIN usuarios u ON r.motorista_id = u.id
            JOIN veiculos vec ON r.motorista_id = vec.motorista_id
            WHERE v.passageiro_id = ? AND v.status IN ('PENDENTE', 'ACEITA')
        """
        
        viagens_ativas = []
        with self.db.conectar() as conn:
            viagens_ativas = conn.execute(query, (self.usuario_id,)).fetchall()

        if not viagens_ativas:
            Interface.print_aviso("Você não tem nenhuma viagem ativa no momento.")
            Interface.input_personalizado("Pressione Enter para voltar...")
            return

        for v in viagens_ativas:
            # v[0]=id, v[1]=status, v[2]=motorista, v[3]=modelo, v[4]=placa, v[5]=cor, v[6]=origem, v[7]=destino
            vid, status, mot, mod, placa, cor, orig, dest = v
            
            print(f"--- Viagem #{vid} ---")
            print(f"Rota: {orig} -> {dest}")
            
            if status == 'PENDENTE':
                print(f"Status: {Cores.AMARELO}AGUARDANDO MOTORISTA...{Cores.FIM}")
                print("O motorista ainda não confirmou sua solicitação.")
            
            elif status == 'ACEITA':
                print(f"Status: {Cores.VERDE}ACEITA! O MOTORISTA ESTÁ A CAMINHO{Cores.FIM}")
                print(f"Motorista: {mot}")
                print(f"Veículo: {mod} {cor} (Placa: {placa})")
                print("Fique atento ao local de embarque.")
            
            print("-" * 30)

        # Loop q serve para 'simular' tempo real
        print("\n[1] Atualizar Status")
        print("[0] Voltar")
        op = Interface.input_personalizado("Opção: ").strip()
        
        if op == '1':
            self.acompanhar_viagem() 
        else:
            return
        
    def avaliar_motorista(self):
        Interface.exibir_cabecalho("Avaliar Motorista")
        
        # 1. Listar viagens elegíveis (CONCLUÍDA e SEM avaliação deste autor)
        print("--- Viagens Pendentes de Avaliação ---")
        query_pendentes = """
            SELECT v.id, r.origem, r.destino, u.nome
            FROM viagens v
            JOIN rotas r ON v.rota_id = r.id
            JOIN usuarios u ON r.motorista_id = u.id
            WHERE v.passageiro_id = ? 
              AND v.status = 'CONCLUÍDA'
              AND NOT EXISTS (SELECT 1 FROM avaliacoes a WHERE a.viagem_id = v.id AND a.autor_id = ?)
        """
        
        with self.db.conectar() as conn:
            pendentes = conn.execute(query_pendentes, (self.usuario_id, self.usuario_id)).fetchall()
            
        if not pendentes:
            Interface.print_aviso("Nenhuma viagem pendente para avaliar.")
            print("=" * 60)
            Interface.input_personalizado("Pressione Enter para voltar...")
            return

        for p in pendentes:
            print(f"[ID: {p[0]}] {p[1]} -> {p[2]} (Motorista: {p[3]})")
        print("-" * 60)

        # 2. Captura do ID com tratamento de erros robusto
        viagem_id = Interface.input_personalizado("Digite o ID da viagem para avaliar (ou 'voltar'): ").strip()
        if Interface.checar_voltar(viagem_id): return

        with self.db.conectar() as conn:
            # Busca dados crus da viagem para validar as Regras de Negócio
            # Trazemos também o motorista_id para saber quem será o 'alvo' da avaliação
            dados_viagem = conn.execute("""
                SELECT v.status, r.motorista_id 
                FROM viagens v 
                JOIN rotas r ON v.rota_id = r.id
                WHERE v.id = ? AND v.passageiro_id = ?
            """, (viagem_id, self.usuario_id)).fetchone()

            # Viagem inexistente ou de outro usuário
            if not dados_viagem:
                Interface.print_erro("Viagem não encontrada ou não pertence a você.")
                Interface.aguardar(2)
                return

            status_atual, motorista_id = dados_viagem

            # Tentar avaliar viagem não concluída
            if status_atual != 'CONCLUÍDA':
                Interface.print_erro(f"Ação Bloqueada: O status atual é '{status_atual}'.")
                Interface.print_aviso("Avaliação disponível apenas após a viagem ser CONCLUÍDA.")
                Interface.aguardar(3)
                return
                
            # Verifica se já existe um registro na tabela avaliacoes para essa viagem e autor
            ja_avaliou = conn.execute(
                "SELECT 1 FROM avaliacoes WHERE viagem_id = ? AND autor_id = ?", 
                (viagem_id, self.usuario_id)
            ).fetchone()
            
            if ja_avaliou:
                Interface.print_erro("Você já avaliou esta viagem anteriormente.")
                Interface.aguardar(2)
                return

            # 3. Captura da Nota (Validação 1-5)
            nota = 0
            while True:
                entrada = Interface.input_personalizado("Nota (1 a 5): ").strip()
                if Interface.checar_voltar(entrada): return
                
                if entrada.isdigit():
                    nota = int(entrada)
                    if 1 <= nota <= 5:
                        break # Nota válida!
                
                # FLUXO DE ERRO 4: Nota inválida (Tipo ou Intervalo)
                Interface.print_erro("Nota inválida! Digite um número inteiro entre 1 e 5.")

            # 4. Captura do Comentário (Opcional)
            comentario = Interface.input_personalizado("Comentário (Opcional): ").strip()

            # 5. Persistência
            try:
                conn.execute(
                    "INSERT INTO avaliacoes (viagem_id, autor_id, alvo_id, nota, comentario) VALUES (?, ?, ?, ?, ?)",
                    (viagem_id, self.usuario_id, motorista_id, nota, comentario)
                )
                conn.commit()
                Interface.print_sucesso("Avaliação registrada com sucesso!")
                Interface.aguardar(2)
            except Exception as e:
                Interface.print_erro(f"Erro ao salvar avaliação: {e}")
                
    def acompanhar_viagem_tempo_real(self):
        """
        Bloqueia o terminal e atualiza o status a cada 5 segundos.
        """
        Interface.limpar_tela()
        print(f"{Cores.AMARELO}--- MODO RADAR ATIVADO ---{Cores.FIM}")
        print("Atualizando status a cada 5 segundos...")
        print("(Pressione CTRL+C para sair deste modo)\n")

        try:
            while True:
                # 1. Busca status atual
                query = """
                    SELECT v.id, v.status, u.nome, r.origem, r.destino
                    FROM viagens v
                    JOIN rotas r ON v.rota_id = r.id
                    JOIN usuarios u ON r.motorista_id = u.id
                    WHERE v.passageiro_id = ? AND v.status IN ('PENDENTE', 'ACEITA')
                """
                
                with self.db.conectar() as conn:
                    viagem = conn.execute(query, (self.usuario_id,)).fetchone()

                # Limpa a área de status (simulado limpando a tela toda)
                Interface.limpar_tela()
                print(f"{Cores.AMARELO}--- MONITORAMENTO EM TEMPO REAL ---{Cores.FIM}")
                print("(Pressione CTRL+C para voltar ao menu)\n")

                if not viagem:
                    print("Nenhuma viagem ativa encontrada ou viagem concluída/recusada.")
                    input("Enter para sair...")
                    return

                vid, status, mot, orig, dest = viagem
                print(f"Viagem #{vid} | {orig} -> {dest}")
                print(f"Motorista: {mot}")
                print("-" * 30)
                
                if status == 'PENDENTE':
                    print(f"STATUS ATUAL: {Cores.AMARELO}⏳ PENDENTE{Cores.FIM}")
                elif status == 'ACEITA':
                    print(f"STATUS ATUAL: {Cores.VERDE}✅ ACEITA! (Prepare-se){Cores.FIM}")
                    # Aqui poderíamos tocar um som (print('\a') as vezes funciona no Windows)
                    print("\a") 

                print(f"\nÚltima atualização: {time.strftime('%H:%M:%S')}")
                
                # Aguarda 5 segundos antes de repetir
                Interface.aguardar(5)

        except KeyboardInterrupt:
            print("\nSaindo do modo radar...")
            Interface.aguardar(1)
            return

    def menu(self):
        opcao = ""
        while opcao != '0':
            Interface.exibir_cabecalho("Menu do Passageiro")
            print("[1] Buscar Rotas")
            print("[2] Histórico")
            
            # Muda o texto dependendo se o usuário já é motorista
            if self.usuario.eh_motorista:
                print("[3] Adicionar Veículo (Extra)")
            else:
                print("[3] Quero ser motorista")
                
            print("[4] Avaliar Motorista")
            print("[5] Acompanhar Status da Viagem")
            print("[6] Acompanhar Viagem (Modo Radar)")
            print("[0] Deslogar")
            print()
            print("(Digite 'voltar' para trocar de perfil)") 
            
            opcao = Interface.input_personalizado("Opção: ").strip()

            if opcao.lower() == 'voltar':
                return False

            if opcao == "1": 
                self.buscar_rotas()
            elif opcao == "2": 
                self.visualizar_historico()
            elif opcao == "3":
                # Captura o resultado da operação (True ou False)
                sucesso = auth.ControladorAutenticacao.completar_cadastro_motorista(self.usuario_id)
                
                if sucesso:
                    # Só desloga se o cadastro funcionou, para atualizar as permissões
                    Interface.print_aviso("Perfil atualizado! Faça login novamente.")
                    return True
                else:
                    # Se cancelou (voltar) ou deu erro, apenas roda o loop de novo
                    pass
            elif opcao == "4":
                self.avaliar_motorista()
                
            elif opcao == "5":
                self.acompanhar_viagem()
            elif opcao == "6":
                self.acompanhar_viagem_tempo_real()
            elif opcao == "0":
                Interface.print_aviso("Deslogando...")
                Interface.aguardar(1)
                return True
            else:
                Interface.print_erro("Inválido.")
                Interface.aguardar()
        
        return True
