# genetic_algorithm.py

import random
import pandas as pd
from geopy.distance import geodesic

# Fixed hotel coordinates (example: Hotel Paris Bastille)
HOTEL_COORDS = ("Hotel", 48.853, 2.370)  # latitude, longitude

def calculate_distance(point1, point2):
    return geodesic(point1, point2).kilometers

def total_route_distance(route):
    total = 0.0
    current = HOTEL_COORDS
    for point in route:
        point_la = point[1]  # latitude
        point_lo = point[2]  # longitude
        current_la = current[1]  # latitude
        current_lo = current[2]  # longitude
        total += calculate_distance((current_la, current_lo), (point_la, point_lo))
        current = point  # update current to the next point's coordinates
    total += calculate_distance(current[1:3], HOTEL_COORDS[1:3])  # return to hotel
    return total

def create_initial_population(locations, size=50):
    return [random.sample(locations, len(locations)) for _ in range(size)]

def crossover(parent1, parent2):
    cut = random.randint(1, len(parent1) - 2)
    child = parent1[:cut]
    child += [p for p in parent2 if p not in child]
    return child

def mutate(route, mutation_rate=0.1):
    for i in range(len(route)):
        if random.random() < mutation_rate:
            j = random.randint(0, len(route) - 1)
            route[i], route[j] = route[j], route[i]
    return route

def select_parents(population, fitnesses):
    sorted_population = [x for _, x in sorted(zip(fitnesses, population))]
    return sorted_population[:2]  # best two

def run_genetic_algorithm(locations: list[tuple[str, str]], generations=100, population_size=50):
    population = create_initial_population(locations, population_size)
    best_route, best_distance = None, float('inf')
    for gen in range(generations):
        fitnesses = [total_route_distance(route) for route in population]
        best_idx = fitnesses.index(min(fitnesses))
        if fitnesses[best_idx] < best_distance:
            best_distance = fitnesses[best_idx]
            best_route = population[best_idx]

        new_population = []
        for _ in range(population_size):
            p1, p2 = select_parents(population, fitnesses)
            child = crossover(p1, p2)
            child = mutate(child)
            new_population.append(child)
        population = new_population

    return best_route, best_distance

if __name__ == "__main__":
    df = pd.read_csv("data/places_with_coords_mock.csv")
    locations = list(zip(df["places"], df["latitude"], df["longitude"]))
    best_route, best_distance = run_genetic_algorithm(locations)
    print(f"Best route found with total distance: {best_distance:.2f} km")
