from abc import ABC, abstractmethod
from pygame import Vector2


class Shape(ABC):
    def __init__(self, starting_pos: Vector2):
        self._position = starting_pos

    def get_position(self):
        return self._position

    @abstractmethod
    def set_position(self, position: Vector2):
        pass