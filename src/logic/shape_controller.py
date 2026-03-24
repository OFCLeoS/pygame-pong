import pygame
from pygame import Vector2
from pygame.key import ScancodeWrapper
from geometry.shape import Shape


class ShapeController:
    def __init__(self, shape: Shape, key_to_direction: dict[int, Vector2]):
        self.direction = Vector2(0, 0)
        self.shape = shape
        self.key_to_direction = key_to_direction

    def handle_movement(self, keys_pressed: ScancodeWrapper):
        for key in self.key_to_direction:
            if keys_pressed[key]:
                self.shape.set_position(
                    self.shape.get_position() + self.key_to_direction[key])
