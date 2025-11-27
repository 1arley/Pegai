from util import Interface
from database import BancoDeDados
import auth
from models import Rota
from models import Rota, Viagem 

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
            Interface.aguardar(2)
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

        print("="*30)
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
        
        print("="*30)
        Interface.input_personalizado("Pressione Enter para voltar...")

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

            elif opcao == "0":
                Interface.print_aviso("Deslogando...")
                Interface.aguardar(1)
                return True
            else:
                Interface.print_erro("Inválido.")
                Interface.aguardar()
        
        return True