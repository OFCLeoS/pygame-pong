from abc import ABC, abstractmethod
from logic.shape_game_physics_object import ShapeGamePhysicsObject
from pygame import Vector2
import threading


class BoxCollider(ABC):
    def __init__(self, center: Vector2, extents: Vector2):
        self.active = True
        self.center = center
        self.extents = extents

    @abstractmethod
    def on_collision(self, physics_object: ShapeGamePhysicsObject, collision_side: Vector2):
        pass

    def __activate(self):
        self.active = True

    # TODO: Sure about using multiple threads?
    def __deactive(self, delay: float):
        self.active = False
        t = threading.Timer(delay, self.__activate)
        t.start()
