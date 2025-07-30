import pandas as pd
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TravelGeneticAlgorithm:
    def __init__(self,
                 population_size: int,
                 mutation_rate: int,
                 crossover_rate: int,
                 generations:int,
                 time_min_daily:int,
                 tasks: pd.DataFrame | None = None):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generations = generations
        self.time_min_daily = time_min_daily
        self.population = pd.DataFrame()
        self.tasks = tasks if tasks is not None else pd.DataFrame()

    def run(self) -> None:
        self.population = self._initialize_population()
        for generation in range(self.generations):
            fitness_scores = self._evaluate_fitness()

    def _initialize_population(self) -> None:
        # Initialize the population with random individuals
        try:
            df_places_to_visit = pd.read_csv("data/places_with_coords_mock.csv")
            print(df_places_to_visit)
            df_places_to_visit_sorted = df_places_to_visit.sort_values(by="priority", ascending=False)
            #places_name = df_places_to_visit_sorted["places"].tolist()
            indices = list(df_places_to_visit_sorted.index)
            
            population = []
            for _ in range(self.population_size):
                individual = random.sample(indices, len(indices))
                population.append(individual)
            return population
        except FileNotFoundError:
            logging.exception("Error: The tasks.csv file was not found. Please ensure it exists in the data directory.")
            raise
        except pd.errors.EmptyDataError: 
            logging.exception("Error: The tasks.csv file is empty. Please provide valid data.")
            raise
        except pd.errors.ParserError:
            logging.exception("Error: There was a parsing error with the tasks.csv file. Please check its format.")
            raise
        except Exception as e:
            logging.exception(f"An error occurred while initializing the population: {e}")
            raise


    def _evaluate_fitness(self) -> list[float]:
        try: 
            ...
        except Exception as e:
            logging.exception(f"An error occurred while evaluating fitness: {e}")
            raise


    def _select_parents_by_ranking(self, fitness_scores: list[float], num_parents: int) -> list[list[int]]:
        ranked = sorted(zip(self.population, fitness_scores), key=lambda x: x[1])
        total = len(ranked)
        weights = [i + 1 for i in range(total)]
        selected = random.choices(
            [ind for ind, _ in ranked],
            weights=weights,
            k=num_parents
        )
        return selected

    def _crossover_and_mutate(self, parents: list[list[int]]) -> list[list[int]]:
        children = []

        for _ in range(len(parents) // 2):
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)

            # Crossover
            if random.random() < self.crossover_rate:
                # 1. Sorteia dois pontos de corte
                a, b = sorted(random.sample(range(len(parent1)), 2))
                slice1 = parent1[a:b]

                # 2. Preenche com genes do parent2, pulando os da fatia
                rest = [gene for gene in parent2 if gene not in slice1]
                child = rest[:a] + slice1 + rest[a:]
            else:
                # Sem crossover: clona um pai
                child = parent1[:]

            # Mutação
            if random.random() < self.mutation_rate:
                i, j = random.sample(range(len(child)), 2)
                child[i], child[j] = child[j], child[i]  # swap

            children.append(child)

        # Garante população completa (em caso de número ímpar)
        while len(children) < self.population_size:
            children.append(random.choice(parents))

        return children


if __name__ == "__main__":
    try:
        ga = TravelGeneticAlgorithm(population_size=50,
                                    mutation_rate=0.01,
                                    crossover_rate=0.7,
                                    generations=100,
                                    time_min_daily=240)
        ga.run()
    except Exception as e:
        logging.exception(f"An error occurred while running the Genetic Algorithm: {e}")
        raise