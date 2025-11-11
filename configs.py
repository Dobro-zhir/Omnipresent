import os
import json
from tkinter import filedialog
import sys

# ---Конфиг---
def get_exe_dir():
    """Возвращает путь к директории, где находится исполняемый файл (или скрипт)"""
    if getattr(sys, 'frozen', False):  # Если программа "заморожена" (создана через cx_Freeze)
        return sys._MEIPASS  # Временная директория при запуске .exe
    else:
        return os.path.dirname(os.path.abspath(__file__))  # Для обычного запуска из .py

# Путь к директории, где находится .exe (или .py)
EXE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(EXE_DIR, "settings.json")

def create_default_config():
    """Создаёт пустой файл settings.json, если его нет"""
    if not os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)
            print("Файл settings.json создан (пустой)")
        except Exception as e:
            print("Не удалось создать файл настроек:", e)

def load_setting(key):
    """Загружает значение по ключу из файла конфига"""
    create_default_config()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get(key)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Файл конфига повреждён или отсутствует")
        return None

def save_setting(key, value):
    """Сохраняет значение по ключу в файл конфига"""
    create_default_config()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        data[key] = value
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("Ошибка при сохранении настроек:", e)

def load_full_config():
    """Загружает весь конфиг как словарь"""
    create_default_config()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        print("Файл конфига повреждён или отсутствует")
        return {}

def choose_path(entry):
    create_default_config()
    initial = load_setting("download_path") or os.path.expanduser("~/Downloads")
    path = filedialog.askdirectory(title="Выберите папку для сохранения", initialdir=initial)
    if path:
        entry.delete(0, "end")
        entry.insert(0, path)
        save_setting("download_path", path)