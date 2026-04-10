from geometry.colliders.box_collider import BoxCollider
from logic.shape_game_physics_object import ShapeGamePhysicsObject
from pygame import Vector2


class WallCollider(BoxCollider):
    def __init__(self, center: Vector2, extents: Vector2):
        super().__init__(center, extents)

    def on_collision(self, physics_object: ShapeGamePhysicsObject, collision_side: Vector2):
        physics_object.direction.y = -physics_object.direction.y
