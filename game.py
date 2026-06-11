# client/game.py

import tkinter as tk
from snake import Snake
from food import Food
from network_listener import NetworkListener
from encryption_manager import EncryptionManager
import os

WIDTH = 600
HEIGHT = 400

class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cyber Snake")

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()

        self.snake = Snake(100, 100)
        self.food = Food(WIDTH, HEIGHT)
        self.enc_mgr = EncryptionManager()

        self.speed_multiplier = 0.25  # Start slower
        self.score = 0
        self.high_score = self.load_high_score()

        self.listener = NetworkListener("127.0.0.1", 5000, self.handle_event)
        self.listener.start()

        self.root.bind("<Up>", lambda e: self.snake.set_direction("UP"))
        self.root.bind("<Down>", lambda e: self.snake.set_direction("DOWN"))
        self.root.bind("<Left>", lambda e: self.snake.set_direction("LEFT"))
        self.root.bind("<Right>", lambda e: self.snake.set_direction("RIGHT"))

        self.update()

        self.root.mainloop()

    def load_high_score(self):
        try:
            with open("high_score.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 0

    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open("high_score.txt", "w") as f:
                f.write(str(self.high_score))

    def handle_event(self, event):
        print("EVENT RECEIVED:", event)

        # Security: Validate event to prevent injection
        valid_events = ["SPEED+", "SPEED-", "FOOD+", "ENCRYPT|"]
        if not any(event.startswith(ve) for ve in valid_events):
            print("Invalid event received, ignoring.")
            return

        if event.startswith("ENCRYPT|"):
            parts = event.split("|")
            if len(parts) != 2:
                return
            hex_data = parts[1].split(" ")[0]
            try:
                bonus = self.enc_mgr.decrypt_text(hex_data)
                self.apply_bonus(bonus)
            except:
                print("Decryption failed, ignoring.")
            return

        if event == "SPEED+":
            self.snake.speed += 1
        elif event == "SPEED-":
            self.snake.speed = max(1, self.snake.speed - 1)
        elif event == "FOOD+":
            self.food.respawn()

    def apply_bonus(self, bonus):
        if bonus == "BONUS_SPEED":
            self.snake.speed += 2
        elif bonus == "BONUS_FOOD":
            self.snake.grow()
        elif bonus == "BONUS_INVINCIBLE":
            self.speed_multiplier = 0.5

    def update(self):
        self.snake.move()
        if self.check_collisions():
            self.game_over()
            return
        self.check_food_collision()
        self.draw()
        delay = int(30 / self.speed_multiplier)
        self.root.after(delay, self.update)

    def check_collisions(self):
        # Wall collision
        x, y = self.snake.body[0]
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            return True
        # Self collision
        head_pos = (x, y)
        for segment in self.snake.body[1:]:
            if head_pos == segment:
                return True
        return False

    def game_over(self):
        self.save_high_score()
        self.canvas.create_text(WIDTH//2, HEIGHT//2, text=f"Game Over\nScore: {self.score}\nHigh Score: {self.high_score}", fill="white", font=("Arial", 20))
        self.root.after(2000, self.root.quit)

    def check_food_collision(self):
        sx, sy = self.snake.body[0]
        if abs(sx - self.food.x) < 20 and abs(sy - self.food.y) < 20:
            self.snake.grow()
            self.food.respawn()
            self.score += 1
            self.speed_multiplier += 0.1  # Speed up on scoring

    def draw(self):
        self.canvas.delete("all")

        # draw snake
        for x, y in self.snake.body:
            self.canvas.create_rectangle(x, y, x+20, y+20, fill="lime")

        # draw food
        self.canvas.create_oval(
            self.food.x, self.food.y,
            self.food.x+20, self.food.y+20,
            fill="red"
        )

        # draw score
        self.canvas.create_text(50, 20, text=f"Score: {self.score}", fill="white", font=("Arial", 12))
        self.canvas.create_text(50, 40, text=f"High Score: {self.high_score}", fill="white", font=("Arial", 12))

if __name__ == "__main__":
    Game()