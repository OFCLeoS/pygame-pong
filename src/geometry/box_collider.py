from pygame import Vector2

class BoxCollider:
    def __init__(self, center: Vector2, extents: Vector2):
        self.center = center
        self.extents = extents