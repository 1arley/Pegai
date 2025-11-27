import re
from util import Interface
from database import BancoDeDados
from models import Rota  
from mapas import ServicoMapas

class ControladorMotorista:
    def __init__(self, motorista_id):
        self.motorista_id = motorista_id
        self.db = BancoDeDados()

    def cadastrar_rota(self):
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
        Interface.exibir_cabecalho("Minhas Rotas")
        
        rotas_objetos = [] # Lista para guardar OBJETOS Rota

        with self.db.conectar() as conn:
            cursor = conn.cursor()
            # Buscamos os dados crus
            cursor.execute("SELECT id, origem, destino, horario_partida, dias_semana, vagas_disponiveis FROM rotas WHERE motorista_id = ?", (self.motorista_id,))
            tuplas = cursor.fetchall()

            # CONVERSÃO MÁGICA: Tupla -> Objeto
            for t in tuplas:
                # t[0]=id, t[1]=origem, etc.
                nova_rota = Rota(t[0], t[1], t[2], t[3], t[4], t[5])
                rotas_objetos.append(nova_rota)

        if not rotas_objetos:
            Interface.print_aviso("Nenhuma rota cadastrada.")
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
            Interface.input_personalizado("Enter para voltar...")
        
        return rotas_objetos # Retorna lista de objetos

    def deletar_rota(self):
        Interface.exibir_cabecalho("Deletar Rota")
        # Recebe objetos Rota
        rotas = self.visualizar_minhas_rotas(mostrar_ids=True)
        if not rotas:
            Interface.aguardar(2)
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

    def menu(self):
        opcao = ""
        while opcao != '0':
            Interface.exibir_cabecalho("Menu do Motorista")
            print("[1] Cadastrar Nova Rota")
            print("[2] Visualizar Minhas Rotas")
            print("[3] Deletar Rota")
            print("[0] Deslogar")
            print()
            print("(Digite 'voltar' para trocar de perfil)")
            
            opcao = Interface.input_personalizado("Opção: ").strip()

            if opcao.lower() == 'voltar':
                return False # <--- Voltar para escolha de perfil

            if opcao == "1": self.cadastrar_rota()
            elif opcao == "2": self.visualizar_minhas_rotas()
            elif opcao == "3": self.deletar_rota()
            elif opcao == "0":
                Interface.print_aviso("Deslogando...")
                Interface.aguardar(1)
                return True 
            else:
                Interface.print_erro("Opção inválida.")
                Interface.aguardar()
        return True