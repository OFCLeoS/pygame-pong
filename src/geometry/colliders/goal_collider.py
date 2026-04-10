from geometry.colliders.box_collider import BoxCollider
from logic.shape_game_physics_object import ShapeGamePhysicsObject
from logic.goal_manager import GoalManager
from pygame import Vector2


class GoalCollider(BoxCollider):
    def __init__(self, center: Vector2, extents: Vector2, player_id: int, goal_manager: GoalManager):
        super().__init__(center, extents)
        self.player_id = player_id
        self.goal_manager = goal_manager

    def on_collision(self, physics_object: ShapeGamePhysicsObject, collision_side: Vector2):
        self.goal_manager.score(self.player_id)
