import util
import re
import sqlite3 as sql

def cadastrar_rota(motorista_id):
    util.exibir_cabecalho("Cadastro de rotas")

    # Origem
    while True:
        origem = util.input_personalizado("Ponto de partida: ").strip()
        if util.checar_voltar(origem):
            return
        if len(origem) > 100:
            util.print_erro("Você excedeu o número de caracteres. (100)")
            continue
        if len(origem) == 0:
            util.print_erro("A origem não pode ser vazia.")
            continue
        break

    # Destino
    while True:
        destino = util.input_personalizado("Destino: ").strip()
        if util.checar_voltar(destino):
            return
        if len(destino) > 100:
            util.print_erro("Você excedeu o número de caracteres. (100)")
            continue
        if len(destino) == 0:
            util.print_erro("O destino não pode ser vazio.")
            continue
        break

    # Horário
    while True:
        horario_partida = util.input_personalizado("Horário de partida (ex: 13:00): ").strip()
        pattern = re.compile(r"^\d{2}:\d{2}$")
        if util.checar_voltar(horario_partida):
            return
        if not re.match(pattern, horario_partida):
            util.print_erro("Digite no formato válido. ex: 13:00")
            continue
        break

    # Dias da semana
    dias_validos = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']
    while True:
        dias_semana = util.input_personalizado("Dias (seg, ter, qua, qui, sex, sab, dom): ").strip()
        if util.checar_voltar(dias_semana):
            return
        if dias_semana not in dias_validos:
            util.print_erro("Digite no formato válido. ex: seg")
            continue
        break

    # Vagas
    while True:
        vagas_str = util.input_personalizado("Vagas disponíveis: ").strip()
        if util.checar_voltar(vagas_str):
            return
        if not vagas_str.isdigit():
            util.print_erro("Digite um número válido para vagas.")
            continue
        vagas_disponiveis = int(vagas_str)
        if vagas_disponiveis >= 50:
            util.print_erro("Você definitivamente não tem um ônibus maior que isso.")
            continue
        break

    banco = None
    try:
        banco = sql.connect('pegai.db')
        cursor = banco.cursor()
        cursor.execute(
            "INSERT INTO rotas (motorista_id, origem, destino, horario_partida, dias_semana, vagas_disponiveis) VALUES (?, ?, ?, ?, ?, ?)",
            (motorista_id, origem, destino, horario_partida, dias_semana, vagas_disponiveis)
        )
        banco.commit()
        util.print_sucesso("Rota cadastrada com sucesso!")
    except Exception as e:
        util.print_erro(f"Ocorreu um erro ao cadastrar a rota: {e}")
    finally:
        if banco:
            banco.close()
        util.aguardar(2)


def visualizar_minhas_rotas(motorista_id, mostrar_ids=False):
    """Exibe todas as rotas cadastradas pelo motorista."""
    util.exibir_cabecalho("Minhas Rotas Cadastradas")
    banco = sql.connect('pegai.db')
    cursor = banco.cursor()
    cursor.execute("SELECT origem, destino, horario_partida, dias_semana, vagas_disponiveis FROM rotas WHERE motorista_id = ?", (motorista_id,))
    rotas = cursor.fetchall()
    banco.close()

    if not rotas:
        util.print_aviso("Você ainda não cadastrou nenhuma rota.")
    else:
        for i, rota in enumerate(rotas):
            print(f"\n--- Rota {i+1} ---")
            print(f"  Origem: {rota[0]}")
            print(f"  Destino: {rota[1]}")
            print(f"  Horário: {rota[2]}")
            print(f"  Dias: {rota[3]}")
            print(f"  Vagas: {rota[4]}")

    print("\n") # Adiciona espaço antes de pedir o Enter
    util.input_personalizado("Pressione Enter para voltar ao menu...")

def deletar_rota(motorista_id):
    """Exibe as rotas com ID e permite ao motorista deletar uma."""
    util.exibir_cabecalho("Deletar Rota")
    
    # Chama a função de visualização mostrando os IDs
    rotas = visualizar_minhas_rotas(motorista_id, mostrar_ids=True)
    
    if not rotas: # Se for Falso (sem rotas), apenas retorna
        util.aguardar(2)
        return

    # Cria uma lista de IDs válidos para checagem
    ids_validos = [str(rota[0]) for rota in rotas]

    while True:
        id_para_deletar = util.input_personalizado("Digite o ID da rota que deseja deletar (ou 'voltar'): ").strip()
        
        if util.checar_voltar(id_para_deletar):
            return

        if id_para_deletar in ids_validos:
            try:
                banco = sql.connect('pegai.db')
                cursor = banco.cursor()
                # A query de deleção TAMBÉM checa o motorista_id por segurança
                cursor.execute(
                    "DELETE FROM rotas WHERE id = ? AND motorista_id = ?",
                    (id_para_deletar, motorista_id)
                )
                banco.commit()
                util.print_sucesso(f"Rota {id_para_deletar} deletada com sucesso!")
            except Exception as e:
                util.print_erro(f"Ocorreu um erro ao deletar a rota: {e}")
            finally:
                banco.close()
                util.aguardar(2)
                return # Sai da função após a tentativa
        else:
            util.print_erro("ID inválido. Tente novamente.")
            util.aguardar()


def menu_motorista(motorista_id):
    """Exibe o menu de opções para o motorista."""
    opcao = ""
    while opcao != '0':
        util.exibir_cabecalho("Menu do Motorista")
        print("[1] Cadastrar Nova Rota")
        print("[2] Visualizar Minhas Rotas")
        print("[3] Deletar Rota")
        print("[0] Deslogar (Voltar ao menu principal)")
        print()
        opcao = util.input_personalizado("Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_rota(motorista_id)
        elif opcao == "2":
            visualizar_minhas_rotas(motorista_id, mostrar_ids=False) # Apenas visualiza
            util.input_personalizado("Pressione Enter para voltar ao menu...")
        elif opcao == "3":
            deletar_rota(motorista_id) # <-- NOVA CHAMADA
        elif opcao == "0":
            util.print_aviso("Deslogando...")
            util.aguardar(1)
            return # Retorna para a função de login
        else:
            util.print_erro("Opção inválida. Tente novamente.")
            util.aguardar()
