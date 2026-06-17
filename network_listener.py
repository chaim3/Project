# client/network_listener.py

import socket  # socket API for networking
import threading  # thread for background listening

class NetworkListener:
    def __init__(self, host, port, callback):
        self.host = host  # server host to connect
        self.port = port  # server port to connect
        self.callback = callback  # event handler callback
        self.running = True  # loop control flag
        self.sock = None  # socket object placeholder
        self.buffer = ""  # partial incoming text buffer

    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()  # start background listen thread

    def listen(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create TCP socket
            self.sock.connect((self.host, self.port))  # connect to server

            while self.running:
                data = self.sock.recv(1024)  # receive raw bytes
                if not data:
                    break  # stop if connection closed

                self.buffer += data.decode("utf-8", errors="ignore")  # decode bytes to string
                while "\n" in self.buffer:
                    line, self.buffer = self.buffer.split("\n", 1)  # consume one line
                    msg = line.strip()  # strip whitespace
                    if msg.startswith("EVENT:"):
                        self.callback(msg[6:])  # forward event payload

        except Exception as e:
            print("Network error:", e)  # report any socket error
        finally:
            if self.sock is not None:
                try:
                    self.sock.close()  # close socket cleanly
                except Exception:
                    pass
                self.sock = None

    def stop(self):
        self.running = False  # stop listen loop
        if self.sock is not None:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)  # shutdown socket
            except Exception:
                pass