import pygame
from pygame import Vector2
from pygame.key import ScancodeWrapper
# from geometry.shape import Shape

class ShapeGamePhysicsObject:
    def __init__(self, shape, direction: Vector2 = Vector2(0,0)):
        self.shape = shape
        self.direction = direction

    def tick(self):
        last_shape_position = self.shape.get_position()
        self.shape.set_position(last_shape_position+self.direction)