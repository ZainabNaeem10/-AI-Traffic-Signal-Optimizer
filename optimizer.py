import random
import math

class SimulatedAnnealing:
    def __init__(self, environment, cars_per_minute):
        self.environment = environment
        self.cars_per_minute = cars_per_minute

    def optimize(self, starting_temperature=100.0, cooling_rate=0.99, iterations=2000):

        total_green_time = self.environment.cycle_time - self.environment.total_clearance_time

        # Start from equal split
        current_ns_green = total_green_time // 2
        current_delay = self.environment.get_total_delay(
            current_ns_green,
            total_green_time - current_ns_green,
            self.cars_per_minute
        )

        best_ns_green = current_ns_green
        best_delay = current_delay
        temperature = starting_temperature

        for _ in range(iterations):

            step = random.choice([-1, 1])

            # Keep minimum green of 15 seconds
            next_ns_green = max(
                15,
                min(current_ns_green + step, total_green_time - 15)
            )

            next_delay = self.environment.get_total_delay(
                next_ns_green,
                total_green_time - next_ns_green,
                self.cars_per_minute
            )

            change_in_delay = next_delay - current_delay

            # Accept better solutions or probabilistically accept worse ones
            if change_in_delay < 0 or (
                temperature > 0 and random.random() < math.exp(-change_in_delay / temperature)
            ):
                current_ns_green = next_ns_green
                current_delay = next_delay

                if current_delay < best_delay:
                    best_ns_green = current_ns_green
                    best_delay = current_delay

            temperature *= cooling_rate

        return int(best_ns_green), int(total_green_time - best_ns_green), best_delay


class HillClimbing:
    def __init__(self, environment, cars_per_minute):
        self.environment = environment
        self.cars_per_minute = cars_per_minute

    def optimize(self, max_iterations=50):

        total_green_time = self.environment.cycle_time - self.environment.total_clearance_time

        current_ns_green = total_green_time // 2
        current_delay = self.environment.get_total_delay(
            current_ns_green,
            total_green_time - current_ns_green,
            self.cars_per_minute
        )

        for _ in range(max_iterations):
            improvement_found = False

            for step in [-1, 1]:
                next_ns_green = current_ns_green + step

                if 15 <= next_ns_green <= total_green_time - 15:

                    next_delay = self.environment.get_total_delay(
                        next_ns_green,
                        total_green_time - next_ns_green,
                        self.cars_per_minute
                    )

                    if next_delay < current_delay:
                        current_ns_green = next_ns_green
                        current_delay = next_delay
                        improvement_found = True
                        break  # take first improvement

            if not improvement_found:
                break  # local optimum reached

        return int(current_ns_green), int(total_green_time - current_ns_green), current_delay
    
class GeneticAlgorithm:
    def __init__(self, environment, cars_per_minute):
        self.environment = environment
        self.cars_per_minute = cars_per_minute

    def fitness(self, ns_green, total_green_time):
        delay = self.environment.get_total_delay(
            ns_green,
            total_green_time - ns_green,
            self.cars_per_minute
        )
        return 1 / (1 + delay)

    def optimize(self, population_size=10, generations=50, mutation_rate=0.1):

        total_green_time = (
            self.environment.cycle_time
            - self.environment.total_clearance_time
        )

        # Initial population
        population = [
            random.randint(15, total_green_time - 15)
            for _ in range(population_size)
        ]

        best_ns = population[0]
        best_delay = self.environment.get_total_delay(
            best_ns,
            total_green_time - best_ns,
            self.cars_per_minute
        )

        for _ in range(generations):

            # Sort by fitness
            population.sort(
                key=lambda x: self.fitness(x, total_green_time),
                reverse=True
            )

            # Best current solution
            current_best = population[0]
            current_delay = self.environment.get_total_delay(
                current_best,
                total_green_time - current_best,
                self.cars_per_minute
            )

            if current_delay < best_delay:
                best_ns = current_best
                best_delay = current_delay

            new_population = population[:2]  # elitism

            while len(new_population) < population_size:
                parent1, parent2 = random.sample(population[:4], 2)

                # Crossover
                child = (parent1 + parent2) // 2

                # Mutation
                if random.random() < mutation_rate:
                    child += random.choice([-1, 1])

                child = max(15, min(child, total_green_time - 15))

                new_population.append(child)

            population = new_population

        return best_ns, total_green_time - best_ns, best_delay