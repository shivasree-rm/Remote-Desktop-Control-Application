import socket
import cv2
import numpy as np
import threading
import time
from pynput import mouse, keyboard
import pyautogui
# Set server IP and port
SERVER_IP = "192.168.129.148"
PORT = 9999
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))
print("[+] Connected to server.")
running = True
# Real-time mouse movement tracking using pyautogui
def send_mouse_position():
last_pos = (-1, -1)
while running:
x, y = pyautogui.position()
if (x, y) != last_pos:
try:
client.sendall(f"MOVE {x} {y}\n".encode())
last_pos = (x, y)
except:
break
time.sleep(0.3) # Fast polling for smooth movement
# Real-time mouse click tracking
def on_click(x, y, button, pressed):
if pressed:
try:
client.sendall(f"CLICK {x} {y}\n".encode())
except:
pass
# Real-time keyboard control
def on_press(key):
try:
if hasattr(key, 'char') and key.char:
client.sendall(f"TYPE {key.char}\n".encode())
elif key == keyboard.Key.enter:
client.sendall(f"TYPE \n".encode())
elif key == keyboard.Key.space:
client.sendall(f"TYPE \n".encode())
elif key == keyboard.Key.backspace:
client.sendall(f"TYPE {chr(8)}\n".encode())
except:
pass
# Start mouse and keyboard listeners
def start_input_listeners():
mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press)
mouse_listener.start()
keyboard_listener.start()
# Start mouse position sender thread
threading.Thread(target=send_mouse_position, daemon=True).start()
# Start input listeners
start_input_listeners()
# Show the server screen
try:
while running:
# Receive image size
size_data = b""
while len(size_data) < 16:
packet = client.recv(16 - len(size_data))
if not packet:
raise ConnectionError("Disconnected.")
size_data += packet
size = int(size_data.decode().strip())
# Receive frame
data = b""
while len(data) < size:
packet = client.recv(size - len(data))
if not packet:
raise ConnectionError("Disconnected.")
data += packet
# Decode and show frame
frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
cv2.imshow("Remote Desktop", frame)
if cv2.waitKey(1) == ord('q'):
running = False
break
except Exception as e:
print(f"[!] Error: {e}")
finally:
client.close()
cv2.destroyAllWindows()
print("[+] Client closed.")
