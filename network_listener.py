# client/network_listener.py

import socket
import threading

class NetworkListener:
    def __init__(self, host, port, callback):
        self.host = host
        self.port = port
        self.callback = callback
        self.running = True

    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))

            while self.running:
                data = sock.recv(1024)
                if not data:
                    break

                msg = data.decode("utf-8", errors="ignore").strip()
                if msg.startswith("EVENT:"):
                    event = msg[6:]
                    self.callback(event)

        except Exception as e:
            print("Network error:", e)