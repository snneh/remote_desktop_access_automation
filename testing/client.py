import socket
import threading
import json
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key


def handle_mouse(client_socket):
    mouse = MouseController()
    buffer = ""

    while True:
        try:
            buffer += client_socket.recv(1024).decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                data = json.loads(line)
                action, x, y = data["type"], int(data["x"]), int(data["y"])

                if action == "move":
                    mouse.position = (x, y)
                elif action == "click":
                    mouse.position = (x, y)
                    mouse.click(Button.left, 1)
                    print(f"Left clicked at ({x}, {y})")
                elif action == "rightclick":
                    mouse.position = (x, y)
                    mouse.click(Button.right, 1)
                    print(f"Right clicked at ({x}, {y})")
        except Exception as e:
            print(f"Mouse socket error: {e}")
            break


SPECIAL_KEYS = {
    "enter": Key.enter,
    "shift": Key.shift,
    "ctrl": Key.ctrl_l,
    "ctrl": Key.ctrl_r,
    "alt": Key.alt,
    "tab": Key.tab,
    "esc": Key.esc,
    "backspace": Key.backspace,
    "caps_lock": Key.caps_lock,
    "cmd": Key.cmd,
    "delete": Key.delete,
    "space": Key.space,
    "up": Key.up,
    "down": Key.down,
    "left": Key.left,
    "right": Key.right,
}


def handle_keyboard(client_socket):
    keyboard = KeyboardController()
    buffer = ""

    while True:
        try:
            buffer += client_socket.recv(1024).decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    print(f"Invalid JSON: {line}")
                    continue

                # Accept either a string or a list of keys
                keys = data.get("key")
                if not keys:
                    continue

                # Normalize input
                if isinstance(keys, str):
                    keys = [keys]

                key_objects = []
                for k in keys:
                    k = k.lower()
                    key_objects.append(
                        SPECIAL_KEYS.get(k, k)
                    )  # fallback to literal key if not special

                # Press and release keys (for combinations, hold modifiers)
                if len(key_objects) == 1:
                    key = key_objects[0]
                    if isinstance(key, Key):
                        keyboard.press(key)
                        keyboard.release(key)
                    else:
                        keyboard.type(str(key))
                else:
                    try:
                        for key in key_objects:
                            keyboard.press(key)
                        for key in reversed(key_objects):
                            keyboard.release(key)
                    except Exception as e:
                        print(f"Failed to press combo: {keys} -> {e}")

        except Exception as e:
            print(f"Keyboard socket error: {e}")
            break


def handle_screenshare(client_socket, client_addr):
    while True:
        try:
            data, addr = client_socket.recvfrom(1024)
            if data:
                print(f"Screenshare data from {addr}")
        except Exception as e:
            print(f"Screenshare socket error: {e}")
            break


def main():
    # Create TCP socket for main connection
    main_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_server.bind(("0.0.0.0", 42069))
    main_server.listen(5)
    print(f"Server IP: {socket.gethostbyname(socket.gethostname())}")

    mouse_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    keyboard_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    screenshare_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    mouse_socket.bind(("0.0.0.0", 5001))
    keyboard_socket.bind(("0.0.0.0", 5002))
    screenshare_socket.bind(("0.0.0.0", 5003))

    print("Main server listening.")

    mouse_socket.listen()
    keyboard_socket.listen()

    mouse_conn, mouse_addr = mouse_socket.accept()
    keyboard_conn, keyboard_addr = keyboard_socket.accept()
    # screenshare_socket.connect()

    threading.Thread(target=handle_mouse, args=(mouse_conn,), daemon=True).start()
    threading.Thread(target=handle_keyboard, args=(keyboard_conn,), daemon=True).start()

    # threading.Thread(
    #     target=handle_screenshare, args=(screenshare_socket, None), daemon=True
    # ).start()

    # Main loop to accept TCP connections
    while True:
        try:
            conn, addr = main_server.accept()
            print(f"Client connected from {addr}")
            # You can handle the main connection here if needed
        except KeyboardInterrupt as e:
            print(f"Error accepting connection: {e}")
            break
        except KeyboardInterrupt:
            mouse_socket.close()
            keyboard_socket.close()


if __name__ == "__main__":
    main()
