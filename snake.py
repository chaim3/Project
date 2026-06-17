# client/snake.py

class Snake:
    def __init__(self, x, y, size=20, speed=20):
        self.size = size  # width/height of each segment
        self.speed = speed  # movement increment in pixels
        self.direction = "RIGHT"  # current move direction
        self.body = [(x, y)]  # list of segment positions, head first
        self.length = 1  # how many segments snake should keep

    def move(self):
        x, y = self.body[0]  # current head position

        if self.direction == "UP":
            y -= self.speed  # move up
        elif self.direction == "DOWN":
            y += self.speed  # move down
        elif self.direction == "LEFT":
            x -= self.speed  # move left
        elif self.direction == "RIGHT":
            x += self.speed  # move right

        self.body.insert(0, (x, y))  # insert new head position

        if len(self.body) > self.length:
            self.body.pop()  # remove tail if not growing

    def grow(self):
        self.length += 1  # increase snake length

    def set_direction(self, direction):
        opposite = {
            "UP": "DOWN",
            "DOWN": "UP",
            "LEFT": "RIGHT",
            "RIGHT": "LEFT",
        }
        if direction != opposite.get(self.direction):
            self.direction = direction  # change direction if valid