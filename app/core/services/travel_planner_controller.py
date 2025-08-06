import logging
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from datetime import datetime
from core.api.open_api import OpenAi
from core.utils.file_utils import FileUtils
from core.utils.date_utils import DateUtils
from core.utils.request_utils import RequestUtils
from core.api.google.routes_api import RoutesClient
from core.api.google.geocoding_api import GeoCodingClient
from core.genetic.genetic_algorithm import TravelGeneticAlgorithm


class TravelPlannerController:
    def __init__(self):
        self.file_utils = FileUtils()
        self.date_utils = DateUtils()

    def handle_text_input(self,
                          destination: str,
                          hotel_name: str,
                          start_date,
                          end_date,
                          temperature: float,
                          top_p: float) -> pd.DataFrame:
        
        trip_days = self.date_utils.get_trip_days(start_date, end_date)
        geo_client = GeoCodingClient()
        open_ai = OpenAi(top_p, temperature, destination, trip_days)
    
        def fetch_hotel_coordinates():
            return geo_client.get_coordinates(hotel_name)

        def fetch_tourist_places():
            return open_ai.get_places_tourist_points()
        
        tasks = [fetch_hotel_coordinates, fetch_tourist_places]

        hotel_coordinates, tourist_places_df = RequestUtils.run_parallel_tasks(tasks)

        hotel_df = pd.DataFrame([{
            'places': 'HOTEL',
            'latitude': hotel_coordinates[0],
            'longitude': hotel_coordinates[1],
            'mon': '00:00-23:59',
            'tue': '00:00-23:59',
            'wed': '00:00-23:59',
            'thu': '00:00-23:59',
            'fri': '00:00-23:59',
            'sat': '00:00-23:59',
            'sun': '00:00-23:59',
            'estimated_duration_min': 0,
            'priority': 0
        }])
        
        tourist_places_df = pd.concat([hotel_df, tourist_places_df], ignore_index=True)

        return tourist_places_df



    def handle_file_upload(self, uploaded_file, hotel_name: str) -> pd.DataFrame:
        """
        Lê o arquivo CSV enviado pelo usuário e transforma em DataFrame.
        """
        geo_client = GeoCodingClient()
        hotel_coordinates = geo_client.get_coordinates(hotel_name)
        df_file = self.file_utils.read_csv(uploaded_file)
        return df_file, hotel_coordinates
    

    def run_genetic_algorithm(self,
                               df_places: pd.DataFrame,
                               pop_size: int,
                               generations: int,
                               mutation: float,
                               crossover: float,
                               time_limit: int,
                               start_date: datetime,
                               end_date: datetime) -> TravelGeneticAlgorithm:
        """
        Executa o algoritmo genético com os dados fornecidos.
        """
        # Consulta API Routes para obter distâncias e durações
        routes_client = RoutesClient()
        duration_df, distance_df = routes_client.compute_duration_and_distance(df_places)
        
        ga = TravelGeneticAlgorithm(
            places=df_places,
            duration = duration_df,
            distance = distance_df,
            population_size=pop_size,
            generations=generations,
            mutation_rate=mutation,
            crossover_rate=crossover,
            time_min_daily=time_limit,
            start_date=start_date,
            end_date=end_date,
        )
        return ga.run()

    def render_result_summary(self, resultado: dict) -> None:
        try:
            st.subheader("📊 Resumo da Execução do Algoritmo Genético")

            st.markdown(f"**Melhor Fitness:** `{resultado['melhor_fitness']:.2f}`")
            st.markdown(f"**Gerações Executadas:** `{resultado['geracoes_executadas']}`")

            st.markdown("**Ordem dos Locais (índices):**")
            st.code(resultado['melhor_individuo_idx'], language="python")

            st.markdown("**Ordem dos Locais (nomes):**")
            st.code(resultado['melhor_individuo_nomes'], language="python")

        except Exception as e:
            st.error("Erro ao exibir o resumo dos resultados.")
            logging.exception("Erro ao exibir resumo:", exc_info=e)


    def render_daily_maps(self, roteiro_por_dia: dict, hotel_coords: tuple[float, float]) -> None:
        try:
            st.subheader("📍 Mapas dos Roteiros por Dia")

            for i, (dia, info) in enumerate(sorted(roteiro_por_dia.items()), 1):
                locais = info.get("locais", [])
                if not locais:
                    continue

                with st.container():  # 🔒 Garante que tudo fique agrupado
                    st.markdown(f"#### 🗓️ Dia {i} - {dia}")

                    mapa = folium.Map(location=hotel_coords, zoom_start=13)

                    # Hotel
                    folium.Marker(hotel_coords, tooltip="Hotel", icon=folium.Icon(color='green')).add_to(mapa)

                    coords_list = []
                    for j, local in enumerate(locais, 1):
                        coord = (float(local["latitude"]), float(local["longitude"]))  # garantir float
                        coords_list.append(coord)
                        folium.Marker(coord, tooltip=f"{j}. {local['nome']}", icon=folium.Icon(color='blue')).add_to(mapa)

                    # Linha da rota
                    folium.PolyLine([hotel_coords] + coords_list + [hotel_coords],
                                    color="blue", weight=2.5, opacity=0.8).add_to(mapa)

                    # Exibe o mapa
                    st_folium(mapa, width=700, height=500)

                    st.markdown("---")  # 🔹 linha de separação discreta

        except Exception as e:
            st.error(f"Erro ao renderizar os mapas: {e}")
            logging.exception(f"Erro ao renderizar os mapas: {e}")
            