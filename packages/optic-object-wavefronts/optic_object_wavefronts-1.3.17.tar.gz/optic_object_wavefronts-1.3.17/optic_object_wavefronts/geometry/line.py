import numpy as np


class Line:
    def __init__(self, start, stop):
        start = np.array(start)
        stop = np.array(stop)
        self.support = start
        self.length = np.linalg.norm(stop - start)
        self.direction = (stop - start) / self.length

    def parameter_for_closest_distance_to_point(self, point):
        point = np.array(point)
        d = np.dot(self.direction, point)
        return d - np.dot(self.support, self.direction)

    def at(self, parameter):
        return self.support + parameter * self.direction

    def projection_of_point(self, point):
        point = np.array(point)
        parameter = self.parameter_for_closest_distance_to_point(point)
        if 0 <= parameter <= self.length:
            return self.at(parameter)
        else:
            None

    def closest_distence(self, point):
        point = np.array(point)
        param = self.parameter_for_closest_distance_to_point(point)
        clspoint = self.at(param)
        return np.linalg.norm(point - clspoint)
