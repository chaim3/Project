# server/server.py

import socket  # networking primitives for TCP sockets
import time  # timing helpers like sleep
import random  # random choices and intervals
import argparse  # command-line argument parsing
from encryption_manager import EncryptionManager, encode_encrypted_event  # local encryption utilities


def parse_server_args():
    parser = argparse.ArgumentParser(description="Cyber Snake event server")  # create CLI parser
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Bind host/IP (use 0.0.0.0 to accept remote clients)",
    )  # host option with default
    parser.add_argument("--port", type=int, default=5000, help="Bind TCP port")  # port option with default
    return parser.parse_args()  # parse and return args


class SnakeServer:
    def __init__(self, host, port):
        self.host = host  # address to bind to
        self.port = port  # TCP port to listen on
        self.running = True  # control flag for main loops
        self.enc_mgr = EncryptionManager()  # instance for encrypting events
        self.events = ["SPEED+", "SPEED-", "FOOD+", "BONUS_SPEED", "BONUS_FOOD", "BONUS_INVINCIBLE"]  # available events

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create IPv4 TCP socket
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # allow quick reuse of address
        server_socket.bind((self.host, self.port))  # bind to configured host/port
        server_socket.listen(1)  # start listening (backlog=1)
        print(f"Server listening on {self.host}:{self.port}")  # log bound address
        while self.running:  # accept loop
            client_socket, addr = server_socket.accept()  # block until a client connects
            print(f"Client connected: {addr}")  # log client address
            self.serve_client(client_socket)  # handle the connected client

    def serve_client(self, client_socket):
        try:
            while self.running:  # send events while server is running
                time.sleep(random.randint(5, 15))  # wait 5-15s between events
                event = encode_encrypted_event(random.choice(self.events), self.enc_mgr)  # pick & encode an event
                client_socket.sendall(f"EVENT:{event}\n".encode("utf-8"))  # send event line to client
        except OSError:
            print("Client disconnected")  # handle socket errors (client closed)
        finally:
            try:
                client_socket.close()  # ensure socket is closed
            except OSError:
                pass  # ignore errors during close


if __name__ == "__main__":
    args = parse_server_args()  # get CLI args
    server = SnakeServer(args.host, args.port)  # create server instance
    server.start()  # start serving