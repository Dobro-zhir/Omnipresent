import customtkinter as ctk
from typing import Callable


class Timebox(ctk.CTkFrame):
    """Компонент для ввода чисел с ведущим нулём (например, 01, 02, 03...)
       Позволяет кликами мыши или клавиатурой вводить значения в заданном диапазоне
       Визуал автоматически подстраивается под текущую тему customtkinter"""

    def __init__(self, *args,
                 width: int = 35,  # Ширина компонента
                 height: int = 27,  # Высота компонента
                 step_size: int = 1,  # На сколько изменяется значение при клике
                 min_value: int = 0,  # Минимальное значение (например 0)
                 max_value: int = 59,  # Максимальное значение (например 59)
                 command: Callable = None,  # Функция, которая вызывается при изменении значения
                 **kwargs):

        # Базовые настройки
        super().__init__(*args, width=width, height=height, **kwargs)

        # МОЖНО ОТКЛЮЧИТЬ
        self.configure(width=width, height=height)  # Явное управление размерами

        # Отключаем авто-ресайзинг, чтобы сохранить заданные размеры
        self.grid_propagate(False)

        # Настраиваем внутренние веса для корректного отображения элементов
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, minsize=25) # МОЖНО ОТКЛЮЧИТЬ
        self.grid_columnconfigure(0, minsize=30) # МОЖНО ОТКЛЮЧИТЬ

        # Параметры работы
        self.step_size = step_size
        self.min_value = min_value
        self.max_value = max_value
        self.command = command

        # Настройки автоматического увеличения при долгом нажатии
        self._repeat_job = None
        self.repeat_delay = 150
        self.acceleration_factor = 1.2
        self.click_delay = 300

        # Для обработки ручного ввода
        self.buffer = ""
        self.after_typing = None

        # # === КНОПКА УВЕЛИЧЕНИЯ ===
        # self.up_button = ctk.CTkButton(self, text="▲", width=5, height=5, font=("Arial", 5),
        #                                fg_color="transparent", hover=True,
        #                                command=lambda: self.change_value(1))
        # self.up_button.grid(row=0, column=0, padx=0, pady=(0, 0), sticky="ew")
        # # Долгое нажатие - автоматическое увеличение
        # self.up_button.bind("<ButtonPress-1>", lambda e: self.start_repeat(lambda: self.change_value(1)))
        # self.up_button.bind("<ButtonRelease-1>", lambda e: self.stop_repeat())

        # === ПОЛЕ ВВОДА ===
        self.entry = ctk.CTkEntry(self, width=30, height=25, border_width=1,
                                  font=("Arial", 18), justify="center",
                                  insertwidth=0)
        self.entry.grid(row=0, column=0, padx=1, pady=0, sticky="nsew")
        self.set(0)  # Установить начальное значение

        # Проверка ввода
        vcmd = (self.register(self.validate_input), "%P")
        self.entry.configure(validate="key", validatecommand=vcmd)
        self.entry.bind("<KeyRelease>", self.on_key_release)
        self.entry.bind("<FocusOut>", lambda e: self.correct_value())

        # Прокрутка колесом мыши
        self.entry.bind("<MouseWheel>", self.on_mouse_wheel)
        # Изменение курсора при наведении
        self.entry.bind('<Enter>', lambda e: self.entry.configure(cursor='hand2'))
        self.entry.bind('<Leave>', lambda e: self.entry.configure(cursor='xterm'))

        # # === КНОПКА УМЕНЬШЕНИЯ ===
        # self.down_button = ctk.CTkButton(self, text="▼", width=5, height=5, font=("Arial", 5),
        #                                  fg_color="transparent", hover=True, border_width=0,
        #                                  command=lambda: self.change_value(-1))
        # self.down_button.grid(row=2, column=0, padx=0, pady=(0, 0), sticky="ew")
        # # Долгое нажатие - автоматическое уменьшение
        # self.down_button.bind("<ButtonPress-1>", lambda e: self.start_repeat(lambda: self.change_value(-1)))
        # self.down_button.bind("<ButtonRelease-1>", lambda e: self.stop_repeat())

    def change_value(self, direction: int):
        """Изменяет значение на заданный шаг вверх или вниз"""
        try:
            current = int(self.entry.get())
            new_value = current + direction * self.step_size

            # Если вышли за пределы - возвращаемся к противоположному краю
            if new_value > self.max_value:
                new_value = self.min_value
            elif new_value < self.min_value:
                new_value = self.max_value

            self.set(new_value)
            if self.command:
                self.command()
        except ValueError:
            pass

    def start_repeat(self, func):
        """Запускает автоматическое повторение функции при долгом нажатии"""
        self.stop_repeat()
        self._current_func = func
        self._delay = self.repeat_delay
        self._repeat_job = self.after(self.click_delay, lambda: self._repeat_action(func))

    def _repeat_action(self, func):
        """Выполняет функцию с ускоряющейся задержкой"""
        func()
        self._delay = max(30, int(self._delay / self.acceleration_factor))
        self._repeat_job = self.after(self._delay, lambda: self._repeat_action(func))

    def stop_repeat(self):
        """Останавливает автоматическое повторение"""
        if self._repeat_job:
            self.after_cancel(self._repeat_job)
            self._repeat_job = None
        self._delay = self.repeat_delay

    def on_mouse_wheel(self, event):
        """Обработка прокрутки колесом мыши"""
        self.change_value(1 if event.delta > 0 else -1)

    def get(self) -> int:
        """Получить текущее значение из поля"""
        try:
            return int(self.entry.get())
        except ValueError:
            return 0

    def set(self, value: int):
        """Установить значение в поле с ведущим нулём (01, 02...)"""
        self.entry.delete(0, "end")
        self.entry.insert(0, f"{value:02d}")

    def validate_input(self, new_value):
        """Проверяет, что введены только цифры и не более 2 символов"""
        if new_value == "": return True
        if not new_value.isdigit() or len(new_value) > 2: return False
        return True

    def on_key_release(self, event):
        """Обработка ручного ввода с клавиатуры"""
        if event.char.isdigit():
            self.buffer += event.char
            self.entry.delete(0, "end")
            self.entry.insert(0, self.buffer[:2])

            if len(self.buffer) >= 2:
                self.correct_value()
                self.buffer = ""
                return

            if self.after_typing:
                self.after_cancel(self.after_typing)
            self.after_typing = self.after(1000, lambda: setattr(self, "buffer", ""))

    def correct_value(self):
        """Корректирует значение при выходе за границы диапазона"""
        try:
            value = int(self.entry.get())
            value = max(self.min_value, min(self.max_value, value))
            self.set(value)
        except ValueError:
            self.set(self.min_value)
        finally:
            if self.command:
                self.command()
            self.buffer = ""

