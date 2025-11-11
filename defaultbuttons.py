import customtkinter as ctk
import re # Библиотека, которая проверяет корректность ссылки
from urlsentrylist import urls_lists
import threading # Библиотека для разделения потоков
# import time
from datetime import datetime
import os # Для аудио
from playsound import playsound
# sys — модуль Python для взаимодействия с интерпретатором. Нужен нам для переопределения sys.exit().
import sys
# import yt_dlp
import subprocess


# Сохранял для вывода имени. Но, видимо, не потребуется.
# from configs import load_setting, save_setting

# Определение пути
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# Определение пути для ffmpeg
ffmpeg_path = os.path.join(get_base_dir(), 'ffmpeg.exe')
yt_dlp_path = os.path.join(get_base_dir(), 'yt-dlp.exe')



"""Ниже импорты от нейросети для обработки исключений в командной строке"""
"""Ну, т.е., чтобы не прерывался цикл скачивания, если включены фрагменты"""
# contextlib — библиотека, которая помогает писать контекстные менеджеры (типы конструкций with ...:).
import contextlib
# StringIO — позволяет создать "виртуальный файл" в памяти, чтобы перехватывать вывод в консоль.
from io import StringIO

class DefaultButtons(ctk.CTkButton):
    def __init__(self, parent, *args, **kwargs):
        # Вызываем конструктор родительского класса
        super().__init__(parent, *args, **kwargs)


class DownloadButton(DefaultButtons):
    def __init__(
            self,
            parent,
            # url_link,
            status_label,
            audio_checkbox=None,
            video_checkbox=None,
            together_checkbox=None,
            choose_path_entry=None,
            quality_menu=None,
            image_download=None,
            time_lists=None,
            download_fragment_button=None,
            cookie_settings=None,
            *args,
            **kwargs
    ):
        # if url_link is None:
        #     raise TypeError("Параметр 'url_link' обязателен")
        if status_label is None:
            raise TypeError("Параметр 'status_label' обязателен")
            # Сигнал тревоги
        # self.url_link = url_link
        self.status_label = status_label
        self.audio_checkbox = audio_checkbox
        self.video_checkbox = video_checkbox
        self.together_checkbox = together_checkbox
        self.choose_path_entry = choose_path_entry
        self.quality_menu = quality_menu
        self.image_download = image_download
        self.time_lists = time_lists  # Сохраняем для дальнейшего использования
        self.download_fragment_button = download_fragment_button
        self.cookie_settings = cookie_settings
        # Пояснение: для объявления взаимосвязи, чтобы работал command
        # Т.е. откуда брать ссылки
        # url_input = UrlsEntry(root)
        # download_button = DownloadButton(root, urls_entry=url_input)
        super().__init__(parent,
                         # command=lambda: threading.Thread(target=self.download_video).start(),
                         command=self.on_download_click,  # <-- Метод-обёртка для Thread, потокового скачивания
                         *args, **kwargs)



        # self.all_urls = []
    # Распределение потоковой нагрузки, чтобы работало GUI и не отключалось во время скачивания
    def on_download_click(self):
        self.configure(state="disabled")  # Блокируем повторное нажатие
        thread_for_download = threading.Thread(target=self.download_video, daemon=True)
        thread_for_download.start()

    # def download_video(self):
    #     try:
    #         import yt_dlp
    #     except ImportError:
    #         self.show_error("yt-dlp не установлен. Пожалуйста, перезапустите программу.")
    #         self.configure(state="normal")
    #         return

    def download_video(self):
        self.log_start_new()  # Перезаписываем старый лог
        #self.log_write(f"\n=== НАЧАЛО ЗАГРУЗКИ ===\n")
        # Берём ссылки для скачивания
        # Попытка взять и пробелы тоже
        # all_urls = [url.strip() for url in urls_lists if url.strip()]
        all_urls = [url for url in urls_lists]
        # print(all_urls)
        # Определяем путь для скачивания
        download_path = self.choose_path_entry.get().strip()
        if not download_path:
            self.show_error("Определите путь!!!")
            self.configure(state="normal")  # Кнопка скачивания снова доступна
            return
        # Получаем временные метки
        time_sections = self.time_lists.get_all_time_sections()

        # Получаем текущее время в формате ЧЧ-ММ-СС
        current_time = datetime.now().strftime("%H-%M-%S")
        start_load_int = datetime.now()

        # Я хер знает как это получилось, но получилось
        selected_format = self.quality_menu.get_selected_format()
        # print("selected_format:", repr(selected_format))
        selected_key = self.quality_menu.get_selected_key()
        # print("selected_key:", selected_key)
        video_format = self.quality_menu.for_only_video.get(selected_key)
        # print(video_format)
        cookie_settings_format = self.cookie_settings.get_selected_browser()

        # Задал куки
        def get_cookies_argument_for_CMD():
            # print("cookie_settings_format =", repr(cookie_settings_format))
            if cookie_settings_format == "not use":
                return []
            if cookie_settings_format == "own file":
                cookies_path = os.path.join(get_base_dir(), 'cookies.txt')
                # print("Путь к cookies.txt:", cookies_path)
                if os.path.exists(cookies_path):
                    return ['--cookies', cookies_path]
                else:
                    # print(f"[ПРЕДУПРЕЖДЕНИЕ] cookies.txt не найден в папке программы")
                    return []
            # Из-за недавних обновлений у YouTube, теперь невозможно скачивать
            # только аудио или только видео вместе с куки, не знаю почему это
            # так работает, но во всяком случае надо отключить
            if self.together_checkbox.get() == 0:
                return []
            if cookie_settings_format:
                return ['--cookies-from-browser', cookie_settings_format]

                # ydl_options_together += get_cookies_argument_for_CMD()

        def get_cookies_argument_for_API():
            # Получаем путь к базовой директории
            cookies_path = os.path.join(get_base_dir(), 'cookies.txt')
           #  print("Путь к cookies.txt:", cookies_path)

            if os.path.exists(cookies_path):
                return {'cookiefile': cookies_path}  # yt-dlp поддерживает такой формат
            else:
                # print(f"[ПРЕДУПРЕЖДЕНИЕ] cookies.txt не найден в папке программы")
                return {}

        # Проигрывать звук завершения или ошибки
        self.all_okay_download = True

        # Оборачиваем всё нахуй в цикл, чтобы скачалось каждое видео
        # А также делим при помощи enumerate на индекс и ссылку, чтобы можно было работать
        # с отрезками видео
        for idx, url in enumerate(all_urls):

            # Игнорирование пустых строк, но само скачивание никак не страдает!
            if not url.strip():
                end_load = datetime.now().strftime('%H:%M:%S')
                # print(f"Пустая строка на №{idx+1}")
                # self.show_error(f"Пустая строка на №{idx+1}, пропуск.")
                self.log_write(f"{end_load} [PASS] Пустая строка на №{idx+1}, игнорирование.")
                continue

            # === Скачивание обложки ===
            # ydl_options_image = {
            #     'outtmpl': '%(title)s.%(ext)s',
            #     'writethumbnail': True,
            #     # 'quiet': True,  # отключает вывод в консоль
            #     # 'no_warnings': True, # Отключает предупреждения, лучше оставить
            #     # 'extract_flat': True,  # ускоряет процесс, извлекает только базовую инфу
            #     'skip_download': True,  # Не скачиваем само видео
            #     'thumbnailformat': 'webp',  # можно указать jpg
            #     'paths': {'home': download_path},
            #     'ffmpeg_location': f'{ffmpeg_path}',
            #     'extractor_args': {
            #         'youtube': {
            #             'player_client': ['default', '-tv_simply'],
            #         },
            #     },
            #     **get_cookies_argument_for_API()
            # }
            # перебираем ссылки из списка чтобы скачать обложку

            # Скачивание обложки первым делом
            # Хорошо было бы отключить повторное скачивание обложки, если ссылка повторяется.
            # НО! Мне лень. Хотя можно это реализовать через проверку повторяющихся url в списке.
            # Однако слишком много геморра для вонючих обложек...
            # Старый код
            # try:
            #     if self.image_download.get() == 1:
            #         self.show_message(f"Скачивание обложки №{idx+1}")
            #         with yt_dlp.YoutubeDL(ydl_options_image) as ydl:
            #             result = ydl.extract_info(url, download=True)
            #             video_title = result.get('title', 'unknown_title')
            #
            #         # Конвертирование, ПОНЯТИЯ НЕ ИМЕЮ КАК
            #         self.image_download.convert_thumbnail(video_title=video_title, input_ext=".webp", output_ext=".jpg")
            #         self.show_message(f"Обложка №{idx+1} успешно скачана")
            #         self.log_write(f"[OK] Обложка №{idx+1} успешно скачана")
            #         if self.audio_checkbox.get() == 0 and self.video_checkbox.get() == 0 and self.together_checkbox.get() == 0:
            #             continue
            # except Exception as e:
            #     self.show_message(f"Ошибка при скачивании/конвертации изображения: {e}")

# Новый код: Чёт не все функции понял, но работает... значит, не трогаем.

            try:
                if self.image_download.get() == 1:
                    self.show_message(f"Скачивание обложки №{idx + 1}")
                    cmd = [
                        yt_dlp_path,
                        '--write-thumbnail',
                        '--skip-download',
                        '--quiet',
                        '--output', '%(title)s.%(ext)s',
                        '--convert-thumbnails', 'jpg',
                        '--ffmpeg-location', ffmpeg_path,
                        '--paths', download_path,
                        '--extractor-args', 'youtube:player_client=default,-tv_simply',
                        url
                    ]
                    cmd += get_cookies_argument_for_CMD()

                    result = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )

                    if result.returncode == 0:
                        # self.show_message(f"Обложка №{idx + 1} успешно скачана")
                        # self.log_write(f"[OK] Обложка №{idx + 1} успешно скачана")
                        if (self.audio_checkbox.get() == 0 and
                                self.video_checkbox.get() == 0 and
                                self.together_checkbox.get() == 0):
                            pass  # или continue, если внутри цикла
                    else:
                        raise Exception(result.stderr.strip() or "Неизвестная ошибка yt-dlp")
            except Exception as e:
                self.show_message(f"Ошибка при скачивании обложки: {e}")
                self.all_okay_download = False



            # Настройки ydl-dlp
            # В принципе они тут не нужны, но визуально понятнее чо зачем
            # Актуально ток для API
            ydl_options_audio_only = [
                '--output', '%(title)s.%(ext)s',
                '--ffmpeg-location', ffmpeg_path,
                '--paths', download_path,
                '--extractor-args', 'youtube:player_client=default,-tv_simply',
                url
            ]
            ydl_options_audio_only += get_cookies_argument_for_CMD()

            ydl_options_video_only = [
                '--output', '%(title)s.%(ext)s',
                '--ffmpeg-location', ffmpeg_path,
                '--paths', download_path,
                '--extractor-args', 'youtube:player_client=default,-tv_simply',
                url
            ]
            ydl_options_video_only += get_cookies_argument_for_CMD()

            ydl_options_together = [
                '--output', '%(title)s.%(ext)s',
                '--ffmpeg-location', ffmpeg_path,
                '--paths', download_path,
                '--extractor-args', 'youtube:player_client=default,-tv_simply',
                url
            ]
            ydl_options_together += get_cookies_argument_for_CMD()

            ydl_options_video_separately = [
                '--output', '%(title)s.%(ext)s',
                '--ffmpeg-location', ffmpeg_path,
                '--paths', download_path,
                '--extractor-args', 'youtube:player_client=default,-tv_simply',
                url
            ]
            ydl_options_video_separately += get_cookies_argument_for_CMD()

            ydl_options_audio_separately = [
                '--output', '%(title)s.%(ext)s',
                '--ffmpeg-location', ffmpeg_path,
                '--paths', download_path,
                '--extractor-args', 'youtube:player_client=default,-tv_simply',
                url
            ]
            ydl_options_audio_separately += get_cookies_argument_for_CMD()

            # Опеределение формата из optionmenu
            # Получаем формат видео и ключ (название качества)
            # # Я хер знает как это получилось, но получилось
            # selected_format = self.quality_menu.get_selected_format()
            # # print("selected_format:", repr(selected_format))
            # selected_key = self.quality_menu.get_selected_key()
            # # print("selected_key:", selected_key)
            # video_format = self.quality_menu.for_only_video.get(selected_key)
            # # print(video_format)
            # cookie_settings_format = self.cookie_settings.get_selected_browser.get()


            # Проверяем, есть ли временные метки для этой ссылки, при условии, что
            # чек-бокс, отвечающий за скачивание фрагментов, включен
            if self.download_fragment_button.get() == 1:
                section_info = time_sections.get(idx)
                if section_info and isinstance(section_info, dict):
                    start = section_info.get('start_seconds')
                    end = section_info.get('end_seconds')
                    if start is not None and end is not None and start < end:
                        # ydl_options['download_sections'] = f'*{start}-{end}'
                        pass  # Здесь можно активировать скачивание части видео
                    else:
                        end_load = datetime.now().strftime('%H:%M:%S')
                        if not url.strip():
                            # print(f"Пустая строка на №{idx+1}")
                            # self.show_error(f"Пустая строка на №{idx+1}, пропуск.")
                            self.log_write(f"{end_load} [PASS] Пустая строка на №{idx + 1}, игнорирование.")
                            continue
                        self.show_error(f"Неверные значения времени для фрагмента №{idx+1}"
                                        f"\nОн будет пропущен.")
                        self.log_write(f"{end_load} [ERROR] Неверные значения времени для фрагмента №{idx + 1}."
                                       f" Пропуск загрузки.")
                        self.configure(state="normal")  # Кнопка скачивания снова доступна
                        self.all_okay_download = False
                        continue
                else:
                    if not url.strip():
                        # print(f"Пустая строка на №{idx+1}")
                        # self.show_error(f"Пустая строка на №{idx+1}, пропуск.")
                        self.log_write(f"[PASS] Пустая строка на №{idx + 1}, игнорирование.")
                        continue
                    self.show_error(f"Неверные данные о временном промежутке для файла №{idx+1}"
                                    f"\nОн будет пропущен.")
                    self.log_write(f"[ERROR] Неверные значения времени для фрагмента №{idx + 1}."
                                   f" Пропуск загрузки.")
                    self.configure(state="normal")  # Кнопка скачивания снова доступна
                    self.all_okay_download = False
                    continue

            # Проверка на выбор формата (audio, video)
            if not self.audio_checkbox.get() and not self.video_checkbox.get():
                self.show_error("Не выбран формат (аудио/видео/обложка)")
                self.configure(state="normal")  # Кнопка скачивания снова доступна
                self.all_okay_download = False
                continue

            if self.together_checkbox.get() == 1:
                # Если "Объединить" активировано, но не выбраны оба "Аудио" и "Видео"
                if not (self.audio_checkbox.get() == 1 and self.video_checkbox.get() == 1):
                    #➡️ Это значит: "Если не оба выбраны сразу, тогда делаем код ниже".
                    self.show_error("Чтобы использовать объединение, выберите формат и аудио, и видео")
                    self.all_okay_download = False
                    continue
                # Если всё ОК, выбираем лучший формат
                # ydl_options_together['format'] = f"{selected_format}"
                # ydl_options_together['outtmpl'] = f'%(title)s_№{idx+1}_%(resolution)s.%(ext)s'
                ydl_options_together += ['--format', selected_format]
                ydl_options_together += ['--output', f'%(title)s_№{idx+1}_%(resolution)s.%(ext)s']
                # Если включено фрагментарное скачивание
                if self.download_fragment_button.get() == 1:
                    # ydl_options_together['download_sections'] = all_time
                    ydl_options_together = [
                        '--download-sections', f'*{start}-{end}',
                        # Необходимо скачивание с таймером, если скачивается сразу несколько кусков. Так надо
                        # чтобы yt-dlp понимал, что файлы скачиваются разные. Такие дела.
                        '--output', f'%(title)s_№{idx+1}_%(resolution)s_{current_time}.%(ext)s', # {int(time.time())}
                        '-f', selected_format,
                        '--paths', f'{download_path}',
                        # '--verbose', # отладка
                        '--no-overwrites', # Функция для повторного скачивания одной и той же ссылки
                        '--ffmpeg-location', f'{ffmpeg_path}',
                        '--extractor-args', "youtube:player-client=default,-tv_simply",
                        # '--no-cache-dir',
                        # '--ignore-config',
                        # '--cookies-from-browser', 'chrome',
                        # '--cookies', 'D:\\IT\\YouTube-Video Downloader\\build\\exe.win-amd64-3.13\\cookies.txt',
                        url # https://www.youtube.com/watch?v=ZFa8i7dbHsg&t=8s
                        # f'{url}?t={int(time.time())}'
                    ]
                    ydl_options_together += get_cookies_argument_for_CMD()

            if self.audio_checkbox.get() == 1 and self.video_checkbox.get() == 1:
                    if self.download_fragment_button.get() == 1:
                        ydl_options_audio_separately = [
                            '--download-sections', f'*{start}-{end}',
                            '--output', f'%(title)s_№{idx+1}_%(resolution)s_{current_time}.%(ext)s',
                            '-f', 'bestaudio[ext=m4a][acodec=aac]/bestaudio[ext=m4a]/bestaudio',
                            '--paths', download_path,
                            #'--verbose',
                            '--no-overwrites',
                            '--ffmpeg-location', f'{ffmpeg_path}',
                            '--extractor-args', "youtube:player-client=default,-tv_simply",
                            url
                        ]
                        ydl_options_audio_separately += get_cookies_argument_for_CMD()
                        ydl_options_video_separately = [
                            '--download-sections', f'*{start}-{end}',
                            '--output', f'%(title)s_№{idx+1}_%(resolution)s_{current_time}.%(ext)s',
                            '-f', video_format,
                            '--paths', download_path,
                            #'--verbose',
                            '--no-overwrites',
                            '--ffmpeg-location', f'{ffmpeg_path}',
                            '--extractor-args', "youtube:player-client=default,-tv_simply",
                            url
                        ]
                        ydl_options_video_separately += get_cookies_argument_for_CMD()
                    if self.download_fragment_button.get() == 0:
                        # ydl_options_audio_separately['format'] = 'bestaudio[ext=m4a][acodec=aac]/bestaudio[ext=m4a]/bestaudio'
                        # ydl_options_audio_separately['outtmpl'] = f'%(title)s_№{idx+1}_%(resolution)s.%(ext)s'
                        # ydl_options_video_separately['format'] = f'{video_format}'
                        # ydl_options_video_separately['outtmpl'] = f'%(title)s_№{idx+1}_%(resolution)s.%(ext)s'
                        ydl_options_audio_separately += ['--format', 'bestaudio[ext=m4a][acodec=aac]/bestaudio[ext=m4a]/bestaudio']
                        ydl_options_audio_separately += ['--output', f'%(title)s_№{idx+1}_%(resolution)s.%(ext)s']
                        ydl_options_video_separately += ['--format', f'{video_format}']
                        ydl_options_video_separately += ['--output', f'%(title)s_№{idx+1}_%(resolution)s.%(ext)s']
            elif self.audio_checkbox.get() == 1:
                # ydl_options_audio_only['format'] = 'bestaudio[ext=m4a][acodec=aac]/bestaudio[ext=m4a]/bestaudio'
                # ydl_options_audio_only['outtmpl'] = f'%(title)s_№{idx+1}_%(resolution)s.%(ext)s'
                ydl_options_audio_only += ['--format', 'bestaudio[ext=m4a][acodec=aac]/bestaudio[ext=m4a]/bestaudio']
                ydl_options_audio_only += ['--output', f'%(title)s_№{idx+1}_%(resolution)s.%(ext)s']
                if self.download_fragment_button.get() == 1:
                    ydl_options_audio_only = [
                        '--download-sections', f'*{start}-{end}',
                        '--output', f'%(title)s_№{idx+1}_%(resolution)s_{current_time}.%(ext)s',
                        '-f', 'bestaudio[ext=m4a][acodec=aac]/bestaudio[ext=m4a]/bestaudio',
                        '--paths', download_path,
                        # '--verbose',
                        '--no-overwrites',
                        '--ffmpeg-location', f'{ffmpeg_path}',
                        '--extractor-args', "youtube:player-client=default,-tv_simply",
                        url
                    ]
                    ydl_options_audio_only += get_cookies_argument_for_CMD()
            elif self.video_checkbox.get() == 1:
                # ydl_options_video_only['format'] = f"{video_format}"
                # ydl_options_video_only['outtmpl'] = f'%(title)s_№{idx+1}_%(resolution)s.%(ext)s'
                ydl_options_video_only += ['--format', f"{video_format}"]
                ydl_options_video_only += ['--output', f'%(title)s_№{idx+1}_%(resolution)s.%(ext)s']
                if self.download_fragment_button.get() == 1:
                    ydl_options_video_only = [
                        '--download-sections', f'*{start}-{end}',
                        '--output', f'%(title)s_№{idx+1}_%(resolution)s_{current_time}.%(ext)s',
                        '-f', video_format,
                        '--paths', download_path,
                        # '--verbose',
                        '--no-overwrites',
                        '--ffmpeg-location', f'{ffmpeg_path}',
                        '--extractor-args', "youtube:player-client=default,-tv_simply",
                        url
                    ]
                    ydl_options_video_only += get_cookies_argument_for_CMD()

            """Разделённые способы скачивания"""
            # self.show_message(f"Подготовка к скачиванию {url}")
            try:
                if self.together_checkbox.get() == 1:
                    # Если "Объединить" активировано, но не выбраны оба "Аудио" и "Видео"
                    if not (self.audio_checkbox.get() == 1 and self.video_checkbox.get() == 1):
                        # ➡️ Это значит: "Если не оба выбраны сразу, тогда делаем код ниже".
                        self.show_error("Чтобы использовать объединение, выберите форматы и аудио, и видео")
                        self.all_okay_download = False
                        continue
                    # self.show_message(f"Скачивание видео о №{idx+1}")
                    if self.download_fragment_button.get() == 1:
                        self.show_message(f"Cкачивание фрагмента видео №{idx + 1}")
                        try:
                            self.run_ytdlp_with_subprocess(ydl_options_together, idx=idx, url=url)
                        except Exception as e:
                            pass
                            # self.show_error(f"Ошибка при скачивании фрагмента №{idx + 1}.\n{e}")
                            # self.log_write(f"[ERROR] Фрагмент №{idx + 1} {url} не удалось загрузить.\n{e}")
                        continue
                    if self.download_fragment_button.get() == 0:
                        self.show_message(f"Cкачивание видео №{idx+1}")
                        try:
                            # with yt_dlp.YoutubeDL(ydl_options_together) as downloader:
                            #     # Запускаем загрузку по ссылке
                            #     downloader.download([url])
                            self.run_ytdlp_with_subprocess(ydl_options_together, idx=idx, url=url)
                            # Если всё прошло хорошо

                            # self.show_message(f"Видео №{idx+1} успешно скачано!")
                            # self.log_write(f"[OK] Видео №{idx+1} {url} успешно скачано.")

                        # except yt_dlp.utils.DownloadError as e:
                        #     self.show_error(f"Ошибка при скачивании видео №{idx + 1}.\n{e}")
                        #     self.log_write(f"[ERROR] Видео №{idx + 1} {url} не удалось загрузить.\n{e}")
                        # except Exception as e:
                        #     self.show_error(f"Ошибка при скачивании фрагмента №{idx + 1}.\n{e}")
                        #     self.log_write(f"[ERROR] Видео №{idx + 1} {url} не удалось загрузить.\n{e}")
                        except Exception as e:
                            pass
                        continue
                if self.audio_checkbox.get() == 1 and self.video_checkbox.get() == 1:
                    if self.download_fragment_button.get() == 1:
                        # self.show_message(f"Скачивание фрагмента отдельно аудио и видео №{idx + 1}")
                        self.show_message(f"Скачивание фрагмента №{idx + 1}")
                        try:
                            self.run_ytdlp_with_subprocess(ydl_options_audio_separately, idx=idx, url=url)
                        except Exception as e:
                            pass
                            # self.show_error(f"Ошибка при скачивании фрагмента №{idx + 1}.\n{e}")
                            # self.log_write(f"[ERROR] Фрагмент №{idx + 1} {url} не удалось загрузить.\n{e}")
                        self.show_message(f"Скачивание фрагмента №{idx + 1}")
                        try:
                            self.run_ytdlp_with_subprocess(ydl_options_video_separately, idx=idx, url=url)
                        except Exception as e:
                            pass
                            # self.show_error(f"Ошибка при скачивании фрагмента №{idx + 1}.\n{e}")
                            # self.log_write(f"[ERROR] Фрагмент №{idx + 1} {url} не удалось загрузить.\n{e}")
                        continue
                    if self.download_fragment_button.get() == 0:
                        ### АУДИО
                        self.show_message(f"Скачивание отдельно аудио №{idx + 1}")
                        try:
                            self.run_ytdlp_with_subprocess(ydl_options_audio_separately, idx=idx, url=url)
                            # with yt_dlp.YoutubeDL(ydl_options_audio_separately) as downloader:
                            #     # Запускаем загрузку по ссылке
                            #     downloader.download([url])
                            # Если всё прошло хорошо
                            # self.show_message(f"Отдельно аудио №{idx + 1} успешно скачано!")
                            # self.log_write(f"[OK] Отдельно аудио №{idx + 1} {url} успешно скачано.")
                        # except yt_dlp.utils.DownloadError as e:
                        #     self.show_error(f"Ошибка при скачивании отдельно аудио №{idx + 1}.\n{e}")
                        #     self.log_write(f"[ERROR] Отдельно аудио №{idx + 1} {url} не удалось загрузить.\n{e}")
                        except Exception as e:
                            # self.show_error(f"Ошибка при скачивании отдельно аудио №{idx + 1}.\n{e}")
                            # self.log_write(f"[ERROR] Отдельно аудио №{idx + 1} {url} не удалось загрузить.\n{e}")
                            pass
                        ### ВИДЕО
                        self.show_message(f"Скачивание отдельно видео №{idx+1}")
                        try:
                            self.run_ytdlp_with_subprocess(ydl_options_video_separately, idx=idx, url=url)
                            # with yt_dlp.YoutubeDL(ydl_options_video_separately) as downloader:
                            #     # Запускаем загрузку по ссылке
                            #     downloader.download([url])
                            # # Если всё прошло хорошо
                            # self.show_message(f"Отдельно видео №{idx + 1} успешно скачано!")
                            # self.log_write(f"[OK] Отдельно видео №{idx + 1} {url} успешно скачано.")
                        # except yt_dlp.utils.DownloadError as e:
                        #     self.show_error(f"Ошибка при скачивании отдельно видео №{idx + 1}.\n{e}")
                        #     self.log_write(f"[ERROR] Отдельно видео №{idx + 1} {url} не удалось загрузить.\n{e}")
                        except Exception as e:
                        #     self.show_error(f"Ошибка при скачивании отдельно видео №{idx + 1}.\n{e}")
                        #     self.log_write(f"[ERROR] Отдельно видео №{idx + 1} {url} не удалось загрузить.\n{e}")
                        # self.show_message(f"Аудио и видео №{idx+1} успешно скачаны!")
                            pass
                        continue
                if self.audio_checkbox.get() == 1:
                    if self.download_fragment_button.get() == 1:
                        self.show_message(f"Скачивание фрагмента №{idx + 1}")
                        try:
                            self.run_ytdlp_with_subprocess(ydl_options_audio_only, idx=idx, url=url)
                        except Exception as e:
                            pass
                            # self.show_error(f"Ошибка при скачивании фрагмента №{idx + 1}.\n{e}")
                            # self.log_write(f"[ERROR] Фрагмент №{idx + 1} {url} не удалось загрузить.\n{e}")
                        continue
                    if self.download_fragment_button.get() == 0:
                        self.show_message(f"Скачивание отдельно аудио №{idx + 1}")
                        try:
                            self.run_ytdlp_with_subprocess(ydl_options_audio_only, idx=idx, url=url)
                            # with yt_dlp.YoutubeDL(ydl_options_audio_only) as downloader:
                            #     # Запускаем загрузку по ссылке
                            #     downloader.download([url])
                            # Если всё прошло хорошо
                            # self.show_message(f"Отдельно аудио №{idx + 1} успешно скачано!")
                            # self.log_write(f"[OK] Отдельно аудио №{idx + 1} {url} успешно скачано.")
                        # except yt_dlp.utils.DownloadError as e:
                        #     self.show_error(f"Ошибка при скачивании отдельно аудио №{idx + 1}.\n{e}")
                        #     self.log_write(f"[ERROR] Отдельно аудио №{idx + 1} {url} не удалось загрузить.\n{e}")
                        except Exception as e:
                            # self.show_error(f"Ошибка при скачивании отдельно аудио №{idx + 1}.\n{e}")
                            # self.log_write(f"[ERROR] Отдельно аудио №{idx + 1} {url} не удалось загрузить.\n{e}")
                            pass
                        continue
                if self.video_checkbox.get() == 1:
                    if self.download_fragment_button.get() == 1:
                        self.show_message(f"Скачивание фрагмента №{idx + 1}")
                        try:
                            self.run_ytdlp_with_subprocess(ydl_options_video_only, idx=idx, url=url)
                        except Exception as e:
                            pass
                            # self.show_error(f"Ошибка при скачивании фрагмента №{idx + 1}.\n{e}")
                            # self.log_write(f"[ERROR] Фрагмент №{idx + 1} {url} не удалось загрузить.\n{e}")
                        continue
                    if self.download_fragment_button.get() == 0:
                        ### ВИДЕО
                        self.show_message(f"Скачивание отдельно видео №{idx + 1}")
                        try:
                            self.run_ytdlp_with_subprocess(ydl_options_video_only, idx=idx, url=url)
                        #     with yt_dlp.YoutubeDL(ydl_options_video_only) as downloader:
                        #         # Запускаем загрузку по ссылке
                        #         downloader.download([url])
                        #     # Если всё прошло хорошо
                        #     self.show_message(f"Отдельно видео №{idx + 1} успешно скачано!")
                        #     self.log_write(f"[OK] Отдельно видео №{idx + 1} {url} успешно скачано.")
                        # except yt_dlp.utils.DownloadError as e:
                        #     self.show_error(f"Ошибка при скачивании отдельно видео №{idx + 1}.\n{e}")
                        #     self.log_write(f"[ERROR] Отдельно видео №{idx + 1} {url} не удалось загрузить.\n{e}")
                        except Exception as e:
                            pass
                            # self.show_error(f"Ошибка при скачивании отдельно видео №{idx + 1}.\n{e}")
                            # self.log_write(f"[ERROR] Отдельно видео №{idx + 1} {url} не удалось загрузить.\n{e}")
                        continue
            except Exception as e:
                # Выводим её в консоль
                self.show_error(f"Глобальная ошибка №{idx+1}\n{e}")
                self.log_write(f"[ERROR]Глобальная ошибка №{idx+1}\n"
                               f"{e}")
            finally:
                self.configure(state="normal")  # Кнопка скачивания снова доступна

        self.configure(state="normal")  # Кнопка скачивания снова доступна
        # Воспроизведение колокольчика при завершении загрузки
        #self.log_write(f"\n=== ОКОНЧАНИЕ ЗАГРУЗКИ ===\n")
        end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        end_load_int =  datetime.now()
        #  Окончание
        self.log_write(f"\n=== {end} ===\n")
        time_expenditure = end_load_int - start_load_int
        total_seconds = int(time_expenditure.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        readable_time = f"{hours} ч {minutes} м {seconds} с"
        self.log_write(f"Время загрузки: {readable_time}")
        try:
            # Получаем путь к колокольчику относительно скрипта
            if getattr(sys, 'frozen', False):
                # Если программа собрана через cx_Freeze
                script_dir = os.path.dirname(sys.executable)
            else:
                # Если запускается как обычный скрипт
                script_dir = os.path.dirname(os.path.abspath(__file__))
            if self.all_okay_download == False:
                sound_path = os.path.join(script_dir, "tech_error.mp3")
            if self.all_okay_download == True:
                sound_path = os.path.join(script_dir, "processed_audio (mp3cut.net).mp3")
            if not os.path.exists(sound_path):
                print("Звуковой файл не найден!")
                return
            # Воспроизводим звук
            playsound(sound_path)
            self.all_okay_download = True
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")

    # def run_ytdlp_with_download_sections(self, args, idx, url):
    #     """
    #     Выполняет скачивание фрагмента видео с помощью yt_dlp.
    #
    #     Задачи:
    #     - Не допустить завершения программы через sys.exit()
    #     - Перехватить вывод в консоль
    #     - Показать сообщение о результате (успех или ошибка)
    #     - Записать результат в лог
    #
    #     Аргументы:
    #         args: список аргументов для передачи в yt_dlp.main()
    #         idx: номер фрагмента (для отображения в интерфейсе)
    #         url: ссылка на видео (для логирования)
    #     """
    #
    #     # 1. СОХРАНЯЕМ оригинальную функцию sys.exit
    #     # Это нужно, чтобы восстановить её после выполнения yt_dlp.main(),
    #     # иначе мы можем сломать поведение выхода из приложения
    #     original_exit = sys.exit
    #
    #     # 2. ОПРЕДЕЛЯЕМ свою собственную "версию" sys.exit
    #     # Вместо того, чтобы завершать программу, она генерирует исключение SystemExit
    #     def custom_exit(*args):
    #         raise SystemExit(*args)
    #
    #     # 3. ПОДМЕНЯЕМ стандартный sys.exit на нашу реализацию
    #     # Теперь любой вызов sys.exit() внутри yt_dlp.main() будет бросать исключение,
    #     # вместо немедленного завершения программы
    #     sys.exit = custom_exit
    #
    #     # 4. ОСНОВНОЙ БЛОК try
    #     # Здесь происходит основная работа по запуску yt_dlp и обработке результата
    #     try:
    #
    #         # 5. ИСПОЛЬЗУЕМ contextlib.redirect_stdout(StringIO())
    #         # Это контекстный менеджер, который перенаправляет весь вывод в консоль
    #         # в "пустое место", то есть подавляет его.
    #         # Полезно, если ты запускаешь это из GUI и не хочешь видеть технический вывод yt-dlp.
    #         with contextlib.redirect_stdout(StringIO()):
    #
    #             # 6. ЗАПУСКАЕМ yt_dlp.main(args)
    #             # Это основной метод yt_dlp, который:
    #             #   - парсит аргументы командной строки
    #             #   - загружает видео/аудио по заданным правилам
    #             #   - завершает работу через sys.exit(0) при успехе или sys.exit(1) при ошибке
    #             yt_dlp.main(args)
    #
    #             # ⚠️ Эта строка НИКОГДА не выполняется!
    #             # Потому что yt_dlp.main() всегда вызывает sys.exit()
    #             pass
    #
    #     # 7. ЛОВИМ исключения SystemExit, которые были вызваны через наш custom_exit
    #     except SystemExit as e:
    #
    #         # 8. ПРОВЕРЯЕМ код возврата
    #         if e.code == 0:
    #             # ✅ УСПЕШНОЕ завершение
    #             # Сообщаем пользователю, что фрагмент скачан
    #             self.show_message(f"Скачивание фрагмента №{idx + 1} завершено.")
    #
    #             # Записываем событие в лог-файл
    #             self.log_write(f"[OK] Фрагмент №{idx + 1} {url} успешно скачан.")
    #
    #         else:
    #             # ❌ ОШИБКА при скачивании
    #             # Показываем ошибку в интерфейсе
    #             self.show_error(f"Ошибка при скачивании фрагмента №{idx + 1}.")
    #
    #             # Логируем ошибку
    #             self.log_write(f"[ERROR] Фрагмент №{idx + 1} {url} не удалось загрузить.")
    #
    #     # 9. finally — гарантирует восстановление оригинального sys.exit()
    #     # Даже если произошло исключение или всё прошло нормально
    #     finally:
    #         sys.exit = original_exit

    # Вместо него:
    def run_ytdlp_with_subprocess(self, args, idx, url):
        """
        Выполняет скачивание фрагмента видео с помощью yt-dlp.exe через subprocess.

        Аргументы:
            args: список аргументов командной строки (без пути к yt-dlp.exe)
            idx: номер фрагмента (для отображения в интерфейсе)
            url: ссылка на видео (для логирования)
        """

        # Полная передача аргументов и загрузка
        full_cmd = [yt_dlp_path] + args # + url

        try:
            # Подавляем вывод в консоль (GUI-режим)
            result = subprocess.run(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            end_load = datetime.now().strftime('%H:%M:%S')
            if result.returncode == 0:
                self.show_message(f"Скачивание №{idx + 1} завершено.")
                self.log_write(f"{end_load} [OK] Скачивание №{idx + 1} завершено.")
            else:
                # Выводим ошибку из stderr для диагностики
                error_msg = result.stderr.strip() or "Неизвестная ошибка yt-dlp"
                self.show_error(f"Ошибка при скачивании №{idx + 1}.")
                self.log_write(f"{end_load} [ERROR] №{idx + 1} не удалось загрузить.\n{error_msg}")
                self.all_okay_download = False

        except Exception as e:
            self.show_error(f"Исключение при запуске yt-dlp: {e}")
            self.log_write(f"[EXCEPTION???] №{idx + 1}"
                           f"\n{e}")
            self.all_okay_download = False

    def is_valid_url(self, url):
        """Простая проверка, является ли строка URL"""
        regex = re.compile(
            r'^(?:http|https)://'  # http:// или https://
            r'(?:\S+\.)*\S+'  # домен + путь
            , re.IGNORECASE)
        return re.match(regex, url) is not None

    def show_error(self, message):
        print("Ошибка:", message)
        if self.status_label:
            self.status_label.after(0, lambda: self.status_label.configure(text=message, text_color="red"))

    def show_message(self, message):
        """Обновляет текст лейбла (результат загрузки)"""
        # Разделение на потоки, чтобы не лагало
        print(message)
        if self.status_label is not None:
            # Делается через after, который отвечает за потоки
            # ❗ Выполнить обновление GUI из другого потока (например, фонового потока threading.Thread)
            # , потому что Tkinter не потокобезопасный.
            # Ты вызываешь .after(0, ...) — это значит, что функция будет выполнена немедленно,
            # но в контексте mainloop Tkinter .
            self.status_label.after(0, lambda: self.status_label.configure(text=message, text_color="white")) # config
        else:
            print("Status label не задан, вывод в консоль:", message)

    """ФУНКЦИЯ ЛОГИРОВАНИЯ"""
    def log_start_new(self):
        """Создает новый файл лога или перезаписывает старый"""
        # Получаем директорию, где находится .exe (или .py)
        if getattr(sys, 'frozen', False):
            # Если программа собрана через cx_Freeze
            exe_dir = os.path.dirname(sys.executable)
        else:
            # Если запускается как обычный скрипт
            exe_dir = os.path.dirname(os.path.abspath(__file__))

        self.log_file = os.path.join(exe_dir, "download_log.txt")
        with open(self.log_file, 'w', encoding='utf-8') as f:
            start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Запуск
            f.write(f"=== {start} ===\n\n")
            # f.write(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    def log_write(self, message):
        """Записывает строку в лог"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(message + "\n")

    def open_log_file(self):
        """Открывает лог-файл с помощью стандартной программы ОС"""
        if os.path.exists(self.log_file):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(self.log_file)
                # elif os.name == 'posix':  # macOS и Linux
                #     subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', self.log_file])
            except Exception as e:
                self.show_error(f"Ошибка открытия лога: {e}")
        else:
            self.show_error("Файл лога не найден!")



class PinWindow(DefaultButtons):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent,
                         text="Закрепить окно",
                         command=self.toggle_always_on_top,
                         *args, **kwargs
                         )

        self.parent = parent  # Сохраняем ссылку на главное окно


    def toggle_always_on_top(self):
        # Получаем текущее состояние окна
        current_state = self.parent.attributes("-topmost")

        # Меняем состояние на противоположное
        self.parent.attributes("-topmost", not current_state)

        # Обновляем текст кнопки
        if not current_state:
            self.configure(text="Открепить окно")
        else:
            self.configure(text="Закрепить окно")

class HelpButton(DefaultButtons):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent,
                         text="ЧаВо?!",
                         command=self.open_help_window,
                         *args, **kwargs
                         )

    def open_help_window(self):
        # Создаем новое окно Toplevel
        help_window = ctk.CTkToplevel(self.winfo_toplevel())
        help_window.title("Справка")
        help_window.geometry("740x550")

        # Делаем окно модальным # ШО? КАКИМ????
        help_window.transient(self.winfo_toplevel())
        help_window.grab_set()

        # Заголовок
        title_label = ctk.CTkLabel(help_window, text="Версия 1.2.3 | 6 ноября 2025", font=("Arial", 25, "bold"))
        title_label.pack(pady=5)

        # Добавляем текстовое поле с прокруткой
        textbox_frame = ctk.CTkFrame(help_window)
        textbox_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Прокрутка
        # scrollbar = ctk.CTkScrollbar(textbox_frame, orientation="vertical")
        # scrollbar.pack(side="right", fill="y")

        help_text = ctk.CTkTextbox(textbox_frame, wrap="word") #, yscrollcommand=scrollbar.set
        help_text.pack(fill="both", expand=True)

        # scrollbar.configure(command=help_text.yview)

        # --- Настройка шрифта ---
        default_font = ctk.CTkFont(family="Helvetica", size=20)  # Меняй здесь: size — размер шрифта
        # family="Helvetica" "Arial"
        help_text.configure(font=default_font)

        # Вставляем описание приложения
        description = (
            "\n❔ У меня ошибка, что делать?"
            "\n💬 Отключите/включите cookie, выбрав нужный браузер и авторизовавшись на площадке откуда "
            "пытаетесь загрузить. "
            "Если как неделю получаете ошибки, значит, у YouTube вышло критическое изменение и надо обновить программу."
            # "Из-за этого приложение"
            # " может запускаться чуть дольше обычного."
            "\n"
            "\n❔ Не могу загрузить только аудио у видео с возрастным ограничением, хотя выбрал cookie файлы. Что делать?"
            "\n💬 Ничего. Загрузить не получится."
            "\n"
            "\n❔ У меня не работают горячие клавиши (Ctrl+V, например), что делать?"
            "\n💬 Смените раскладку (язык)."
            "\n"
            "\n❔ Почему я хотел скачать одно видео, а началась загрузка всего плейлиста?"
            "\n💬 Под видео на YouTube есть кнопка «Поделиться», используйте её для корректной ссылки."
            "\n"
            "\n❔ Какие браузеры поддерживаются для cookie?"
            "\n💬 Firefox. Остальные не знаю. Все браузеры, основанные на сhromium, "
            "не позволяют читать cookie (вроде)."
            "\n"
            "\n❔ Что за консоль в начале?"
            "\n💬 Обновление yt-dlp — сервиса для загрузки, который и реализует всю логику."
            "\n"
            "\n❔ Какие сайты поддерживаются?"
            "\n💬 Все ныне существующие. Почти. Вот список:"
            "\nhttps://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md"
            "\n"
            "\n❔ Можно ли скачивать плейлисты?"
            "\n💬 Да, кроме служебных: «смотреть позже» или «понравившиеся»."
            "\n"
            "\n❔ Что такое очередь ссылок?"
            "\n💬 Это возможность загружать множество видео (макс. 8, искусственное ограничение). Можно "
            "так же подключить функцию фрагментов, и точечно скачать разные куски "
            "из одного видео. Если жмакнуть на «Очередь ссылок» дважды, то очистятся поля ввода. У фрагментов "
            "аналогично."
            "\n"
            "\n❔ Почему у «Авто», «2160p» и «1440p» разрешений стоит знак предупреждения?"
            "\n💬 При «Авто» площадка автоматически выбирает, какого формата/разрешения файлы загрузить. "
            "А разрешения «2160p» и «1440p» могут быть проблемными или вовсе не работать (с недавнего обновления "
            "YouTube)."
            "\n"
            "\n❗️ Инструкция по ручному внедрению cookie:"
            "\n1. Скачайте расширение для браузера «Get cookies.txt LOCALLY»"
            "\nhttps://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc"
            "\n2. Авторизуйтесь и зайдите на нужный сайт"
            "\n3. Откройте расширение, "
            "жмакните Export (убедитесь, что формат Netscape, это указано ниже)"
            "\n4. Переименуйте скачанный "
            "файл в cookies"
            "\n5. Переместите его в главную папку приложения, где находится «Omnipresent.exe»"
            "\nИмейте ввиду, что файлы cookies имеют ограниченный срок годности (минут 30), поэтому ошибка повторится. "
            "\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
            "\n\nУвы, но пауза и возобновление загрузки слишком заморочено для моих гуманитарных мозгов."
            " Поэтому, если хотите "
            "прекратить загрузку — просто дропните приложение."
            "\n\nЭто моя первая программа, да и на момент написания я изучал программирование всего 2 месяца, "
            "поэтому за баги, лаги, и неработающие функции не бейте — "
            "у меня лапки. Но можете обратиться куда-нибудь сюда:"
            "\n"
            "\nТГ — https://t.me/dobrozhir_official"
            "\nДС — https://discord.gg/eQ4nSd3zkM"
            "\nГИТ — https://github.com/Dobro-zhir (правда я хезе где там можно написать, АХАХХАХА)"
            "\nПочта — backup.dobrozhir@gmail.com"
            "\n"
            "\nПостараюсь помочь. Также выложу в ТГ актуальную версию с изменениями, если "
            "ютуб похерит текущий способ скачивания."
            "\n\nДанное приложение — это моё маленькое спасибо всему интернету за то, что он мне дал."
            "\n\nВы, кстати, тоже можете дать... мне на лапу:"
            "\nРубли — boosty.to/dobrozhir"
            "\nДоллАры — patreon.com/Dobrozhir"
            "\nКрипту — disk.yandex.ru/i/VuQbtI4_QZOHuw"
            "\n"
            "\n🤓"
        )
        help_text.insert("0.0", description)  # Вставка текста в начало
        help_text.configure(state="disabled")  # Блокируем редактирование

# Слишком кривое отображение виджетов, отключено
# class ChooseNameFile(DefaultButtons):
#     def __init__(self, parent, *args, **kwargs):
#         super().__init__(parent,
#                          text="Выбрать имя",
#                          command=self.toggle_dropdown,
#                          *args, **kwargs)
#
#         # Возможные параметры yt-dlp для имени файла
#         self.format_name_for_file = {
#             "Оригинальное название": "%(title)s",
#             "Имя автора": "%(uploader)s",
#             "Разрешение": "%(resolution)s",
#             "ID видео": "%(id)s"
#         }
#
#         # Переменные для переключателей
#         self.switch_vars = {key: ctk.BooleanVar(value=True) for key in self.format_name_for_file}
#
#         # Фрейм под выпадающее меню (изначально скрыт)
#         self.dropdown_frame = ctk.CTkFrame(self.master, width=250, height=180, corner_radius=8)
#         self.dropdown_frame.place_forget()
#
#         # Создание виджетов (чекбоксов) внутри dropdown
#         self.create_dropdown_widgets()
#
#         # Загружаем состояние из конфига при инициализации
#         self.load_state_from_config()
#
#         # Привязываем событие клика вне фрейма к root, чтобы не мешало кнопке
#         self.root = parent.winfo_toplevel()
#         self.root.bind("<Button-1>", self.on_click_outside)
#
#     def create_dropdown_widgets(self):
#         """Создаёт переключатели в выпадающем меню."""
#         self.switches = {}
#         for idx, label in enumerate(self.format_name_for_file.keys()):
#             switch = ctk.CTkSwitch(
#                 self.dropdown_frame,
#                 text=label,
#                 variable=self.switch_vars[label],
#                 onvalue=True,
#                 offvalue=False,
#                 command=self.save_state_to_config
#             )
#             switch.grid(row=idx, column=0, padx=10, pady=2, sticky="w")
#             self.switches[label] = switch
#
#     def toggle_dropdown(self):
#         """Отображает или скрывает выпадающее меню."""
#         if self.dropdown_frame.winfo_ismapped():
#             self.dropdown_frame.place_forget()
#         else:
#             # Обновляем позицию только после рендера окна
#             self.update_idletasks()
#
#             # Получаем абсолютные координаты кнопки
#             x = self.winfo_rootx()
#             y = self.winfo_rooty() + self.winfo_height() + 5  # Немного ниже кнопки
#
#             # Проверяем, чтобы меню не выходило за границы экрана
#             screen_width = self.winfo_screenwidth()
#             screen_height = self.winfo_screenheight()
#             dropdown_width = self.dropdown_frame.winfo_reqwidth()
#             dropdown_height = self.dropdown_frame.winfo_reqheight()
#
#             # Если меню выходит за правую границу экрана, корректируем x
#             if x + dropdown_width > screen_width:
#                 x = screen_width - dropdown_width
#
#             # Если меню выходит за нижнюю границу экрана, корректируем y
#             if y + dropdown_height > screen_height:
#                 y = self.winfo_rooty() - dropdown_height - 5  # Показываем выше кнопки
#
#             # Показываем меню
#             self.dropdown_frame.place(x=x, y=y)
#             self.dropdown_frame.lift()  # Поднимаем над другими виджетами
#
#     def on_click_outside(self, event):
#         """Скрывает меню, если клик вне него."""
#         if self.dropdown_frame.winfo_ismapped():
#             x_inside = self.dropdown_frame.winfo_rootx() <= event.x_root <= (
#                     self.dropdown_frame.winfo_rootx() + self.dropdown_frame.winfo_width())
#             y_inside = self.dropdown_frame.winfo_rooty() <= event.y_root <= (
#                     self.dropdown_frame.winfo_rooty() + self.dropdown_frame.winfo_height())
#
#             if not (x_inside and y_inside):
#                 self.dropdown_frame.place_forget()
#
#     def get_selected_values(self):
#         """
#         Возвращает словарь с выбранными ключами и значениями.
#         {
#             "keys": ["Оригинальное название", ...],
#             "values": ["%(title)s", ...]
#         }
#         """
#         selected_keys = [key for key, var in self.switch_vars.items() if var.get()]
#         selected_values = [self.format_name_for_file[key] for key in selected_keys]
#         return {
#             "keys": selected_keys,
#             "values": selected_values
#         }
#
#     def save_state_to_config(self):
#         """Сохраняет текущее состояние чекбоксов в файл конфига"""
#         selected_keys = [key for key, var in self.switch_vars.items() if var.get()]
#         save_setting("filename_format_selection", selected_keys)
#
#     def load_state_from_config(self):
#         """Загружает состояние чекбоксов из файла конфига"""
#         saved_selection = load_setting("filename_format_selection") or []
#         for key in self.switch_vars:
#             self.switch_vars[key].set(key in saved_selection)