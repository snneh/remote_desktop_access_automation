import socket
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key

HOST = input("Enter server IP: ")
PORT = 42069

mouse = MouseController()
keyboard = KeyboardController()


def setup_connection():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        print("Connected to server")
        return client
    except Exception as e:
        print(f"Connection Failed: {e}")
        return None


def handle_event(data):
    try:
        # Try to parse as mouse event first (format: action,x,y)
        parts = data.strip().split(",")
        if len(parts) == 3:
            action, x, y = parts[0].lower(), int(parts[1]), int(parts[2])
            mouse.position = (x, y)
            if action == "click":
                mouse.click(Button.left, 1)
                print(f"left clicked at ({x}, {y})")
            elif action == "rightclick":
                mouse.click(Button.right, 1)
                print(f"right clicked at ({x}, {y})")
            elif action == "move":
                print(f"Moved to ({x}, {y})")
            else:
                print(f"Unknown mouse action: {action}")
        else:
            # Otherwise, treat as keyboard event
            action = data.strip()
            # Handle special keys if needed
            if action.startswith("Key."):
                key_name = action.replace("Key.", "")
                key_obj = getattr(Key, key_name, None)
                if key_obj:
                    keyboard.press(key_obj)
                    keyboard.release(key_obj)
                    print(f"Pressed special key: {action}")
                else:
                    print(f"Unknown special key: {action}")
            else:
                keyboard.press(action)
                keyboard.release(action)
                print(f"Pressed key: {action}")
    except Exception as e:
        print(f"Error processing data: {data} - {str(e)}")


def main():
    client = setup_connection()
    if not client:
        return

    try:
        while True:
            data = client.recv(1024)
            if not data:
                print("Server disconnected.")
                break
            handle_event(data.decode())
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
