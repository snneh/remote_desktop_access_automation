import socket
import threading
from pynput import mouse, keyboard
import time
import json


# Helper function to send data over a socket
def send_data(sock, data):
    try:
        message = json.dumps(data) + "\n"
        sock.sendall(message.encode())
    except Exception as e:
        print(f"Error sending data: {e}")


def mouse_tracker(mouse_socket):
    def on_move(x, y):
        data = {"type": "move", "x": x, "y": y}
        send_data(mouse_socket, data)

    def on_click(x, y, button, pressed):
        if pressed:
            action = "click" if button == mouse.Button.left else "rightclick"
            data = {"type": action, "x": x, "y": y}
            send_data(mouse_socket, data)

    # Start mouse listener
    with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
        listener.join()


# Set of currently pressed keys
pressed_keys = set()


# Mapping for special keys
def format_key(key):
    if isinstance(key, keyboard.KeyCode) and key.char:
        return key.char
    elif isinstance(key, keyboard.Key):
        return key.name  # Returns "enter", "ctrl", etc.
    else:
        return str(key)


def keyboard_tracker(keyboard_socket):
    def on_press(key):
        try:
            k = format_key(key)
            if k not in pressed_keys:
                pressed_keys.add(k)

                # Send combination if multiple are held (e.g., ctrl + c)
                if len(pressed_keys) > 1:
                    send_data(keyboard_socket, {"key": list(pressed_keys)})
                else:
                    send_data(keyboard_socket, {"key": k})
        except Exception as e:
            print(f"Keyboard error on press: {e}")

    def on_release(key):
        try:
            k = format_key(key)
            pressed_keys.discard(k)
        except Exception as e:
            print(f"Keyboard error on release: {e}")

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


# def keyboard_tracker(keyboard_socket):
#     def on_press(key):
#         try:
#             if hasattr(key, "char"):
#                 data = {"type": "keypress", "key": key.char}
#             else:
#                 data = {"type": "keypress", "key": str(key)}
#             send_data(keyboard_socket, data)
#         except Exception as e:
#             print(f"Keyboard error: {e}")

#     with keyboard.Listener(on_press=on_press) as listener:
#         listener.join()


def screenshare_tracker(screenshare_socket):
    while True:
        # Simulate sending screen data (e.g., as a placeholder)
        try:
            data = {"type": "screenshare", "frame": "dummy_frame_data"}
            send_data(screenshare_socket, data)
            time.sleep(1)  # Simulate frame rate
        except Exception as e:
            print(f"Screenshare error: {e}")
            break


def main():
    # Connect to the main server
    HOST = input()
    main_port = 42069

    try:
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        main_socket.connect((HOST, main_port))
        print(f"Connected to main server at {HOST}:{main_port}")
    except Exception as e:
        print(f"Could not connect to main server: {e}")
        return

    # Set up additional sockets for mouse, keyboard, and screenshare
    try:
        mouse_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        keyboard_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # screenshare_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        mouse_socket.connect((HOST, 5001))
        keyboard_socket.connect((HOST, 5002))
        # screenshare_socket.connect((HOST, 5003))

        print("All auxiliary sockets connected!")
    except Exception as e:
        print(f"Failed to connect auxiliary sockets: {e}")
        return

    # Start threads for mouse, keyboard, and screenshare tracking
    mouse_thread = threading.Thread(
        target=mouse_tracker, args=(mouse_socket,), daemon=True
    )
    keyboard_thread = threading.Thread(
        target=keyboard_tracker, args=(keyboard_socket,), daemon=True
    )
    # screenshare_thread = threading.Thread(
    #     target=screenshare_tracker, args=(screenshare_socket,), daemon=True
    # )

    mouse_thread.start()
    keyboard_thread.start()
    # screenshare_thread.start()

    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down client.")
        mouse_socket.close()
        keyboard_socket.close()
        # screenshare_socket.close()
        main_socket.close()


if __name__ == "__main__":
    main()
