from abc import ABC, abstractmethod
from pygame import Color
from pygame import Vector2

from geometry.colliders.box_collider import BoxCollider


class Shape(ABC):
    def __init__(self, starting_pos: Vector2, colour:  Color, collider: BoxCollider):
        self._position = starting_pos
        self.colour = colour
        self.collider = collider

    def get_position(self):
        return self._position

    @abstractmethod
    def set_position(self, position: Vector2):
        pass
