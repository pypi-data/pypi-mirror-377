import numpy as np
from typing import List
from .AbstractMetric import AbstractMetric


class RadialVarianceMetric(AbstractMetric):
    __badvars__ = AbstractMetric.__badvars__ + ['population']  # references to population may cause pickling errors

    def __init__(self, history=100, regularize=True):
        super().__init__(name="Radial_Variance", history_size=history)
        self.population = None
        self.world_radius = 0
        self.regularize = regularize

    def attach_world(self, world):
        super().attach_world(world)
        self.population = world.population
        self.world_radius = world.config.radius

    def calculate(self):
        n = len(self.population)
        r = self.world_radius
        mew = self.center_of_mass()

        # Calculate the Average distance from C.O.M. for all agents first, save to variable 'avg_dist'
        distance_list = []
        for agent in self.population:
            x_i = agent.getPosition()
            distance = np.linalg.norm(x_i - mew)
            distance_list.append(distance)
        avg_dist = np.average(distance_list)

        variance_list = []
        for agent in self.population:
            x_i = agent.getPosition()
            distance = np.linalg.norm(x_i - mew)
            variance = (distance - avg_dist) ** 2  # Square to make positive(?)
            variance_list.append(variance)

        scaling_factor = (1 / (r * r * n)) if self.regularize else (1 / n)
        radial_variance = sum(variance_list) * scaling_factor

        WEIGHT = 20.0
        self.set_value(radial_variance * WEIGHT)

    def center_of_mass(self):
        positions = np.asarray([agent.getPosition() for agent in self.population])
        return positions.mean(axis=0)
