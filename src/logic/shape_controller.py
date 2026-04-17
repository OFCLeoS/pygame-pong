import pygame
from pygame import Vector2
from pygame.key import ScancodeWrapper
from geometry.shape import Shape


class ShapeController:
    """
        ALlows a user to control a shape with their keyboard
    """
    def __init__(self, shape: Shape, key_to_direction: dict[int, Vector2],min_y_pos: int, max_y_pos: int):
        self.direction = Vector2(0, 0)
        self.shape = shape
        self.key_to_direction = key_to_direction
        self.min_y_pos = min_y_pos
        self.max_y_pos = max_y_pos

    def handle_movement(self, keys_pressed: ScancodeWrapper,delta_time):
        for key in self.key_to_direction:
            if keys_pressed[key]:
                # We multiply by dt so the speed of iterations dont affect the player speed
                new_position = self.shape.get_position() + (self.key_to_direction[key]*delta_time)
                
                if new_position.y > self.max_y_pos:
                    new_position.y = self.max_y_pos
                elif new_position.y < self.min_y_pos:
                    new_position.y = self.min_y_pos
                    
                self.shape.set_position(new_position)
