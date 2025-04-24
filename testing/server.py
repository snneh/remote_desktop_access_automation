import socket
import threading
from pynput import mouse

# Global variables
clients = []
client_lock = threading.Lock()


def connection_handler():
    # Set up server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 42069))
    server.listen(5)
    print(f"Server listening on {socket.gethostbyname(socket.gethostname())}:42069")

    # Accept clients indefinitely
    while True:
        conn, addr = server.accept()
        print(f"New client connected: {addr}")

        # Add client to the global list
        with client_lock:
            clients.append(conn)


def mouse_tracker():
    # Mouse event callbacks
    def on_move(x, y):
        data = f"move,{x},{y}".encode()
        broadcast_to_clients(data)

    def on_click(x, y, button, pressed):
        if pressed:  # Only send on press, not release
            action = "click" if button == mouse.Button.left else "rightclick"
            data = f"{action},{x},{y}".encode()
            broadcast_to_clients(data)

    # Start mouse listener (runs in its own thread internally)
    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
    mouse_listener.start()
    mouse_listener.join()  # This will keep the thread alive indefinitely


def broadcast_to_clients(data):
    disconnected = []

    with client_lock:
        for client in clients:
            try:
                client.sendall(data)
            except Exception as e:
                disconnected.append(client)
                print(f"Client disconnected: {e}")

        # Remove disconnected clients
        for client in disconnected:
            if client in clients:
                clients.remove(client)


if __name__ == "__main__":
    # Create and start connection thread
    conn_thread = threading.Thread(target=mouse_tracker, daemon=True)
    conn_thread.start()
    # Start mouse tracking in the main thread
    connection_handler()
