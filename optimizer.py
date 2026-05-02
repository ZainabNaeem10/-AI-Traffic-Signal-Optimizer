import random
import math

class SimulatedAnnealing:
    def __init__(self, environment, cars_per_minute):
        self.environment = environment
        self.cars_per_minute = cars_per_minute

    def optimize(self, starting_temperature=100.0, cooling_rate=0.95, iterations=1000):
        """
        Optimize 4 phases using Simulated Annealing.
        State: [gn, gs, ge, gw]
        """
        total_green_time = self.environment.cycle_time - self.environment.total_clearance_time
        
        # Start from equal split (25% each)
        current_state = [total_green_time // 4] * 4
        # Adjust for rounding
        current_state[0] += total_green_time - sum(current_state)

        current_delay = self.environment.get_total_delay(*current_state, self.cars_per_minute)

        best_state = list(current_state)
        best_delay = current_delay
        temperature = starting_temperature

        for _ in range(iterations):
            # Neighbor generation: Pick two random indices, swap 1s
            next_state = list(current_state)
            idx_up, idx_down = random.sample(range(4), 2)
            
            if next_state[idx_down] > 10: # Minimum 10s green per phase
                next_state[idx_up] += 1
                next_state[idx_down] -= 1

            next_delay = self.environment.get_total_delay(*next_state, self.cars_per_minute)
            change_in_delay = next_delay - current_delay

            if change_in_delay < 0 or (temperature > 0 and random.random() < math.exp(-change_in_delay / temperature)):
                current_state = next_state
                current_delay = next_delay

                if current_delay < best_delay:
                    best_state = list(current_state)
                    best_delay = current_delay

            temperature *= cooling_rate

        return (*best_state, best_delay)


class HillClimbing:
    def __init__(self, environment, cars_per_minute):
        self.environment = environment
        self.cars_per_minute = cars_per_minute

    def optimize(self, max_iterations=100):
        """
        Optimize 4 phases using Hill Climbing.
        """
        total_green_time = self.environment.cycle_time - self.environment.total_clearance_time
        current_state = [total_green_time // 4] * 4
        current_state[0] += total_green_time - sum(current_state)
        
        current_delay = self.environment.get_total_delay(*current_state, self.cars_per_minute)

        for _ in range(max_iterations):
            improvement_found = False
            
            # Explore all possible +/- 1 swaps between any two phases
            for i in range(4):
                for j in range(4):
                    if i == j: continue
                    
                    next_state = list(current_state)
                    if next_state[j] > 10:
                        next_state[i] += 1
                        next_state[j] -= 1
                        
                        next_delay = self.environment.get_total_delay(*next_state, self.cars_per_minute)
                        if next_delay < current_delay:
                            current_state = next_state
                            current_delay = next_delay
                            improvement_found = True
                            break # Greedy: take first improvement
                if improvement_found: break
            
            if not improvement_found:
                break

        return (*current_state, current_delay)

class GeneticAlgorithm:
    def __init__(self, environment, cars_per_minute):
        self.environment = environment
        self.cars_per_minute = cars_per_minute

    def fitness(self, state):
        delay = self.environment.get_total_delay(*state, self.cars_per_minute)
        return 1 / (1 + delay)

    def optimize(self, population_size=12, generations=40, mutation_rate=0.2):
        """
        Optimize 4 phases using Genetic Algorithm.
        """
        total_green_time = self.environment.cycle_time - self.environment.total_clearance_time

        # Initial population: random splits that sum to total_green_time
        population = []
        for _ in range(population_size):
            p = [10, 10, 10, 10]
            remaining = total_green_time - 40
            for i in range(3):
                add = random.randint(0, remaining)
                p[i] += add
                remaining -= add
            p[3] += remaining
            population.append(p)

        best_state = population[0]
        best_delay = self.environment.get_total_delay(*best_state, self.cars_per_minute)

        for _ in range(generations):
            population.sort(key=self.fitness, reverse=True)
            
            current_best = population[0]
            current_delay = self.environment.get_total_delay(*current_best, self.cars_per_minute)
            
            if current_delay < best_delay:
                best_state = list(current_best)
                best_delay = current_delay

            new_population = population[:2] # Elitism

            while len(new_population) < population_size:
                p1, p2 = random.sample(population[:6], 2)
                
                # Crossover: Average and adjust
                child = [(a + b) // 2 for a, b in zip(p1, p2)]
                
                # Mutation
                if random.random() < mutation_rate:
                    i, j = random.sample(range(4), 2)
                    if child[j] > 10:
                        child[i] += 1
                        child[j] -= 1
                
                # Adjust sum
                diff = total_green_time - sum(child)
                child[0] += diff
                
                # Ensure min green
                for i in range(4):
                    if child[i] < 10:
                        diff = 10 - child[i]
                        child[i] = 10
                        # steal from largest
                        max_idx = child.index(max(child))
                        child[max_idx] -= diff

                new_population.append(child)

            population = new_population

        return (*best_state, best_delay)