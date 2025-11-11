import os
import subprocess
import sys

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

yt_dlp_path = os.path.join(get_base_dir(), 'yt-dlp.exe')
def update_yt_dlp():
    if not os.path.exists(yt_dlp_path):
        print(f"yt-dlp.exe не найден по пути: {yt_dlp_path}")
        sys.exit(1)

    try:
        # Запускаем обновление
        subprocess.run([yt_dlp_path, '-U'], check=True)
        print("yt-dlp успешно обновлен")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при обновлении yt-dlp: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_yt_dlp()

    import customtkinter as ctk
    from checkbuttons import CheckButtons, DownloadPreview, DownloadFragment, LinkQueue
    from defaultbuttons import DownloadButton
    from urlsentries import *
    from mainwindow import *
    from optionmenu import *
    from defaultbuttons import *
    from alllabel import *
    from configs import *
    from allframe import AllFrame
    from TRY_USE_TIME_BOX import TimeBoxes
    import os



    # ---Интерфейс---
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = MainWindow()

    # Создание конфига
    create_default_config()

    # === Используем root напрямую с grid ===
    root.grid_rowconfigure(0, weight=0)
    root.grid_rowconfigure(1, weight=0)
    root.grid_rowconfigure(2, weight=0)
    root.grid_rowconfigure(3, weight=0)
    root.grid_rowconfigure(4, weight=0)
    root.grid_columnconfigure(0, weight=0)
    root.grid_columnconfigure(1, weight=0)
    root.grid_columnconfigure(2, weight=0)

    # Frame окна
    settings_frame = AllFrame(root, width=200, height=100)
    settings_frame.grid(row=0, column=0, columnspan=1, sticky="n", padx=10, pady=10)
    settings_frame.grid_propagate(True)
    scroll_frame_for_urls_and_time_box = ctk.CTkScrollableFrame(root, width=630, height=200)
    scroll_frame_for_urls_and_time_box.grid(row=0, column=1, columnspan=1, rowspan=4, sticky="nsew", padx=10, pady=10)
    urls_frame = ctk.CTkFrame(scroll_frame_for_urls_and_time_box)
    urls_frame.grid(row=0, column=1, sticky="w", padx=10, pady=10)
    times_frame = AllFrame(scroll_frame_for_urls_and_time_box, width=100, height=100)
    times_frame.grid(row=0, column=2, sticky="ne", padx=10, pady=10)

    # Label
    result_label = AllLabel(root, text="Смените раскладку (язык), если не вставляется ссылка."
                                       "\n"
                                       "При ошибках включите/отключите cookie. Прочтите справку, если не помогло."
                            , font=("Segoe UI", 14, "bold")
                            , wraplength=400)
    result_label.grid(row=5, column=0, columnspan=2, sticky="nsew")
    choose_quality = AllLabel(root, text="Выберите разрешение: ", font=("Segoe UI", 14, "normal"))
    choose_quality.grid(row=2, column=0, sticky="w", padx=10)

    # Чек-Кнопки
    audio_button = CheckButtons(settings_frame, config_key="audio", text="Аудио отдельно")
    video_button = CheckButtons(settings_frame, config_key="video", text="Видео отдельно")
    together_button = CheckButtons(settings_frame, config_key="together", text="Объединить вместе")
    only_fragment_button = DownloadFragment(settings_frame, config_key="only_fragment", text="Только фрагмент")
    image_button = DownloadPreview(settings_frame, config_key="image", text="Скачать обложку")
    link_queue = LinkQueue(settings_frame, config_key="links", text="Очередь ссылок")


    # Размещение времени
    time_boxes = TimeBoxes(times_frame, fragment_check_box=only_fragment_button)

    # Размещение настроек
    settings_frame.layout_grid(cols=2)

    # Выбор разрешения
    video_quality_optionmenu = OptionMenu(root, width=300)
    video_quality_optionmenu.grid(row=2, column=0, columnspan=1, sticky="e")

    # Выбор куки
    cookie_optionmenu = CookieOptionMenu(root, width=300)
    cookie_optionmenu.grid(row=3, column=0, columnspan=1, sticky="e")
    choose_cookie = AllLabel(root, text="        Cookie файлы: ", font=("Segoe UI", 14, "normal"))
    choose_cookie.grid(row=3, column=0, sticky="w", padx=10)

    # Выбор пути сохранения
    choose_path_entry = AllEntry(root, width=350)
    choose_path_entry.grid(row=1, column=0, sticky="e")

    choose_path_button = ctk.CTkButton(root, width=50, text="Выбрать путь",
                                       command=lambda: choose_path(choose_path_entry))
    choose_path_button.grid(row=1, column=0, sticky="w", padx=10)

    open_choose_path_button = DefaultButtons(root, text="Открыть путь", command=lambda: open_path(choose_path_entry))
    open_choose_path_button.grid(row=4, column=0, sticky="e", padx=10)


    # Нарушаю правило ООП, но уже такая каша, что запихаю прямо сюда
    def open_path(entry_path):
        path = entry_path.get().strip()  # Получаем путь из поля ввода
        if os.path.exists(path):
            # Открываем папку в проводнике
            if os.name == 'nt':  # Windows
                os.startfile(path)


    # Окно ввода URL
    url_input = UrlsEntry(urls_frame, queue_button=link_queue)
    url_input.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    # Ввод ссылки. Для отладки.
    # url_input.insert(0, "https://www.youtube.com/watch?v=x5KhaCt1d3I")
    # https://www.youtube.com/watch?v=FCFImLRlACw

    # label номера ссылок
    urls_numbers = UrlsNumber(urls_frame, queue_button=link_queue)


    # Кнопка Скачать
    download_button = DownloadButton(
        root,
        text="Скачать",
        status_label=result_label,
        audio_checkbox=audio_button,
        video_checkbox=video_button,
        together_checkbox=together_button,
        choose_path_entry=choose_path_entry,
        quality_menu=video_quality_optionmenu,
        image_download=image_button,
        time_lists=time_boxes,
        download_fragment_button=only_fragment_button,
        cookie_settings=cookie_optionmenu
    )
    download_button.grid(row=5, column=1, sticky="e", padx=10)

    # Кнопка логов
    log_button = DefaultButtons(root, text="Логи", command=download_button.open_log_file)
    log_button.grid(row=5, column=0, sticky='w', padx=10, pady=5)

    # Кнопка закрепления
    pit_window = PinWindow(root)
    pit_window.grid(row=4, column=0)

    # Кнопка справки
    help_button = HelpButton(root)
    help_button.grid(row=4, column=0, sticky='w', padx=10, pady=10)

    # Запуск конфига
    config = load_full_config()
    if "download_path" in config:
        choose_path_entry.insert(0, config["download_path"])
    if link_queue:
        link_queue.on_toggle()

    root.mainloop()
