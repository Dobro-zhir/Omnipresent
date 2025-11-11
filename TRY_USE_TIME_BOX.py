# === Импорты из оригинального кода ===
from time_spin_box import Timebox
import customtkinter as ctk
from urlsentrylist import urls_lists  # Список ссылок, на основе которого создаются поля времени

class TimeBoxes:
    def __init__(self, parent_frame, fragment_check_box):
        self.parent = parent_frame  # <-- Теперь передаём фрейм при инициализации
        self.fragment_check_box = fragment_check_box
        # === Инициализация контейнера для временных полей ===
        self.time_fields = []  # Список временных полей с привязкой к индексу
        # === Подписываемся на изменения списка ссылок ===
        urls_lists.add_observer(self.update_time_fields)

        # "Если мне передали объект fragment_check_box, то подпишись на его
        # изменения и при каждом изменении вызывай метод update_time_fields()".
        if self.fragment_check_box:
            self.fragment_check_box.bind_on_change(self.update_time_fields)

    def create_timebox(self, parent, row, column, min_val, max_val):
        # === Создание одного элемента таймбокса. Например, часов ===
        timebox = Timebox(parent, min_value=min_val, max_value=max_val)
        timebox.grid(row=row, column=column, padx=2, pady=5)
        return timebox

    def create_time_fields_for_row(self, parent, index):
        # === Создание всей строки таймбокса ===
        # Начало времени
        start_h = self.create_timebox(parent, row=index, column=0, min_val=0, max_val=23)
        start_m = self.create_timebox(parent, row=index, column=1, min_val=0, max_val=59)
        start_s = self.create_timebox(parent, row=index, column=2, min_val=0, max_val=59)
        start_time = (start_h, start_m, start_s)

        # Разделитель тайбоксов «—»
        line = ctk.CTkLabel(parent, text="—")
        line.grid(row=index, column=3, padx=5, sticky="ew")

        # Конец времени
        end_h = self.create_timebox(parent, row=index, column=4, min_val=0, max_val=23)
        end_m = self.create_timebox(parent, row=index, column=5, min_val=0, max_val=59)
        end_s = self.create_timebox(parent, row=index, column=6, min_val=0, max_val=59)
        end_time = (end_h, end_m, end_s)

        # Сохраняем все виджеты строки для последующего удаления
        all_widgets = start_time + (line,) + end_time

        return index, start_time, end_time, all_widgets  # ← Теперь возвращаем индекс

    def update_time_fields(self):
        # === Сравнивание текущее кол-во полей с кол-вом индексов ссылок и изменение ===
        current_count = len(self.time_fields)
        new_count = len(urls_lists)
        if self.fragment_check_box.get() == 1:
            # Удаляем лишние строки
            while len(self.time_fields) > new_count:
                removed = self.time_fields.pop()
                _, _, _, widgets = removed
                for widget in widgets:
                    widget.destroy()

            # Добавляем новые строки
            for i in range(current_count, new_count):
                fields = self.create_time_fields_for_row(self.parent, i)
                self.time_fields.append(fields)
        elif self.fragment_check_box.get() == 0:
            # Удаляем все таймбоксы
            for entry in self.time_fields:
                # Теперь извлекаем виджеты из кортежа
                index, start_time, end_time, widgets = entry
                for widget in widgets:
                    widget.grid_forget()
                    widget.destroy()
            self.time_fields.clear()

    def get_all_time_sections(self):
        """
        Собирает все временные промежутки (начало и конец) из интерфейса,
        преобразует их в секунды и сохраняет в словаре.
        Возвращает:
            dict: Словарь, где ключ — индекс URL-адреса, а значение — словарь с
                  'start_seconds' и 'end_seconds', представляющими временные метки начала и конца.
        """
        # Инициализируем пустой словарь для хранения временных промежутков
        time_sections = {}

        # Перебираем все строки временных полей, созданных в интерфейсе
        for idx, start_fields, end_fields, _ in self.time_fields:
            try:
                # Получаем значения из полей времени "Начала" и преобразуем их в целые числа
                start_hours, start_minutes, start_seconds = [
                    int(widget.get()) for widget in start_fields
                ]

                # Получаем значения из полей времени "Конца" и преобразуем их в целые числа
                end_hours, end_minutes, end_seconds = [
                    int(widget.get()) for widget in end_fields
                ]

                # Переводим время начала и конца в общее количество секунд
                start_total_seconds = (
                        start_hours * 3600 +  # часы в секунды
                        start_minutes * 60 +  # минуты в секунды
                        start_seconds  # добавляем секунды
                )

                end_total_seconds = (
                        end_hours * 3600 +
                        end_minutes * 60 +
                        end_seconds
                )

                # Проверяем, что начало меньше конца (временной отрезок корректен)
                # if start_total_seconds and end_total_seconds:
                    # Добавляем в словарь временной промежуток по индексу URL
                time_sections[idx] = {
                    'start_seconds': start_total_seconds,
                    'end_seconds': end_total_seconds
                }

            except ValueError:
                # Если какое-то поле пустое или содержит нечисловое значение — пропускаем
                continue

        # Возвращаем собранный словарь временных промежутков
        # print(time_sections)
        return time_sections