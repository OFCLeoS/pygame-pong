from geometry.colliders.box_collider import BoxCollider
from logic.shape_game_physics_object import ShapeGamePhysicsObject
from pygame import Vector2


class PaddleCollider(BoxCollider):
    def __init__(self, center: Vector2, extents: Vector2):
        super().__init__(center, extents)

    def on_collision(self, physics_object: ShapeGamePhysicsObject, collision_side: Vector2):
        # Is the physiscs object on top of the center of the collider
        y_on_top = self.center.y - physics_object.shape.collider.center.y >= 0
        # Is the physiscs object on the left of the center of the collider
        x_on_left = self.center.x - physics_object.shape.collider.center.x >= 0

        # Below is the opposite of what the collision side actually means because
        # we are looking for the collision side on the paddle, not the physics object
        if collision_side.x == 1:  # Left
            physics_object.direction.x = -abs(physics_object.direction.x)
            if y_on_top:
                physics_object.direction.y = -abs(physics_object.direction.y)
            else:
                physics_object.direction.y = abs(physics_object.direction.y)
        elif collision_side.x == -1:  # Right
            physics_object.direction.x = abs(physics_object.direction.x)
            if y_on_top:
                physics_object.direction.y = -abs(physics_object.direction.y)
            else:
                physics_object.direction.y = abs(physics_object.direction.y)
        elif collision_side.y == -1:  # Bottom
            physics_object.direction.y = abs(physics_object.direction.y)
            if x_on_left:
                physics_object.direction.x = -abs(physics_object.direction.x)
            else:
                physics_object.direction.x = abs(physics_object.direction.x)
        elif collision_side.y == 1:  # Top
            physics_object.direction.y = -abs(physics_object.direction.y)
            if x_on_left:
                physics_object.direction.x = -abs(physics_object.direction.x)
            else:
                physics_object.direction.x = abs(physics_object.direction.x)
        self.__deactive(0.5)
