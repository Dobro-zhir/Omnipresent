import customtkinter as ctk # Переименование для облегчённого обращения
# from defaultbuttons import get_base_dir
import os
import sys
#
# Определение пути
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# icon_path = os.path.join(get_base_dir(), 'icon for program.ico')
class MainWindow(ctk.CTk): # Задаём для MainWindow все те же функции, что и для CTK, главного окна
    def __init__(self):
        super().__init__()
        # Устанавливаем размер окна
        window_width = 1150
        window_height = 350

        # Получаем размеры экрана включая системные панели
        # Обновляем информацию о размерах
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Вычисляем координаты для размещения окна по центру
        x = screen_width - window_width
        y = screen_height - window_height

        # Вычисляем координаты:
        x = (screen_width - window_width) // 2  # Центр по горизонтали
        y = screen_height - window_height # Прижимаем к низу

        # Устанавливаем геометрию окна
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Проверяем значения
        # print(f"Экран: {screen_width}x{screen_height}")
        # print(f"Окно: {window_width}x{window_height}")
        # print(f"Координаты: x={x}, y={y}")

        # Применяем геометрию с центральным расположением
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        # Фиксация размеров окна
        # self.resizable(width=False, height=False)

        # Даю название
        self.title("Omnipresent")
        # Задание иконки
        base_dir = get_base_dir()
        icon_path = os.path.join(base_dir, "ic.ico")
        self.wm_iconbitmap(icon_path)
