import customtkinter as ctk
from configs import load_setting, save_setting


class OptionMenu(ctk.CTkOptionMenu):
    def __init__(self, parent, *args, **kwargs):
        self.video_quality = {  # quality(качество)
            "⚠️ Авто": "bestvideo+bestaudio/best", # Не рекомендуется
            # "⚠️ До 2160p включительно": "bestvideo*[height<=2160][ext=mp4][vcodec=h265]+bestaudio[ext=m4a][acodec=aac]/bestvideo*[height<=2160][ext=mp4][vcodec~='vp09']+bestaudio[ext=m4a]/bestvideo*[height<=2160][ext=mp4][vcodec~='avc1']+bestaudio[ext=m4a]/bestvideo*[height<=2160]+bestaudio/bestvideo*+bestaudio/best[height<=2160]/best",
            "⚠️ Только 2160p": "bestvideo*[height=2160][ext=mp4][vcodec=h265]+bestaudio[ext=m4a][acodec=aac]/bestvideo*[height=2160][ext=mp4][vcodec~='vp09']+bestaudio[ext=m4a]/bestvideo*[height=2160][ext=mp4][vcodec~='avc1']+bestaudio[ext=m4a]/bestvideo[height=2160][vcodec~='^((he|a)vc|h264)']+bestaudio/best[height=2160]",
            "⚠️ Только 1440p": "bestvideo*[height=1440][ext=mp4][vcodec=h265]+bestaudio[ext=m4a][acodec=aac]/bestvideo*[height=1440][ext=mp4][vcodec~='vp09']+bestaudio[ext=m4a]/bestvideo*[height=1440][ext=mp4][vcodec~='avc1']+bestaudio[ext=m4a]/bestvideo*[height=1440]+bestaudio/best[height=1440]",
            "До 1080p включительно": "bestvideo*[height<=1080][ext=mp4][vcodec=h264]+bestaudio[ext=m4a][acodec=aac]/bestvideo*[height<=1080][ext=mp4][vcodec~='avc1']+bestaudio[ext=m4a]/bestvideo*[height<=1080]+bestaudio/bestvideo*+bestaudio/best[height<=1080]/best",
            "До 720p включительно": "bestvideo*[height<=720][ext=mp4][vcodec=h264]+bestaudio[ext=m4a][acodec=aac]/bestvideo*[height<=720][ext=mp4][vcodec~='avc1']+bestaudio[ext=m4a]/bestvideo*[height<=720]+bestaudio/bestvideo*+bestaudio/best[height<=720]/best",
            "До 480p включительно": "bestvideo*[height<=480][ext=mp4][vcodec=h264]+bestaudio[ext=m4a][acodec=aac]/bestvideo*[height<=480][ext=mp4][vcodec~='avc1']+bestaudio[ext=m4a]/bestvideo*[height<=480]+bestaudio/bestvideo*+bestaudio/best[height<=480]/best",
            "До 360p включительно": "bestvideo*[height<=360][ext=mp4][vcodec=h264]+bestaudio[ext=m4a][acodec=aac]/bestvideo*[height<=360][ext=mp4][vcodec~='avc1']+bestaudio[ext=m4a]/bestvideo*[height<=360]+bestaudio/bestvideo*+bestaudio/best[height<=360]/best",
            "До 240p включительно": "bestvideo*[height<=240][ext=mp4][vcodec=h264]+bestaudio[ext=m4a][acodec=aac]/bestvideo*[height<=240][ext=mp4][vcodec~='avc1']+bestaudio[ext=m4a]/bestvideo*[height<=240]+bestaudio/bestvideo*+bestaudio/best[height<=240]/best",
            "144p и ниже))))": "bestvideo*[height<=144][ext=mp4][vcodec=h264]+bestaudio[ext=m4a][acodec=aac]/bestvideo*[height<=144][ext=mp4][vcodec~='avc1']+bestaudio[ext=m4a]/bestvideo*[height<=144]+bestaudio/bestvideo*+bestaudio/best[height<=144]/best"
        }

        # Словарь только для видео
        self.for_only_video = {
            "⚠️ Авто": "bestvideo*/best",
            "⚠️ Только 2160p": "bestvideo*[height=2160][ext=mp4][vcodec=h265]/bestvideo*[height=2160][ext=mp4][vcodec~='vp09']/bestvideo*[height=2160][ext=mp4]/best[height=2160]",
            "⚠️ Только 1440p": "bestvideo*[height=1440][ext=mp4][vcodec=h265]/bestvideo*[height=1440][ext=mp4][vcodec~='vp09']/bestvideo*[height=1440][ext=mp4]/best[height=1440]",
            "До 1080p включительно": "bestvideo*[height<=1080][ext=mp4][vcodec=h264]/bestvideo*[height<=1080][ext=mp4][vcodec~='avc1']/bestvideo[height<=1080][ext=mp4]/bestvideo*/bestvideo",
            "До 720p включительно": "bestvideo*[height<=720][ext=mp4][vcodec=h264]/bestvideo*[height<=720][ext=mp4][vcodec~='avc1']/bestvideo[height<=720][ext=mp4]/bestvideo*/bestvideo",
            "До 480p включительно": "bestvideo*[height<=480][ext=mp4][vcodec=h264]/bestvideo*[height<=480][ext=mp4][vcodec~='avc1']/bestvideo[height<=480][ext=mp4]/bestvideo*/bestvideo",
            "До 360p включительно": "bestvideo*[height<=360][ext=mp4][vcodec=h264]/bestvideo*[height<=360][ext=mp4][vcodec~='avc1']/bestvideo[height<=360][ext=mp4]/bestvideo*/bestvideo",
            "До 240p включительно": "bestvideo*[height<=240][ext=mp4][vcodec=h264]/bestvideo*[height<=240][ext=mp4][vcodec~='avc1']/bestvideo[height<=240][ext=mp4]/bestvideo*/bestvideo",
            "144p и ниже))))": "bestvideo*[height<=144][ext=mp4][vcodec=h264]/bestvideo*[height<=144][ext=mp4][vcodec~='avc1']/bestvideo[height<=144][ext=mp4]/bestvideo*/bestvideo"
        }

        # Загружаем сохранённое значение из конфига
        saved_quality = load_setting("selected_video_quality")
        default_value = saved_quality if saved_quality in self.video_quality else "До 1080p включительно"

        kwargs.setdefault("values", list(self.video_quality.keys()))
        kwargs.setdefault("command", self.option_menu_callback)
        # variable привязывает значение к строке
        kwargs.setdefault("variable", ctk.StringVar(value=default_value))
        # Вызываем конструктор родительского класса
        super().__init__(parent, *args, **kwargs)

    def get_selected_format(self):
        """Возвращает текущий формат yt-dlp"""
        choice = self.get()
        return self.video_quality.get(choice)

    def get_selected_key(self):
        """Возвращает ключ (например, 'До 1080p') по текущему формату"""
        selected_value = self.get_selected_format()
        for key, value in self.video_quality.items():
            if value == selected_value:
                return key
        return None

    # choice(выбор) принимает значение video_quality
    def option_menu_callback(self, choice):
        print("Выбрано разрешение", choice)
        save_setting("selected_video_quality", choice)  # Сохраняем в конфиг


# Пробуем вводить новую опцию
import customtkinter as ctk
from configs import load_setting, save_setting


class CookieOptionMenu(ctk.CTkOptionMenu):
    def __init__(self, parent, *args, **kwargs):
        # Словарь: отображаемое имя → значение для --cookies-from-browser
        self.cookie_browsers = {
            "Не использовать": "not use",
            "✔️ Перенести вручную (см. справку)": "own file",
            "✔️ Firefox": "firefox",
            "❔ Brave": "brave",
            "❔ Opera": "opera",
            "❔ Opera GX": "opera-gx",
            "❔ Vivaldi": "vivaldi",
            "❔ Arc": "arc",
            "❔ LibreWolf": "librewolf",
            "❔ Safari (macOS)": "safari",
            "⚠️ Chrome": "chrome",
            "⚠️ Chromium": "chromium",
            "⚠️ Edge": "edge",
            # Safari поддерживается только на macOS, но можно добавить опционально:
        }

        # Загружаем сохранённое значение из конфига
        saved_browser = load_setting("selected_cookie_browser")
        default_value = (
            saved_browser
            if saved_browser in self.cookie_browsers.values()
            else ""
        )

        # Находим ключ (отображаемое имя) по сохранённому значению
        display_default = "Не использовать cookies"
        for key, value in self.cookie_browsers.items():
            if value == default_value:
                display_default = key
                break

        kwargs.setdefault("values", list(self.cookie_browsers.keys()))
        kwargs.setdefault("command", self.option_menu_callback)
        kwargs.setdefault("variable", ctk.StringVar(value=display_default))

        super().__init__(parent, *args, **kwargs)

    def get_selected_browser(self):
        """Возвращает значение для --cookies-from-browser (например, 'chrome') или пустую строку."""
        display_name = self.get()
        return self.cookie_browsers.get(display_name, "")

    def get_selected_display_name(self):
        """Возвращает отображаемое имя (например, 'Chrome')."""
        return self.get()

    def option_menu_callback(self, display_name):
        """Сохраняет выбранное значение в конфиг."""
        browser_value = self.cookie_browsers.get(display_name, "")
        print("Выбран браузер для cookies:", browser_value or "—")
        save_setting("selected_cookie_browser", browser_value)