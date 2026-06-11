# server/server.py

import socket
import threading
import time
import random

class SnakeServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.running = True

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                # For simplicity, server doesn't read from clients, just sends events
                time.sleep(1)
        except:
            pass
        finally:
            self.clients.remove(client_socket)
            client_socket.close()

    def broadcast_events(self):
        events = ["SPEED+", "SPEED-", "FOOD+", "ENCRYPT|BONUS_SPEED", "ENCRYPT|BONUS_FOOD", "ENCRYPT|BONUS_INVINCIBLE"]
        while self.running:
            time.sleep(random.randint(5, 15))  # Random event every 5-15 seconds
            event = random.choice(events)
            if event.startswith("ENCRYPT|"):
                # Encrypt the bonus
                from encryption_manager import EncryptionManager
                enc_mgr = EncryptionManager()
                bonus = event.split("|")[1]
                encrypted = enc_mgr.encrypt_text(bonus)
                event = f"ENCRYPT|{encrypted}"
            self.send_to_all(f"EVENT:{event}")

    def send_to_all(self, message):
        for client in self.clients[:]:  # Copy list to avoid modification during iteration
            try:
                client.send(message.encode("utf-8"))
            except:
                self.clients.remove(client)

if __name__ == "__main__":
    server = SnakeServer("127.0.0.1", 5000)
    server.start()