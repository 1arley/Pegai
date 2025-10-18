import sqlite3 as sql
import util
import auth

def solicitar_viagem(usuario_id, rota_id):
    """Função interna (placeholder) para solicitar uma viagem."""
    util.exibir_cabecalho(f"Solicitando Rota {rota_id}")
    util.print_sucesso("Solicitação de viagem enviada com sucesso!")
    util.print_aviso("Aguardando confirmação do motorista... (Funcionalidade em desenvolvimento)")
    util.aguardar(2)
    # Aqui, em um app real, diminuiria as vagas e criaria um registro de "viagem"
    
def buscar_rotas_disponiveis(usuario_id):
    """Exibe rotas de outros motoristas com vagas disponíveis."""
    util.exibir_cabecalho("Rotas Disponíveis")
    banco = sql.connect('pegai.db')
    cursor = banco.cursor()
    
    # Query para buscar rotas, juntando nome do motorista e dados do veículo
    query = """
        SELECT
            r.id, u.nome, v.modelo, v.placa,
            r.origem, r.destino, r.horario_partida, r.dias_semana, r.vagas_disponiveis
        FROM rotas r
        JOIN usuarios u ON r.motorista_id = u.id
        JOIN veiculos v ON r.motorista_id = v.motorista_id
        WHERE r.motorista_id != ? AND r.vagas_disponiveis > 0
    """
    
    try:
        cursor.execute(query, (usuario_id,))
        rotas = cursor.fetchall()
    except Exception as e:
        util.print_erro(f"Erro ao buscar rotas: {e}")
        rotas = []
    finally:
        banco.close()

    if not rotas:
        util.print_aviso("Nenhuma rota com vagas disponível no momento.")
        util.aguardar(2)
        return

    print(f"Encontradas {len(rotas)} rotas disponíveis:\n")
    rotas_dict = {} # Dicionário para mapear input para ID da rota
    
    for i, rota in enumerate(rotas):
        numero_rota = str(i + 1)
        rotas_dict[numero_rota] = rota[0] # Mapeia "1" para o ID real da rota (rota[0])
        
        print(f"--- Rota {numero_rota} (ID: {rota[0]}) ---")
        print(f"  Motorista: {rota[1]}")
        print(f"  Veículo:   {rota[2]} (Placa: {rota[3]})")
        print(f"  Origem:    {rota[4]}")
        print(f"  Destino:   {rota[5]}")
        print(f"  Horário:   {rota[6]} (Dias: {rota[7]})")
        print(f"  Vagas:     {rota[8]}\n")
        
    print("="*30)
    
    while True:
        escolha = util.input_personalizado("Digite o número da Rota para solicitar (ou 'voltar'): ").strip()
        if util.checar_voltar(escolha):
            return
            
        if escolha in rotas_dict:
            rota_id_selecionada = rotas_dict[escolha]
            solicitar_viagem(usuario_id, rota_id_selecionada)
            return # Volta para o menu do passageiro
        else:
            util.print_erro("Opção inválida. Tente novamente.")


def visualizar_historico(usuario_id):
    """Exibe o histórico de viagens do passageiro (placeholder)."""
    util.exibir_cabecalho("Meu Histórico de Viagens")
    util.print_aviso("Funcionalidade em desenvolvimento.")
    print("\n")
    util.input_personalizado("Pressione Enter para voltar ao menu...")


def menu_passageiro(usuario_id):
    """Exibe o menu de opções para o passageiro."""
    opcao = ""
    while opcao != '0':
        util.exibir_cabecalho("Menu do Passageiro")
        print("[1] Buscar Rotas Disponíveis")
        print("[2] Meu Histórico de Viagens")
        print("[3] Quero ser motorista") # <-- NOVA OPÇÃO
        print("[0] Deslogar (Voltar ao menu principal)")
        print()
        opcao = util.input_personalizado("Escolha uma opção: ").strip()

        if opcao == "1":
            buscar_rotas_disponiveis(usuario_id)
        elif opcao == "2":
            visualizar_historico(usuario_id)
        elif opcao == "3":

            auth.completar_cadastro_motorista(usuario_id)

            util.print_aviso("Perfil de motorista criado!")
            util.print_aviso("Você será deslogado para atualizar seu perfil.")
            util.aguardar(3)
            return
        elif opcao == "0":
            util.print_aviso("Deslogando...")
            util.aguardar(1)
            return
        else:
            util.print_erro("Opção inválida. Tente novamente.")
            util.aguardar()