class Usuario:
    def __init__(self, id, nome, email, eh_motorista=False):
        self.id = id
        self.nome = nome
        self.email = email
        self.eh_motorista = bool(eh_motorista)

    def __str__(self):
        return f"{self.nome} ({self.email})"

class Rota:
    def __init__(self, id, origem, destino, horario_partida, dias_semana, vagas_disponiveis, preco=0.0, motorista_nome=None, veiculo_modelo=None):
        self.id = id
        self.origem = origem
        self.destino = destino
        self.horario_partida = horario_partida
        self.dias_semana = dias_semana
        self.vagas_disponiveis = vagas_disponiveis
        self.preco = preco 
        
        self.motorista_nome = motorista_nome
        self.veiculo_modelo = veiculo_modelo

    def __str__(self):
        return f"Rota {self.id}: {self.origem} -> {self.destino} (R$ {self.preco:.2f})"

class Avaliacao:
    def __init__(self, autor, nota, comentario):
        self.autor = autor
        self.nota = nota
        self.comentario = comentario

    def __str__(self):
        stars = "★" * self.nota + "☆" * (5 - self.nota)
        return f"{stars} - {self.comentario} (por {self.autor})"
    
class Viagem:
    def __init__(self, id, rota, data_solicitacao, status):
        self.id = id
        self.rota = rota  
        self.data_solicitacao = data_solicitacao
        self.status = status

    def __str__(self):
        return f"Viagem {self.id} | {self.status} | {self.rota.origem} -> {self.rota.destino}"