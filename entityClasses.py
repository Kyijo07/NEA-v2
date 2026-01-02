class Entity:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class StationaryEntity(Entity):
    def __init__(self, x, y, width, height, colour):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.colour = colour

class MovingEntity(StationaryEntity):
    def __init__(self, x, y, width, height, colour, speed):
        super().__init__(x, y, width, height, colour)
        self.speed = speed

