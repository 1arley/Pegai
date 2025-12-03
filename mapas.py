from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from util import Interface

class ServicoMapas:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="pegai_ufrpe_app")

    def obter_coordenadas(self, endereco):
        """Converte texto em (latitude, longitude)."""
        try:
            # Adiciona contexto para ajudar a busca (Recife/PE)
            busca = f"{endereco}, Pernambuco, Brasil"
            local = self.geolocator.geocode(busca)
            
            if local:
                return (local.latitude, local.longitude)
            else:
                return None
        except Exception as e:
            # Em caso de falta de internet ou erro na API
            return None

    def calcular_distancia_km(self, origem_str, destino_str):
        """Retorna a distância em KM entre dois endereços."""
        coord_origem = self.obter_coordenadas(origem_str)
        coord_destino = self.obter_coordenadas(destino_str)

        if not coord_origem or not coord_destino:
            return None

        distancia_reta = geodesic(coord_origem, coord_destino).km
        distancia_ajustada_carro = distancia_reta * 0.35
        
        return round(distancia_ajustada_carro, 2)

    def sugerir_preco(self, distancia_km):
        """Calcula preço base: R$ 3.00 (partida) + R$ 1.50 por Km"""
        tarifa_base = 3.00
        preco_km = 1.50
        return round(tarifa_base + (distancia_km * preco_km), 2)
