import socket
import threading
import cv2
import numpy as np
import pyautogui
import pickle
import struct
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("192.168.129.148", 9999))
server.listen(1)
print("[+] Waiting for client...")
conn, addr = server.accept()
print(f"[+] Connected to {addr}")
running = True
def handle_commands():
global running
buffer = ""
while running:
try:
data = conn.recv(1024).decode()
if not data:
continue
buffer += data
while '\n' in buffer:
command, buffer = buffer.split('\n', 1)
command = command.strip()
if not command:
continue
print(f"[Command received]: {command}")
if command.startswith("TYPE "):
text = command[5:]
print(f"[Typing]: {text}")
pyautogui.write(text)
elif command.startswith("CLICK"):
parts = command.split()
if len(parts) == 3:
_, x, y = parts
pyautogui.click(int(x), int(y))
print(f"[Click]: at ({x},{y})")
else:
print("[!] Invalid CLICK command")
elif command.startswith("MOVE"):
parts = command.split()
if len(parts) == 3:
_, x, y = parts
x, y = int(x), int(y)
if x == 0 and y == 0:
continue
pyautogui.moveTo(x, y)
print(f"[Mouse moved to]: {x}, {y}")
elif command == "q":
print("[!] Client requested quit.")
running = False
break
else:
print("[!] Unknown command:", command)
except Exception as e:
print(f"[!] Command error: {e}")
break
threading.Thread(target=handle_commands, daemon=True).start()
while running:
try:
img = pyautogui.screenshot()
frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
data = cv2.imencode('.jpg', frame)[1].tobytes()
size = str(len(data)).ljust(16).encode()
conn.sendall(size + data)
except Exception as e:
print(f"[!] Screen send error: {e}")
break
conn.close()
server.close()
print("[+] Server shut down.")
