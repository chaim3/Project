# client/game.py

import tkinter as tk  # GUI toolkit
import argparse  # parse CLI arguments
from snake import Snake  # snake game logic
from food import Food  # food position logic
from network_listener import NetworkListener  # network event receiver
from encryption_manager import (
    ENCRYPT_PREFIX,
    EncryptionManager,
    decode_encrypted_event,
)
import os  # environment variable access

WIDTH = 600  # game area width
HEIGHT = 400  # game area height


def parse_client_args():
    parser = argparse.ArgumentParser(description="Cyber Snake client")  # build CLI parser
    parser.add_argument(
        "--server-host",
        default=os.getenv("SNAKE_SERVER_HOST", "127.0.0.1"),
        help="Server host or IP address",
    )  # server host option
    parser.add_argument(
        "--server-port",
        type=int,
        default=int(os.getenv("SNAKE_SERVER_PORT", "5000")),
        help="Server TCP port",
    )  # server port option
    return parser.parse_args()  # return parsed args


class Game:
    def __init__(self, server_host="127.0.0.1", server_port=5000):
        self.running = True  # game loop flag
        self.root = tk.Tk()  # main GUI window
        self.root.title(f"Cyber Snake - {server_host}:{server_port}")  # window title
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # handle window close

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="black")  # drawing surface
        self.canvas.pack()  # show canvas

        self.snake = Snake(100, 100)  # initial snake
        self.food = Food(WIDTH, HEIGHT)  # initial food
        self.enc_mgr = EncryptionManager()  # local decryption helper

        self.speed_multiplier = 0.25  # starting speed factor
        self.score = 0  # current score
        self.high_score = self.load_high_score()  # load saved high score
        self.rx_count = 0  # received event count
        self.event_handlers = {
            "SPEED+": self._on_speed_up,
            "SPEED-": self._on_speed_down,
            "FOOD+": self._on_food_plus,
            "BONUS_SPEED": self._on_bonus_speed,
            "BONUS_FOOD": self._on_bonus_food,
            "BONUS_INVINCIBLE": self._on_bonus_invincible,
        }  # map decoded events to actions

        self.listener = NetworkListener(server_host, server_port, self.handle_event)  # network listener
        self.listener.start()  # start network thread

        self.root.bind("<Up>", lambda e: self.snake.set_direction("UP"))  # up key
        self.root.bind("<Down>", lambda e: self.snake.set_direction("DOWN"))  # down key
        self.root.bind("<Left>", lambda e: self.snake.set_direction("LEFT"))  # left key
        self.root.bind("<Right>", lambda e: self.snake.set_direction("RIGHT"))  # right key

        self.update()  # start game loop

        self.root.mainloop()  # run Tk event loop

    def on_close(self):
        self.running = False  # stop update loop
        self.listener.stop()  # stop network listener
        self.root.destroy()  # close window

    def load_high_score(self):
        try:
            with open("high_score.txt", "r") as f:
                return int(f.read().strip())  # parse saved score
        except (OSError, ValueError):
            return 0  # fallback if no valid file

    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score  # update high score
            with open("high_score.txt", "w") as f:
                f.write(str(self.high_score))  # save to file

    def handle_event(self, event):
        self.rx_count += 1  # count received events

        if not event.startswith(ENCRYPT_PREFIX):
            self.log_event(event)
            print("Invalid transport event, ignoring.")
            return

        try:
            decoded = decode_encrypted_event(event, self.enc_mgr)  # decrypt payload
        except ValueError:
            self.log_event(event)
            print("Decryption failed, ignoring.")
            return

        self.log_event(event, decoded)  # log raw + decoded
        self.apply_event(decoded)  # apply decoded action

    def log_event(self, raw_event, decoded_event=None):
        if decoded_event is None:
            print("EVENT RECEIVED:", raw_event)
            return
        print(f"EVENT RECEIVED: {raw_event} ({decoded_event})")

    def apply_event(self, event):
        handler = self.event_handlers.get(event)  # lookup event handler
        if handler is None:
            print("Unknown decoded event, ignoring:", event)
            return
        handler()  # execute handler

    def _on_speed_up(self):
        self.snake.speed += 1  # increase snake speed

    def _on_speed_down(self):
        self.snake.speed = max(1, self.snake.speed - 1)  # decrease speed but not below 1

    def _on_food_plus(self):
        self.food.respawn()  # move food to new location

    def _on_bonus_speed(self):
        self.snake.speed += 2  # boost snake speed

    def _on_bonus_food(self):
        self.snake.grow()  # grow snake by one segment

    def _on_bonus_invincible(self):
        self.speed_multiplier = 0.5  # slow base update to simulate invincibility

    def update(self):
        if not self.running:
            return  # stop if game closed
        self.snake.move()  # move snake each tick
        if self.check_collisions():
            self.game_over()
            return
        self.check_food_collision()  # detect food pickup
        self.draw()  # render current scene
        delay = int(30 / self.speed_multiplier)  # calculate tick delay
        self.root.after(delay, self.update)  # schedule next frame

    def check_collisions(self):
        x, y = self.snake.body[0]  # head coordinates
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            return True  # wall collision
        head_pos = (x, y)
        for segment in self.snake.body[1:]:
            if head_pos == segment:
                return True  # collided with body
        return False

    def game_over(self):
        self.save_high_score()  # persist score
        self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2,
            text=f"Game Over\nScore: {self.score}\nHigh Score: {self.high_score}",
            fill="white",
            font=("Arial", 20),
        )  # show game over text
        self.root.after(2000, self.root.quit)  # quit after delay

    def check_food_collision(self):
        sx, sy = self.snake.body[0]  # head position
        if abs(sx - self.food.x) < 20 and abs(sy - self.food.y) < 20:
            self.snake.grow()  # eat food
            self.food.respawn()  # spawn new food
            self.score += 1  # increment score
            self.speed_multiplier += 0.1  # increase game speed

    def draw(self):
        self.canvas.delete("all")  # clear previous frame

        for x, y in self.snake.body:
            self.canvas.create_rectangle(x, y, x + 20, y + 20, fill="lime")  # draw snake segment

        self.canvas.create_oval(
            self.food.x,
            self.food.y,
            self.food.x + 20,
            self.food.y + 20,
            fill="red",
        )  # draw food

        self.canvas.create_text(50, 20, text=f"Score: {self.score}", fill="white", font=("Arial", 12))  # score text
        self.canvas.create_text(
            90,
            40,
            text=f"High Score: {self.high_score} | RX: {self.rx_count}",
            fill="white",
            font=("Arial", 12),
        )  # status text


if __name__ == "__main__":
    args = parse_client_args()  # parse CLI args
    Game(args.server_host, args.server_port)  # start game
