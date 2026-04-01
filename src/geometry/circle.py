from pygame import Vector2
from pygame import Color

#from geometry.colliders.box_collider import BoxCollider
from geometry.shape import Shape


class Circle(Shape):
    def __init__(self, radius: float, starting_pos: Vector2, colour: Color, collider):
        super().__init__(starting_pos, colour, collider)
        self.radius = radius
        self.colour = colour

    def set_position(self, position: Vector2):
        self._position = position
        self.collider.center = position
