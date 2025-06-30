import random
import pandas as pd
from geopy.distance import geodesic
from datetime import datetime, timedelta

# Fixed hotel coordinates (example: Hotel Paris Bastille)
HOTEL_COORDS = (48.853, 2.370)  # latitude, longitude
DAY_MAP = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def calculate_distance(point1, point2):
    return geodesic(point1, point2).kilometers

def total_route_distance(route):
    total = 0.0
    current = HOTEL_COORDS
    for point in route:
        point_la = point[0]  # latitude
        point_lo = point[1]  # longitude
        current_la = current[0]  # latitude
        current_lo = current[1]  # longitude
        total += calculate_distance((current_la, current_lo), (point_la, point_lo))
        current = point  # update current to the next point's coordinates
    total += calculate_distance(current, HOTEL_COORDS)  # return to hotel
    return total

def is_open_on_day(row, weekday_index):
    day_col = DAY_MAP[weekday_index % 7]
    return bool(row[day_col])

def filter_open_locations_for_day(df, weekday_index):
    open_places = []
    for _, row in df.iterrows():
        if is_open_on_day(row, weekday_index):
            open_places.append((row["places"], row["latitude"], row["longitude"]))
    return open_places

def create_initial_population(locations, size=50):
    return [random.sample(locations, len(locations)) for _ in range(size)]

def crossover(parent1, parent2):
    if len(parent1) < 2:
        return parent1.copy()
    cut = random.randint(1, len(parent1) - 1)
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

def run_genetic_algorithm_for_multiple_days(df, start_date, end_date, generations=100, population_size=50):
    day_results = []
    current_date = start_date
    while current_date <= end_date:
        weekday_index = current_date.weekday()
        open_locations = filter_open_locations_for_day(df, weekday_index)
        coords_list = [(lat, lon) for _, lat, lon in open_locations]

        if len(coords_list) < 2:
            day_results.append({"date": current_date, "route": open_locations, "distance": 0.0})
            current_date += timedelta(days=1)
            continue

        population = create_initial_population(coords_list, population_size)
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

        name_lookup = {(row["latitude"], row["longitude"]): row["places"] for _, row in df.iterrows()}
        named_route = [(name_lookup[lat, lon], lat, lon) for lat, lon in best_route]

        day_results.append({"date": current_date, "route": named_route, "distance": best_distance})
        current_date += timedelta(days=1)

    return day_results

if __name__ == "__main__":
    df = pd.read_csv("data/places_with_coords_mock.csv")
    start = datetime.today()
    end = start + timedelta(days=2)
    results = run_genetic_algorithm_for_multiple_days(df, start, end)
    for day_result in results:
        print(f"{day_result['date'].strftime('%A')}: {day_result['distance']:.2f} km")