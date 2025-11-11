from PIL import Image  # Библиотека для работы с изображениями
import os
import customtkinter as ctk
from allframe import AllFrame
from configs import load_setting, save_setting
from urlsentries import urls_entry_objects
from alllabel import num_labels



class CheckButtons(ctk.CTkCheckBox):
    # master_frame = AllFrame
    def __init__(self, parent, config_key, *args, **kwargs):
        # if self.master_frame is None:
        #     raise Exception("Сначала установи CheckButtons.master_frame")
        # Вызываем конструктор родительского класса
        super().__init__(parent, *args, **kwargs)
        self.config_key = config_key
        self.configure(command=self.on_change)  # При клике вызываем on_change
        self.load_value()  # Загружаем значение из конфига

    def on_change(self):
        """Сохраняет значение при изменении"""
        save_setting(self.config_key, self.get())

    def load_value(self):
        """Загружает значение из файла при запуске"""
        value = load_setting(self.config_key)
        if value is not None:
            self.select() if value else self.deselect()



class DownloadPreview(CheckButtons):
    def __init__(self, parent, config_key, *args, **kwargs):
        super().__init__(parent, config_key, *args, **kwargs)
        self.download_path = load_setting("download_path") or os.path.expanduser("~/Downloads")


    # Я ПОНЯТИЯ НЕ ИМЕЮ КАК РАБОТАЕТ КОНВЕРТИРОВАНИЕ!!!!!!!
    def convert_thumbnail(self, video_title, input_ext=".webp", output_ext=".jpg"):
        """
        Конвертирует обложку по названию видео
        :param video_title: Название видео
        :param input_ext: Исходное расширение
        :param output_ext: Целевое расширение
        :return: Путь к новому файлу или None
        """
        for file in os.listdir(self.download_path):
            if file.endswith(input_ext) and video_title.lower() in file.lower():
                input_path = os.path.join(self.download_path, file)
                output_path = os.path.splitext(input_path)[0] + output_ext

                try:
                    with Image.open(input_path) as img:
                        # Исправляем формат для JPG
                        img_format = "JPEG" if output_ext == ".jpg" else output_ext[1:].upper()
                        img.save(output_path, format=img_format)

                    os.remove(input_path)
                    print(f"Конвертировано: {output_path}")
                    return output_path
                except Exception as e:
                    print(f"Ошибка при конвертации: {e}")
                    return None

        print("Исходный файл не найден")
        return None


class DownloadFragment(CheckButtons):
    def __init__(self, parent, config_key, *args, **kwargs):
        super().__init__(parent, config_key, *args, **kwargs)
        # self.configure(command=self.on_change)
        self._observers = []

        # При нажатии на чекбокс происходит событие
        self.configure(command=self.notify_observers)

    def bind_on_change(self, callback):
        """Подписываем внешний объект на изменения состояния чекбокса"""
        self._observers.append(callback)

    def unbind_on_change(self, callback):
        """Отписываем внешний объект"""
        if callback in self._observers:
            self._observers.remove(callback)

    def notify_observers(self):
        """Уведомляем всех подписчиков о том, что состояние изменилось"""
        for callback in self._observers:
            callback()

        # Важно! Вызываем оригинальный on_change, чтобы сохранить в конфиг
        # Костыль долбанный
        super().on_change()


class LinkQueue(CheckButtons):
    def __init__(self, parent, config_key, *args, **kwargs):
        super().__init__(parent, config_key, *args, **kwargs)
        self._observers = []

        # Привязываем обработчик события изменения состояния
        self.configure(command=self.on_toggle)  # Теперь вызывается только on_toggle

    def on_toggle(self):
        """Вызывается при изменении состояния чекбокса"""
        if self.get() == 0:
            for entry in urls_entry_objects[1:]:
                if entry.winfo_exists():
                    entry.destroy()
            del urls_entry_objects[1:]

            # Очищаем метки label
            for label in num_labels[:]:
                if label.winfo_exists():
                    label.grid_forget()
                    label.destroy()
            # Очищаем список, чтобы не было попыток удаления несуществующих меток
            num_labels.clear()

        # Важно! Вызываем оригинальный on_change, чтобы сохранить в конфиг
        super().on_change()
        # Уведомляем всех наблюдателей
        self.notify_observers()

    def bind_on_change(self, callback):
        """Подписываем внешний объект на изменения состояния чекбокса"""
        self._observers.append(callback)

    def unbind_on_change(self, callback):
        """Отписываем внешний объект"""
        if callback in self._observers:
            self._observers.remove(callback)

    def notify_observers(self):
        """Уведомляем всех подписчиков о том, что состояние изменилось"""
        for callback in self._observers:
            callback()


