import re
import subprocess
import platform
import time
import threading
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

# Settings
CHECK_HOST = "8.8.8.8"
INTERVAL = 1
TIMEOUT = 2

running = True
current_status = "Inicjalizacja..."


def ping_host(host, timeout=2):
    """Pings host and extracts the exact round-trip time from ping output."""
    is_mac = platform.system().lower() == "darwin"
    is_win = platform.system().lower() == "windows"

    param = "-n" if is_win else "-c"
    timeout_param = "-w" if is_win else "-W"
    timeout_val = str(timeout * 1000) if is_mac else str(timeout)

    command = ["ping", param, "1", timeout_param, timeout_val, host]

    try:
        output = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if output.returncode == 0:
            match = re.search(r"time[=<]([\d\.]+)\s*ms", output.stdout, re.IGNORECASE)
            if match:
                return float(match.group(1))
            return 10.0
        return None
    except Exception:
        return None


def get_network_status():
    """Returns status color and latency."""
    latency = ping_host(CHECK_HOST, timeout=TIMEOUT)

    if latency is None:
        return 'red', None

    if latency < 100:
        return 'green', round(latency, 1)
    elif latency < 300:
        return 'yellow', round(latency, 1)
    else:
        return 'red', round(latency, 1)


def create_circle_image(color):
    """Generates a status icon."""
    image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((12, 12, 52, 52), fill=color, outline="white", width=4)
    return image


def update_loop(icon):
    global running, current_status

    status_map = {
        "green": "Połączenie OK",
        "yellow": "Wysoki ping",
        "red": "Brak połączenia"
    }

    time.sleep(0.5)

    while running:
        new_color, latency = get_network_status()

        base_text = status_map.get(new_color, "Status")
        if latency is not None:
            current_status = f"{base_text} [{latency}ms]"
        else:
            current_status = base_text

        try:
            # 1. Update visual dot icon
            icon.icon = create_circle_image(new_color)
            # 2. Tell pystray to rebuild/update the menu text
            icon.update_menu()
        except Exception:
            break

        time.sleep(INTERVAL)


def on_quit(icon):
    global running
    running = False
    icon.stop()


# Generator function that yields menu items dynamically
def make_menu():
    yield MenuItem(current_status, action=None, enabled=False)
    yield Menu.SEPARATOR
    yield MenuItem('Zakończ program', on_quit)


def main():
    icon = Icon(
        "NetStatus",
        create_circle_image("gray"),
        menu=Menu(make_menu)  # Pass the callable generator
    )

    def setup(icon):
        icon.visible = True
        thread = threading.Thread(target=update_loop, args=(icon,), daemon=True)
        thread.start()

    icon.run(setup)


if __name__ == "__main__":
    main()
