# server/server.py

import socket
import time
import random
import argparse
from encryption_manager import EncryptionManager, encode_encrypted_event


def parse_server_args():
    parser = argparse.ArgumentParser(description="Cyber Snake event server")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Bind host/IP (use 0.0.0.0 to accept remote clients)",
    )
    parser.add_argument("--port", type=int, default=5000, help="Bind TCP port")
    return parser.parse_args()

class SnakeServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.running = True
        self.enc_mgr = EncryptionManager()
        self.events = ["SPEED+", "SPEED-", "FOOD+", "BONUS_SPEED", "BONUS_FOOD", "BONUS_INVINCIBLE"]

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(1)
        print(f"Server listening on {self.host}:{self.port}")
        while self.running:
            client_socket, addr = server_socket.accept()
            print(f"Client connected: {addr}")
            self.serve_client(client_socket)

    def serve_client(self, client_socket):
        try:
            while self.running:
                time.sleep(random.randint(5, 15))  # Random event every 5-15 seconds
                event = encode_encrypted_event(random.choice(self.events), self.enc_mgr)
                client_socket.sendall(f"EVENT:{event}\n".encode("utf-8"))
        except OSError:
            print("Client disconnected")
        finally:
            try:
                client_socket.close()
            except OSError:
                pass

if __name__ == "__main__":
    args = parse_server_args()
    server = SnakeServer(args.host, args.port)
    server.start()