from typing import List

from pygame import Vector2
from pygame.key import ScancodeWrapper
from geometry.shape import Shape
from geometry.box_collider import BoxCollider
from logic.shape_game_physics_object import ShapeGamePhysicsObject


class PhysicsSystem:
    def __init__(self, inital_colliders: List[BoxCollider] = [], initial_physics_objects: List[ShapeGamePhysicsObject] = []):
        self.colliders = inital_colliders
        self.physics_objects = initial_physics_objects

    def handle_physics(self):
        for physics_objects in self.physics_objects:
            pass
    
    @staticmethod
    def is_colliding(collider1: BoxCollider, collider2: BoxCollider) -> bool:
        return False
        # return (
        #     collider1.center.x < collider2.center.x + collider2.extents.x and
        #     a.x + a.w > b.x and
        #     a.y < b.y + b.h and
        #     a.y + a.h > b.y
        # )
    
    @staticmethod
    def get_collision_side(collider1: BoxCollider, collider2: BoxCollider):
        # Centers

        dx = collider1.center.x - collider2.center.x
        dy = collider1.center.y - collider2.center.y

        overlap_x = (collider1.extents.x + collider2.extents.x) - abs(dx)
        overlap_y = (collider1.extents.y + collider2.extents.y) - abs(dy)

        if overlap_x < overlap_y:
            # Horizontal collision
            if dx > 0:
                return "left"   # a hit b on its left side
            else:
                return "right"
        else:
            # Vertical collision
            if dy > 0:
                return "top"
            else:
                return "bottom"
