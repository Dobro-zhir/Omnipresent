import customtkinter as ctk
from urlsentrylist import urls_lists

class AllLabel(ctk.CTkLabel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


num_labels = []  # Сохраняем созданные метки для последующего удаления
class UrlsNumber(AllLabel):
    def __init__(self, parent, queue_button=None, *args, **kwargs):
        self.queue_button = queue_button
        super().__init__(parent, *args, **kwargs)

        # Подписываемся на изменения urls_lists
        urls_lists.add_observer(self.create_and_delete_numerals)


        # Подписываемся на событие изменения checkbox через его bind_on_change
        # "Если мне передали объект queue_button, то подпишись на его
        # изменения и при каждом изменении вызывай метод self.create_and_delete_numerals()".
        if self.queue_button:
            self.queue_button.bind_on_change(self.create_and_delete_numerals)

    def create_and_delete_numerals(self):
        if self.queue_button.get() == 1:
            # Очищаем старые метки
            for label in num_labels:
                label.grid_forget()
                label.destroy()
            num_labels.clear()

            if self.queue_button.get() == 1:
                # Создаём новые метки
                for i, entry in enumerate(urls_lists, start=1):
                    label =ctk.CTkLabel(self.master, text=f"{i}.")
                    label.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
                    num_labels.append(label)

        if self.queue_button.get() == 0:
            for label in num_labels:
                label.grid_forget()
                label.destroy()
            num_labels.clear()

