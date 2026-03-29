import time
import threading
from pythonping import ping
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

# Settings
CHECK_HOST = "8.8.8.8"
INTERVAL = 1
TIMEOUT = 2

running = True


def get_network_status():
    """Zwraca kolor statusu oraz latencję przy użyciu pythonping."""
    try:
        response = ping(CHECK_HOST, count=1, timeout=TIMEOUT)

        if not response.success():
            return 'red', None

        latency = response.rtt_avg_ms

        match latency:
            case l if l < 100:
                return 'green', round(l, 1)
            case l if l < 300:
                return 'yellow', round(l, 1)
            case l:
                return 'red', round(l, 1)

    except Exception:
        return 'red', None


def create_circle_image(color):
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((4, 4, 60, 60), fill=color, outline="white", width=4)
    return image


def update_loop(icon):
    global running

    status_map = {
        "green": "Połączenie prawidłowe",
        "yellow": "Problemy z internetem",
        "red": "Brak połączenia / Wysoki ping"
    }

    while running:
        new_color, latency = get_network_status()

        icon.icon = create_circle_image(new_color)

        base_text = status_map.get(new_color, "Status")
        if latency is not None:
            icon.title = f"{base_text} [{latency}ms]"
        else:
            icon.title = base_text

        for _ in range(int(INTERVAL * 10)):
            if not running:
                break
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
