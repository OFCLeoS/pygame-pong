from pygame import Vector2
from pygame import Color

from geometry.shape import Shape


class Circle(Shape):
    def __init__(self, radius: float, starting_pos: Vector2, colour: Color):
        super().__init__(starting_pos, colour, starting_pos, Vector2(radius, radius))
        self.radius = radius
        self.colour = colour

    def set_position(self, position: Vector2):
        self._position = position
        self.box_collider.center = position
