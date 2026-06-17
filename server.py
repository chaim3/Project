# server/server.py

import socket
import threading
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
        self.clients = []
        self.running = True
        self.enc_mgr = EncryptionManager()

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        threading.Thread(target=self.broadcast_events, daemon=True).start()

        while self.running:
            client_socket, addr = server_socket.accept()
            print(f"Client connected: {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

    def handle_client(self, client_socket):
        self.clients.append(client_socket)
        try:
            while self.running:
                data = client_socket.recv(1)
                if not data:
                    break
        except OSError:
            pass
        finally:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()

    def broadcast_events(self):
        events = ["SPEED+", "SPEED-", "FOOD+", "BONUS_SPEED", "BONUS_FOOD", "BONUS_INVINCIBLE"]
        while self.running:
            time.sleep(random.randint(5, 15))  # Random event every 5-15 seconds
            event = encode_encrypted_event(random.choice(events), self.enc_mgr)
            self.send_to_all(f"EVENT:{event}")

    def send_to_all(self, message):
        for client in self.clients[:]:  # Copy list to avoid modification during iteration
            try:
                client.send(message.encode("utf-8"))
            except:
                self.clients.remove(client)

if __name__ == "__main__":
    args = parse_server_args()
    server = SnakeServer(args.host, args.port)
    server.start()