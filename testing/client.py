import socket
from pynput.mouse import Button, Controller

HOST = input("Enter server IP: ")
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("Connected to server")

mouse = Controller()

while True:
    data = client.recv(1024).decode()

    try:
        # Split data into x, y coordinates and action
        parts = data.strip().split(",")

        action, x, y = parts[0].lower(), int(parts[1]), int(parts[2])

        # Move mouse to specified coordinates
        mouse.position = (x, y)

        # Perform specified action
        if action == "click":
            mouse.click(Button.left, 1)
            print(f"left clicked at ({x}, {y})")
        elif action == "rightclick":
            mouse.click(Button.right, 1)
            print(f"right clicked at ({x}, {y})")
        elif action == "move":
            print(f"Moved to ({x}, {y})")
        else:
            print(f"Unknown action: {action}")

    except Exception as e:
        print(f"Error processing data: {data} - {str(e)}")
