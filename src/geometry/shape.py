from abc import ABC, abstractmethod
from pygame import Color
from pygame import Vector2

from geometry.box_collider import BoxCollider


class Shape(ABC):
    def __init__(self, starting_pos: Vector2, colour:  Color, box_collider_center: Vector2, box_collider_extents: Vector2):
        self._position = starting_pos
        self.colour = colour
        self.box_collider = BoxCollider(
            box_collider_center, box_collider_extents)

    def get_position(self):
        return self._position

    @abstractmethod
    def set_position(self, position: Vector2):
        pass
