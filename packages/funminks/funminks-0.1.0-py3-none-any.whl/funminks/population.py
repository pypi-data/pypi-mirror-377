'''A population of minks (individuals) carrying a genome (code version).
A population script is an object that manages a collection of individuals (minks), and calculates 
metrics of fitness and selection at this emergent level.
'''

import random
from typing import List
from .mink_llm_based import Mink




class Population:
    def __init__(self, pop_size: int, seed_code: str, datapoints: str, prompt: str, llm_params):
        self.pop_size = pop_size
        self.datapoints = datapoints
        self.prompt = prompt
        self.seed_code = seed_code
        self.llm_params = llm_params
        self.minks: List[Mink] = [Mink(datapoints=self.datapoints, prompt=self.prompt, genome=self.seed_code, llm_params=self.llm_params) for _ in range(self.pop_size)]
        self.best_mink_and_fitness = None  # To store the best mink and its fitness score
        
    def evaluate_fitness(self):
        self.avg_fitness = 0
        for mink in self.minks:
            _mink_fitness = mink.calculate_fitness()
            self.avg_fitness += _mink_fitness
        self.avg_fitness /= len(self.minks)


    def select_parents(self):
        # Select parents based on fitness scores (e.g., tournament selection)
        self.minks.sort(key=lambda mink: mink.fitness_score, reverse=True)
        # if the best mink in this generation has a higher (closer to 0) score than the previous best, update best_mink_and_fitness
        if self.best_mink_and_fitness is None or self.minks[0].fitness_score > self.best_mink_and_fitness["fitness"]:
            self.best_mink_and_fitness = {"genome": self.minks[0].genome, "fitness": self.minks[0].fitness_score}
        self.parents = self.minks[:10]

    def create_offspring(self):
        # Create new offspring through crossover and mutation
        offspring = []
        # Introduce the best mink from the previous generation to preserve exploration over best solution
        if self.best_mink_and_fitness is not None:
            best_mink = Mink(datapoints=self.datapoints, prompt=self.prompt, genome=self.best_mink_and_fitness["genome"], llm_params=self.llm_params)
            offspring.append(best_mink)
        # Fill the rest of the population with offspring from parents
        _total_offspring = self.pop_size if self.best_mink_and_fitness is None else self.pop_size - 1
        for _ in range(_total_offspring):
            parent = random.choice(self.parents)
            parent_genome = parent.genome
            child = Mink(datapoints=self.datapoints, prompt=self.prompt, genome=parent_genome)
            child.mutate()
            offspring.append(child)
        self.minks = offspring

    def run_episode(self):
        self.evaluate_fitness()
        self.select_parents()
        self.create_offspring()