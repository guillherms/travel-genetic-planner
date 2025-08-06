import random
import logging
import pandas as pd
from datetime import datetime, timedelta
from core.utils.date_utils import DateUtils
from core.utils.geo_utils import GeoUtils
from core.utils.time_utils import TimeUtils

# logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TravelGeneticAlgorithm:
    def __init__(self,
                 places: pd.DataFrame,
                 duration: pd.DataFrame,
                 distance: pd.DataFrame,
                 population_size: int,
                 generations:int,
                 mutation_rate: int,
                 crossover_rate: int,
                 time_min_daily:int,
                 start_date: datetime,
                 end_date: datetime,):
        self.places = places
        self.duration = duration
        self.distance = distance
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.time_min_daily = time_min_daily
        self.start_date = start_date
        self.end_date = end_date
        self.population = pd.DataFrame()
        self.geo_utils = GeoUtils()
        self.time_utils = TimeUtils()
        self.date_utils = DateUtils()

    def run(self) -> dict:
        self.population = self._initialize_population()

        best_fitness = float('-inf')
        best_individual = None
        generations_without_improvement = 0
        max_generations_without_improvement = 5

        for generation in range(self.generations):
            fitness_scores, roteiro_por_dia = self._evaluate_fitness()
            current_best = max(fitness_scores)
            best_idx = fitness_scores.index(current_best)

            if current_best > best_fitness:
                best_fitness = current_best
                best_individual = self.population[best_idx]
                best_roteiro = roteiro_por_dia[best_idx]
                generations_without_improvement = 0
                logging.info(f"Generation {generation}: New best fitness found: {best_fitness:.2f}")
            else:
                generations_without_improvement += 1

            elite, fathers = self._select_parents_by_elistism_tournament(
                fitness_scores,
                elitismo=2,
                k_torneio=3,
            )
            children = self._apply_crossover_ox(fathers)
            mutated_children = self._apply_mutation(children)

            self.population = elite + mutated_children[:self.population_size - len(elite)]

            logging.info(f"Generation {generation} | Best fitness: {current_best:.2f}")
            generation_reached = generation + 1

            if generations_without_improvement >= max_generations_without_improvement:
                logging.info(f"Parada antecipada por estagnação após {generation + 1} gerações.")
                break

        logging.info(f"Algoritmo finalizado após {generation_reached} gerações.")
        logging.info(f"Melhor fitness final: {best_fitness:.2f}")
        logging.info("Melhor indivíduo (ordem dos locais):", best_individual)
        logging.info("Melhor roteiro por dia:")

        roteiro_dict = self._format_roteiro_por_dia(best_roteiro)

        melhor_individuo_nomes = [self.places.iloc[idx]['places'] for idx in best_individual]

        return self._format_response(best_fitness,
                                     generation_reached,
                                     best_individual,
                                     melhor_individuo_nomes,
                                     roteiro_dict)

    def _format_roteiro_por_dia(self, best_roteiro):
        roteiro_dict = {}
        for i, dia in enumerate(best_roteiro):
            data = self.start_date + timedelta(days=i)
            data_str = data.strftime('%Y-%m-%d')
            locais = []
            for idx in dia:
                lugar = self.places.iloc[idx]
                locais.append({
                    "nome": lugar['places'],
                    "latitude": float(lugar['latitude']),
                    "longitude": float(lugar['longitude'])
                })
            roteiro_dict[data_str] = {"locais": locais}
            logging.info(f"  Dia {i+1} ({data_str}): {[l['nome'] for l in locais]}")
        return roteiro_dict

    def _format_response(self,
                         best_fitness: float,
                         generation_reached: int,
                         best_individual: list[int],
                         melhor_individuo_nomes: list[str],
                         roteiro_dict: dict) -> dict:
        return {
            "melhor_fitness": round(float(best_fitness), 4),
            "geracoes_executadas": generation_reached,
            "melhor_individuo_idx": best_individual,
            "melhor_individuo_nomes": melhor_individuo_nomes,
            "roteiro_por_dia": roteiro_dict
        }
                       
                                               
    def _initialize_population(self) -> None:
        # Initialize the population with random individuals
        try:
            logging.info(self.places.head())
            df_places_to_visit_sorted = self.places.sort_values(by="priority", ascending=False)
            indices = list(df_places_to_visit_sorted.index)
            
            population = []
            for _ in range(self.population_size):
                individual = random.sample(indices, len(indices))
                population.append(individual)
            return population
        except Exception as e:
            logging.exception(f"An error occurred while initializing the population: {e}")
            raise


    def _evaluate_fitness(self):
        try:
            fitness_scores = []
            roteiros_por_individuo = []

            dias_roteiro = self.date_utils.get_date_range(self.start_date, self.end_date) 
            dias_da_semana = [self.date_utils.get_day_abbr(d).lower() for d in dias_roteiro]

            for individuo in self.population:
                roteiro_por_dia = []
                dia_atual = []
                tempo_dia = 0
                tempo_atual = 8 * 60  # 08:00h em minutos
                tempo_total_usado = 0
                prioridade_bonus = 0
                funcionamento_bonus = 0
                deslocamento_total = 0
                dia_index = 0

                for i, idx in enumerate(individuo):
                    lugar = self.places.iloc[idx]
                    tempo_visita = lugar['estimated_duration_min']

                    # Tempo de deslocamento entre locais
                    if dia_atual:
                        origem = self.places.iloc[dia_atual[-1]]['places']
                    else:
                        origem = 'HOTEL'

                    destino = lugar['places']
                    tempo_desloc = self.duration.loc[origem, destino]
                    deslocamento_total += tempo_desloc
                    tempo_total = tempo_visita + tempo_desloc

                    # Verifica se cabe no dia atual
                    if tempo_dia + tempo_total > self.time_min_daily:
                        roteiro_por_dia.append(dia_atual)
                        dia_atual = []
                        tempo_dia = 0
                        tempo_atual = 8 * 60
                        dia_index += 1

                        if dia_index >= len(dias_da_semana):
                            break  # excedeu número de dias disponíveis
                        # Recalcula deslocamento do hotel até novo lugar
                        tempo_desloc = self.duration.loc['HOTEL', destino]
                        deslocamento_total += tempo_desloc
                        tempo_total = tempo_visita + tempo_desloc

                    # Verifica horário de funcionamento
                    dia_semana_atual = dias_da_semana[dia_index]
                    horario_str = lugar.get(dia_semana_atual, "Closed")
                    inicio_func, fim_func = self.time_utils.parse_time_range(horario_str)
                    chegada = tempo_atual + tempo_desloc

                    if inicio_func is not None and inicio_func <= chegada <= fim_func - tempo_visita:
                        funcionamento_bonus += 1  # recompensa por estar dentro do horário
                    # else: nenhuma penalização

                    # Prioridade
                    if 'priority' in lugar and lugar['priority'] == 1:
                        prioridade_bonus += 1  # recompensa por visitar local prioritário

                    dia_atual.append(idx)
                    tempo_dia += tempo_total
                    tempo_total_usado += tempo_total
                    tempo_atual += tempo_total

                if dia_atual:
                    roteiro_por_dia.append(dia_atual)

                # Recompensas:
                # - quanto menos tempo de deslocamento, melhor
                # - quanto mais locais prioritários, melhor
                # - quanto mais locais dentro do horário, melhor
                # - quanto menos dias usados, melhor

                recompensa_total = (
                    (len(individuo) - len(roteiro_por_dia)) * 200 +  # usar menos dias
                    (prioridade_bonus * 100) +
                    (funcionamento_bonus * 50) +
                    max(1, (len(individuo) * 30 - deslocamento_total))  # recompensa por menos deslocamento
                )

                fitness_scores.append(recompensa_total)
                roteiros_por_individuo.append(roteiro_por_dia)

            return fitness_scores, roteiros_por_individuo

        except Exception as e:
            logging.exception(f"An error occurred while evaluating fitness: {e}")
            raise

    def _select_parents_by_elistism_tournament(self,
                                               fitness_scores: list[float],
                                               elitismo: int,
                                               k_torneio: int) -> list[list[int]]:
        try:
            # 1. Elitismo: mantém os melhores indivíduos
            elite_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)[:elitismo]
            elite = [self.population[i] for i in elite_indices]

            # 2. Torneio: selecionar pais
            pais = []
            while len(pais) < self.population_size - elitismo:
                competidores = random.sample(list(zip(self.population, fitness_scores)), k_torneio)
                vencedor = max(competidores, key=lambda x: x[1])[0]
                pais.append(vencedor)

            return elite, pais
        except Exception as e:
            logging.exception(f"An error occurred while selecting parents: {e}")
            raise

    def _apply_crossover_ox(self, parents: list[list[int]]) -> list[list[int]]:
        try:
            filhos = []

            for i in range(0, len(parents) - 1, 2):
                pai1 = parents[i]
                pai2 = parents[i + 1]

                if random.random() < self.crossover_rate:
                    size = len(pai1)
                    a, b = sorted(random.sample(range(size), 2))

                    # 1. Copia o meio de pai1
                    meio = pai1[a:b+1]

                    # 2. Preenche o restante com genes de pai2 na ordem, pulando os que já estão no meio
                    resto = [gene for gene in pai2 if gene not in meio]
                    filho1 = resto[:a] + meio + resto[a:]

                    # Inverte os papéis para gerar filho2
                    meio = pai2[a:b+1]
                    resto = [gene for gene in pai1 if gene not in meio]
                    filho2 = resto[:a] + meio + resto[a:]

                    filhos.append(filho1)
                    filhos.append(filho2)
                else:
                    # Sem crossover: clones
                    filhos.append(pai1[:])
                    filhos.append(pai2[:])

            # Se número ímpar, clona o último pai
            if len(parents) % 2 == 1:
                filhos.append(parents[-1][:])

            return filhos
        except Exception as e:
            logging.exception(f"An error occurred while applying crossover: {e}")
            raise
    
    def _apply_mutation(self, children: list[list[int]]) -> list[list[int]]:
        try:
            for individuo in children:
                if random.random() < self.mutation_rate:
                    for _ in range(2):  # realiza 2 trocas
                        i, j = random.sample(range(len(individuo)), 2)
                        individuo[i], individuo[j] = individuo[j], individuo[i]
            return children
        except Exception as e:
            logging.exception(f"An error occurred while applying mutation: {e}")
            raise
    
    def _apply_response_formatting(self, best_fitness: float, generation_reached: int, best_individual: list[int], roteiro_dict: dict) -> dict:
        """
        Formata a resposta do algoritmo genético para o formato esperado.
        """
        melhor_individuo_nomes = [self.places.iloc[idx]['places'] for idx in best_individual]
        
        return {
            "melhor_fitness": best_fitness,
            "geracoes_executadas": generation_reached,
            "melhor_individuo_idx": best_individual,
            "melhor_individuo_nomes": melhor_individuo_nomes,
            "roteiro_por_dia": roteiro_dict
        }

# if __name__ == "__main__":
#     try:
#         df_places = pd.read_csv("data/Osaka_Places.csv")
#         ga = TravelGeneticAlgorithm(places=df_places,
#                                     population_size=50,
#                                     generations=100,
#                                     mutation_rate=0.1,
#                                     crossover_rate=0.7,
#                                     time_min_daily=240,
#                                     start_date=datetime(2025, 10, 1),
#                                     end_date=datetime(2025, 10, 13),
#                                     hotel_coordinates=(35.0116, 135.7681))
#         logging.info("Iniciando o algoritmo genético...")
#         ga.run()
#     except Exception as e:
#         logging.exception(f"An error occurred while running the Genetic Algorithm: {e}")
#         raise