# Cyber Snake

A simple Tkinter Snake game with a TCP event server (single client).

The server sends encrypted events, and the client decrypts and applies them in real time.

## Files

- `game.py` - Tkinter client game
- `server.py` - TCP event server
- `network_listener.py` - client socket listener
- `encryption_manager.py` - XOR hex encryption/decryption
- `snake.py`, `food.py` - game objects
- `high_score.txt` - saved high score

## Requirements

- Python 3.8+
- Tkinter (usually included with Python)

## Run Locally (Same Machine)

1. Start the server:

```bash
python3 server.py --host 127.0.0.1 --port 5000
```

2. Start the game client in another terminal:

```bash
python3 game.py --server-host 127.0.0.1 --server-port 5000
```

## Run Across Different Machines

1. On the server machine, listen on all interfaces:

```bash
python3 server.py --host 0.0.0.0 --port 5000
```

2. Find the server machine IP (example: `192.168.1.42`).

3. On one client machine, connect to that IP:

```bash
python3 game.py --server-host 192.168.1.42 --server-port 5000
```

4. Ensure firewall/network rules allow inbound TCP `5000` on the server machine.

## Environment Variable Options (Client)

Instead of flags, you can set:

```bash
export SNAKE_SERVER_HOST=192.168.1.42
export SNAKE_SERVER_PORT=5000
python3 game.py
```

## Event Protocol

Server sends messages as:

- `EVENT:ENCRYPT|<HEX_PAYLOAD>\n`

Notes:

- Each TCP message ends with a newline so clients can safely split the stream into complete events.
- Client accepts encrypted transport events only.

Client logs encrypted event plus decrypted value, for example:

- `EVENT RECEIVED: ENCRYPT|7D70716A6C606C6F7A7A7B (BONUS_SPEED)`

## Notes

- Encryption is XOR-based and intended for demonstration, not strong security.
- Transport flow is now one-path for simplicity: server encrypts every event, client decrypts every event.
