# client/food.py

import random

class Food:
    def __init__(self, width, height, size=20):
        self.size = size
        self.width = width
        self.height = height
        self.respawn()

    def respawn(self):
        self.x = random.randint(0, self.width - self.size)
        self.y = random.randint(0, self.height - self.size)