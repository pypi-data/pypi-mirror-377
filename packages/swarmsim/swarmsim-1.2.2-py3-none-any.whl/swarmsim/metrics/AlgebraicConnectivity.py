import numpy as np
from typing import List
from .AbstractMetric import AbstractMetric


class AlgebraicConn(AbstractMetric):
    def __init__(self, history=100, r_disk_size=10):
        super().__init__(name="Alg_Connectivity", history_size=history)
        self.population = None
        self.r_disk_size = r_disk_size

    def attach_world(self, world):
        super().attach_world(world)
        self.population = world.population

    def getLapacianMatrix(self):
        n = len(self.population)
        matrix = np.zeros((n, n))
        r_d2 = self.r_disk_size ** 2
        for i, agent_i in enumerate(self.population):
            for j in range(i + 1, n):
                agent_j = self.population[j]
                dist_p2 = ((agent_i.x_pos - agent_j.x_pos) ** 2) + ((agent_i.y_pos - agent_j.y_pos) ** 2)
                if dist_p2 < r_d2:
                    matrix[i][i] += 1
                    matrix[j][i] = -1
                    matrix[j][j] += 1
                    matrix[i][j] = -1
        return matrix

    def calculate(self):
        m = self.getLapacianMatrix()
        eigen_values = np.linalg.eig(m)[0]
        eigen_values.sort()
        a_conn = eigen_values[1]
        if a_conn != 0:
            a_conn = 1
        self.set_value(np.real(a_conn))
