# client/game.py

import tkinter as tk
import argparse
from snake import Snake
from food import Food
from network_listener import NetworkListener
from encryption_manager import EncryptionManager
import os

WIDTH = 600
HEIGHT = 400


def parse_client_args():
    parser = argparse.ArgumentParser(description="Cyber Snake client")
    parser.add_argument(
        "--server-host",
        default=os.getenv("SNAKE_SERVER_HOST", "127.0.0.1"),
        help="Server host or IP address",
    )
    parser.add_argument(
        "--server-port",
        type=int,
        default=int(os.getenv("SNAKE_SERVER_PORT", "5000")),
        help="Server TCP port",
    )
    return parser.parse_args()

class Game:
    def __init__(self, server_host="127.0.0.1", server_port=5000):
        self.running = True
        self.root = tk.Tk()
        self.root.title(f"Cyber Snake - {server_host}:{server_port}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()

        self.snake = Snake(100, 100)
        self.food = Food(WIDTH, HEIGHT)
        self.enc_mgr = EncryptionManager()

        self.speed_multiplier = 0.25  # Start slower
        self.score = 0
        self.high_score = self.load_high_score()
        self.rx_count = 0
        self.event_handlers = {
            "SPEED+": self._on_speed_up,
            "SPEED-": self._on_speed_down,
            "FOOD+": self._on_food_plus,
            "BONUS_SPEED": self._on_bonus_speed,
            "BONUS_FOOD": self._on_bonus_food,
            "BONUS_INVINCIBLE": self._on_bonus_invincible,
        }

        self.listener = NetworkListener(server_host, server_port, self.handle_event)
        self.listener.start()

        self.root.bind("<Up>", lambda e: self.snake.set_direction("UP"))
        self.root.bind("<Down>", lambda e: self.snake.set_direction("DOWN"))
        self.root.bind("<Left>", lambda e: self.snake.set_direction("LEFT"))
        self.root.bind("<Right>", lambda e: self.snake.set_direction("RIGHT"))

        self.update()

        self.root.mainloop()

    def on_close(self):
        self.running = False
        self.listener.stop()
        self.root.destroy()

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
        self.rx_count += 1

        if not is_valid_transport_event(event):
            self.log_event(event)
            print("Invalid event received, ignoring.")
            return

        if event.startswith(ENCRYPT_PREFIX):
            try:
                decoded = decode_encrypted_event(event, self.enc_mgr)
                self.log_event(event, decoded)
                self.apply_event(decoded)
            except Exception:
                self.log_event(event)
                print("Decryption failed, ignoring.")
            return

        self.log_event(event)
        self.apply_event(event)

    def log_event(self, raw_event, decoded_event=None):
        if decoded_event is None:
            print("EVENT RECEIVED:", raw_event)
            return
        print(f"EVENT RECEIVED: {raw_event} ({decoded_event})")

    def apply_event(self, event):
        handler = self.event_handlers.get(event)
        if handler is None:
            print("Unknown decoded event, ignoring:", event)
            return
        handler()

    def _on_speed_up(self):
        self.snake.speed += 1

    def _on_speed_down(self):
        self.snake.speed = max(1, self.snake.speed - 1)

    def _on_food_plus(self):
        self.food.respawn()

    def _on_bonus_speed(self):
        self.snake.speed += 2

    def _on_bonus_food(self):
        self.snake.grow()

    def _on_bonus_invincible(self):
        self.speed_multiplier = 0.5

    def update(self):
        if not self.running:
            return
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
        self.canvas.create_text(
            90,
            40,
            text=f"High Score: {self.high_score} | RX: {self.rx_count}",
            fill="white",
            font=("Arial", 12),
        )

if __name__ == "__main__":
    args = parse_client_args()
    Game(args.server_host, args.server_port)