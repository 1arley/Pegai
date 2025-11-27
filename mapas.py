# Crie o arquivo mapas.py
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from util import Interface

class ServicoMapas:
    def __init__(self):
        # user_agent é obrigatório para identificar seu app no OpenStreetMap
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

        # geodesic calcula a distância curva na superfície da Terra
        # Multiplicamos por 1.3 como um "Fator de Tortuosidade" aproximado
        # (porque carros não andam em linha reta, eles fazem curvas)
        # Alias 
        # 🔢 Percentual hipotético distância → preço
            # ➡️ Corridas curtas (até 3 km)

            # A tarifa base pesa muito

            # O tempo parado pesa muito

            # A distância pesa pouco

            # Distância representaria: ~30% a 50% do preço final

            # ➡️ Corridas médias (3 a 10 km)

            # Tarifa base dilui

            # Tempo ainda pesa, mas menos

            # Distância vira o principal fator

            # Distância representaria: ~50% a 70% do preço final

            # ➡️ Corridas longas (10 km ou mais)

            # Tarifa base fica irrelevante

            # Tempo ainda pesa, mas proporcional

            # Distância vira o componente dominante

            # Distância representaria: ~70% a 85% do preço final
        # Por Enquanto...
        distancia_reta = geodesic(coord_origem, coord_destino).km
        distancia_ajustada_carro = distancia_reta * 0.35
        
        return round(distancia_ajustada_carro, 2)

    def sugerir_preco(self, distancia_km):
        """Calcula preço base: R$ 3.00 (partida) + R$ 1.50 por Km"""
        tarifa_base = 3.00
        preco_km = 1.50
        return round(tarifa_base + (distancia_km * preco_km), 2)