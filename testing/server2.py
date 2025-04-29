import socket
import threading
from pynput import mouse, keyboard

clients = []
client_lock = threading.Lock()
server_running = True


def connection_handler():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 42069))
    server.listen(5)
    print(f"Server listening on {socket.gethostbyname(socket.gethostname())}:42069")

    while server_running:
        try:
            server.settimeout(1.0)
            conn, addr = server.accept()
            print(f"New client connected: {addr}")
            with client_lock:
                clients.append(conn)
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Server error: {e}")
            break

    server.close()
    print("Server socket closed.")


def mouse_tracker():
    def on_move(x, y):
        data = f"move,{x},{y}".encode()
        broadcast_to_clients(data)

    def on_click(x, y, button, pressed):
        if pressed:
            action = "click" if button == mouse.Button.left else "rightclick"
            data = f"{action},{x},{y}".encode()
            broadcast_to_clients(data)

    with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
        listener.join()


def keyboard_tracker():
    def on_press(key):
        try:
            if hasattr(key, "char") and key.char is not None:
                data = key.char.encode()
            else:
                data = str(key).encode()
            broadcast_to_clients(data)
        except Exception as e:
            print(f"Keyboard event error: {e}")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def broadcast_to_clients(data):
    disconnected = []
    with client_lock:
        for client in clients:
            try:
                client.sendall(data)
            except Exception as e:
                disconnected.append(client)
                print(f"Client disconnected: {e}")
        for client in disconnected:
            if client in clients:
                clients.remove(client)


def main():
    con_thread = threading.Thread(target=connection_handler, daemon=True)
    mouse_thread = threading.Thread(target=mouse_tracker, daemon=True)
    keyboard_thread = threading.Thread(target=keyboard_tracker, daemon=True)

    con_thread.start()
    mouse_thread.start()
    keyboard_thread.start()

    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("Shutting down server.")


if __name__ == "__main__":
    main()
