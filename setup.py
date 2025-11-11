import sys
from cx_Freeze import setup, Executable

# Файлы, которые нужно добавить
include_files = [
    ("processed_audio (mp3cut.net).mp3", "processed_audio (mp3cut.net).mp3"),
     ("settings.json", "settings.json"),  # помещаем в ту же директорию, что и EXE
     ("ic.ico", "ic.ico"),
    ("ffmpeg.exe", "ffmpeg.exe"),
    ("tech_error.mp3", "tech_error.mp3"),
    ("yt-dlp.exe", "yt-dlp.exe"),
    # ("yt-dlp_win", "yt-dlp_win")
]

# Опции сборки
build_exe_options = {
    "packages": [
        "customtkinter",
        # "multiprocessing",
        # "yt_dlp",
        # "PIL",
        "playsound",
        "re",
        "threading",
        "os",
        "sys",
        "datetime",
        # "pip"
    ],
    # "includes": [
    #     "json", "subprocess", "shutil", "urllib", "logging",
    #     "ctypes", "pathlib", "tempfile", "webbrowser",
    #     "yt_dlp.utils", "yt_dlp.compat", "yt_dlp.extractor",
    #     "yt_dlp.postprocessor", "yt_dlp.downloader", "yt_dlp.cli",
    # ],
    "excludes": [
        #"yt_dlp",
        # можно добавить другие модули, которые не нужны, например "tkinter" если не используете
    ],
    "include_files": include_files,
    # "excludes": ["tkinter"],
}

# GUI на Windows
base = "Win32GUI" if sys.platform == "win32" else None # Без консоли
# base = None  # С консолью

setup(
    name="Omnipresent",
    description="Omnipresent",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, target_name="Omnipresent", icon="ic.ico")]
)

# Для запуска прописать
# python setup.py build

# pyinstaller --onefile --add-data "ffmpeg.exe;." --add-data "settings.json;." --add-data "processed_audio (mp3cut.net).mp3;." --add-data "tech_error.mp3;." --add-data "ic.ico;." --icon=ic.ico --name="Omnipresent" main.py

# windowed — отключает консоль