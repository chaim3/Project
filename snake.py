# client/snake.py

class Snake:
    def __init__(self, x, y, size=20, speed=20):
        self.size = size
        self.speed = speed
        self.direction = "RIGHT"
        self.body = [(x, y)]
        self.length = 1

    def move(self):
        x, y = self.body[0]

        if self.direction == "UP":
            y -= self.speed
        elif self.direction == "DOWN":
            y += self.speed
        elif self.direction == "LEFT":
            x -= self.speed
        elif self.direction == "RIGHT":
            x += self.speed

        self.body.insert(0, (x, y))

        if len(self.body) > self.length:
            self.body.pop()

    def grow(self):
        self.length += 1  # smooth snake grows gradually

    def set_direction(self, direction):
        # prevent reversing into itself
        opposite = {
            "UP": "DOWN",
            "DOWN": "UP",
            "LEFT": "RIGHT",
            "RIGHT": "LEFT"
        }
        if direction != opposite.get(self.direction):
            self.direction = direction