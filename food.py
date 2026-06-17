# client/food.py

import random  # random placement for food

class Food:
    def __init__(self, width, height, size=20):
        self.size = size  # food square size
        self.width = width  # canvas width bound
        self.height = height  # canvas height bound
        self.respawn()  # place initial food

    def respawn(self):
        self.x = random.randint(0, self.width - self.size)  # random x position
        self.y = random.randint(0, self.height - self.size)  # random y position