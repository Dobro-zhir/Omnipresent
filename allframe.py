import customtkinter as ctk

class AllFrame(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


    def layout_grid(self, cols):
        """Автоматически собирает все дочерние виджеты и расставляет их по сетке"""
        cols = 3
        widgets = self.winfo_children()  # Получаем всех детей фрейма
        for i, widget in enumerate(widgets):
            row = i // cols
            col = i % cols
            widget.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")