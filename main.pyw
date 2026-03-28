import time
import http.client
import threading
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

# Settings
CHECK_HOST = "www.google.com"
INTERVAL = 3
TIMEOUT = 2

running = True

def get_network_status():
    start_time = time.time()
    try:
        conn = http.client.HTTPSConnection(CHECK_HOST, timeout=TIMEOUT)
        conn.request("HEAD", "/")
        response = conn.getresponse()
        latency = int((time.time() - start_time) * 1000)
        conn.close()
        if response.status < 400:
            return ("green" if latency < 300 else "yellow"), latency
        return "yellow", None
    except:
        return "red", None

def create_circle_image(color):
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((4, 4, 60, 60), fill=color, outline="white", width=4)
    return image

def update_loop(icon):
    global running
    while running:
        new_color, latency = get_network_status()
        icon.icon = create_circle_image(new_color)
        
        status_map = {
            "green": "Połączenie prawidłowe", 
            "yellow": "Problemy z internetem", 
            "red": "Brak połączenia z internetem"
        }
        base_text = status_map.get(new_color, "Status")
        
        if latency:
            icon.title = f"{base_text} [{latency}ms]"
        else:
            icon.title = f"{base_text}"

        for _ in range(INTERVAL * 10):
            if not running: break
            time.sleep(0.1)

def on_quit(icon):
    global running
    running = False
    icon.stop()

def main():
    icon = Icon("NetStatus", create_circle_image("gray"), "Inicjalizacja...")
    icon.menu = Menu(MenuItem('Zakończ program', on_quit))
    
    thread = threading.Thread(target=update_loop, args=(icon,), daemon=True)
    thread.start()
    
    icon.run()

if __name__ == "__main__":
    main()