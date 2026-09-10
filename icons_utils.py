import os
import tempfile
import time

import glob
import win32com.client
from PIL import Image, ImageDraw, ImageFont


def get_temp_size_gb():
    temp_dir = tempfile.gettempdir()
    total_size = 0
    for root, _, files in os.walk(temp_dir):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total_size += os.path.getsize(fp)
            except OSError:
                pass

    return total_size / (1024 ** 3)


def format_gb_text(x_gb):
    if x_gb >= 10:
        return str(round(x_gb))
    if x_gb >= 1:
        return f"{x_gb:.1f}"
    return f"0.{int(x_gb * 10)}"


def get_bg_color(x, x_max=10):
    x = max(0, min(x, x_max))
    ratio = x / x_max
    white = (255, 255, 255)
    red = (255, 0, 0)
    r = int(white[0] + (red[0] - white[0]) * ratio)
    g = int(white[1] + (red[1] - white[1]) * ratio)
    b = int(white[2] + (red[2] - white[2]) * ratio)
    return (r, g, b)


def draw_centered_text_with_outline(draw, text, img_size, font, outline_width=3):
    w, h = img_size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (w - text_w) / 2 - bbox[0]
    y = (h - text_h) / 2 - bbox[1]

    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx * dx + dy * dy <= outline_width * outline_width:
                draw.text((x + dx, y + dy), text, font=font, fill='black')

    draw.text((x, y), text, font=font, fill='white')


def create_icon(x, text, size=256, x_max=10):
    img = Image.new('RGB', (size, size), get_bg_color(x, x_max))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arialbd.ttf", size=int(size * 0.4))
    draw_centered_text_with_outline(draw, text, (size, size), font)
    return img



ICON_DIR = os.path.join(os.getenv('APPDATA'), 'MemoryDefender')
os.makedirs(ICON_DIR, exist_ok=True)

SHORTCUT_PATH = os.path.join(os.path.expanduser('~'), 'Desktop', 'Clean Temp.lnk')

def generate_icon_filename():
    timestamp = int(time.time())
    return os.path.join(ICON_DIR, f"generated_{timestamp}.ico")

def set_icon(new_icon_path):
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(SHORTCUT_PATH)
        if not shortcut.Targetpath:
            return
        shortcut.IconLocation = new_icon_path
        shortcut.save()
    except Exception:
        pass


def cleanup_old_icons(icon_dir):
    for f in glob.glob(os.path.join(icon_dir, "generated_*.ico")):
        try:
            os.remove(f)
        except OSError:
            pass




def update_icon():
    x_gb = get_temp_size_gb()
    text = format_gb_text(x_gb)
    img = create_icon(x_gb, text, x_max=10)

    new_icon_path = generate_icon_filename()
    img.save(new_icon_path, sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
    set_icon(new_icon_path)

    for f in glob.glob(os.path.join(ICON_DIR, "generated_*.ico")):
        if f != new_icon_path:
            try:
                os.remove(f)
            except OSError:
                pass