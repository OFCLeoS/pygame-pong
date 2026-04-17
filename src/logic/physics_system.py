from typing import List

from pygame import Vector2
from pygame.key import ScancodeWrapper
from geometry.shape import Shape
from geometry.colliders.box_collider import BoxCollider
from logic.shape_game_physics_object import ShapeGamePhysicsObject


class PhysicsSystem:
    """
        Handles the in-game physics system
    """
    def __init__(self, inital_colliders: List[BoxCollider] = [], initial_physics_objects: List[ShapeGamePhysicsObject] = []):
        self.colliders = inital_colliders
        self.physics_objects = initial_physics_objects

    def handle_physics(self,delta_time):
        for physics_object in self.physics_objects:
            physics_object.tick(delta_time)
            object_collider = physics_object.shape.collider
            for collider in self.colliders:
                # Physics Object cannot collide with itself
                if collider.active and collider != object_collider and PhysicsSystem.is_colliding(object_collider, collider):
                    side = PhysicsSystem.get_collision_side(object_collider, collider)
                    collider.on_collision(physics_object,side)
                    # WHEN BALL HITS PADLE -> COLLISION DISABLED ON PADLE
                    break

    @staticmethod
    def is_colliding(collider1: BoxCollider, collider2: BoxCollider) -> bool:
        return (
            collider1.center.x-collider1.extents.x < collider2.center.x-collider2.extents.x + (collider2.extents.x*2) and
            collider1.center.x-collider1.extents.x + (collider1.extents.x*2) > collider2.center.x-collider2.extents.x and
            collider1.center.y-collider1.extents.y < collider2.center.y-collider2.extents.y + (collider2.extents.y*2) and
            collider1.center.y-collider1.extents.y +
            (collider1.extents.y * 2) > collider2.center.y-collider2.extents.y
        )

    @staticmethod
    def get_collision_side(collider1: BoxCollider, collider2: BoxCollider) -> Vector2:
        # Centers

        dx = collider1.center.x - collider2.center.x
        dy = collider1.center.y - collider2.center.y

        overlap_x = (collider1.extents.x + collider2.extents.x) - abs(dx)
        overlap_y = (collider1.extents.y + collider2.extents.y) - abs(dy)

        if overlap_x < overlap_y:
            # Horizontal collision
            if dx > 0:
                return Vector2(-1, 0)  # a hit b on its left side
            else:
                return Vector2(1, 0)  # a hit b on its right side
        else:
            # Vertical collision
            if dy > 0:
                return Vector2(0, -1)  # a hit b on its top side
            else:
                return Vector2(0, 1)  # a hit b on its bottom side
