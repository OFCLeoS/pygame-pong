import pygame
from pygame import Vector2
from pygame.key import ScancodeWrapper
from geometry.shape import Shape


class ShapeController:
    def __init__(self, shape: Shape, key_to_direction: dict[int, Vector2],min_y_pos: int, max_y_pos: int):
        self.direction = Vector2(0, 0)
        self.shape = shape
        self.key_to_direction = key_to_direction
        self.min_y_pos = min_y_pos
        self.max_y_pos = max_y_pos

    def handle_movement(self, keys_pressed: ScancodeWrapper):
        for key in self.key_to_direction:
            if keys_pressed[key]:
                new_position = self.shape.get_position() + self.key_to_direction[key]
                
                if new_position.y > self.max_y_pos:
                    new_position.y = self.max_y_pos
                elif new_position.y < self.min_y_pos:
                    new_position.y = self.min_y_pos
                    
                self.shape.set_position(new_position)
