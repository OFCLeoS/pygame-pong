from pygame import Vector2
from pygame import Color
from pygame import Rect

from geometry.shape import Shape


class Rectangle(Shape):
    def __init__(self, size: Vector2, starting_pos: Vector2, colour: Color):
        super().__init__(starting_pos)
        self.rect_like = Rect(starting_pos, size)
        self.colour = colour

    def set_position(self, position: Vector2):
        self._position = position
        self.rect_like.left = position.x
        self.rect_like.top = position.y
        pass
