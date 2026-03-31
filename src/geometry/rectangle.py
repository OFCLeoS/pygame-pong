from pygame import Vector2
from pygame import Color
from pygame import Rect

from geometry.shape import Shape


class Rectangle(Shape):
    def __init__(self, size: Vector2, starting_pos: Vector2, colour: Color):
        super().__init__(starting_pos, colour, Vector2(starting_pos.x+(size.x/2),
                                                       starting_pos.y+(size.y/2)), Vector2(size.x/2, size.y/2))
        self.rect_like = Rect(starting_pos, size)
        self.colour = colour

    def set_position(self, position: Vector2):
        self._position = position
        self.rect_like.left = position.x
        self.rect_like.top = position.y
        self.box_collider.center = Vector2(
            position.x+(self.rect_like.width/2), position.y+(self.rect_like.height/2))
