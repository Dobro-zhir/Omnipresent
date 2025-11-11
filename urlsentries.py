import customtkinter as ctk
from urlsentrylist import urls_lists  # urls_lists наследуется от list и отслеживает изменения


class AllEntry(ctk.CTkEntry):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


# Список для хранения объектов UrlsEntry (для UI)
urls_entry_objects = []


class UrlsEntry(AllEntry):
    # Задаём изначальные данные
    def __init__(self, parent, queue_button=None, placeholder_text="Вставьте ссылку", width=300, *args, **kwargs):
        # Инициализируем чек-бокс очереди ссылок
        self.queue_button = queue_button
        # Передаём изначальные данные в родительский класс CTkEntry
        super().__init__(parent, placeholder_text=placeholder_text, width=width, *args, **kwargs)
        # Задаём действие, когда происходит нажатие на клавиатуру
        self.bind("<KeyRelease>", self.check_and_add)


        # "Если мне передали объект queue_button, то подпишись на его
        # изменения и при каждом изменении вызывай метод check_and_add()".
        if self.queue_button:
            self.queue_button.bind_on_change(self.check_and_add)

        # Добавляем объект в список объектов Entry
        # Проверка, является ли текущее Entry в списке urls_entry_objects
        if self not in urls_entry_objects:
            # Если нет — добавляем
            urls_entry_objects.append(self)




    def update_urls_list(self):
        """Обновляет urls_lists, только если значение изменилось"""
        # Получаем текущие непустые URL'ы из всех Entry
        new_urls = [entry.get().strip() for entry in urls_entry_objects]
        #  if entry.get().strip() условие убрано, чтобы получать пустые значения тоже

        # Проверяем, нужно ли вообще обновлять длину списка
        if len(new_urls) != len(urls_lists):
            # Если длина изменилась — приходится обновлять полностью
            urls_lists[:] = new_urls  # Полное обновление
            # print("Добавление новой ссылки", urls_lists)
            # print(urls_entry_objects)
            return

        #
        updated = False
        # Если длина одинаковая — проверяем каждый элемент по индексу
        for i, url in enumerate(new_urls):
            if i >= len(urls_lists) or url != urls_lists[i]:
                urls_lists[i] = url
                updated = True

        # if updated:
        #     print("Изменение ссылки", urls_lists)
        #     print(urls_entry_objects)
        # else:
        #     print("Изменений не было")
        #     print(urls_entry_objects)

    # event передаёт значения из bind (self.bind("<KeyRelease>", self.check_and_add)),
    # чтобы иметь информацию о нажатых клавишах или другой информации
    def check_and_add(self, event=None):
        # ✅ Защита от множественного вызова метода (например, при быстром вводе)
        # Если _adding есть, И он равен True, → значит метод уже работает → не надо запускать его снова
        if hasattr(self, '_adding') and self._adding:
            return
        # Сказать "ДА", что "ПРОЦЕСС РАБОТАЕТ"
        self._adding = True

        # Блок try и finally нужен для того, чтобы регулировать создание окон entry
        # Чтобы окна при случае ошибки не наслаивались друг на друга
        try:
            # Проверка, включена ли очередь ссылок
            if self.queue_button.get() == 1:
                # Проверка на наличие виджета и что его строка не пустая
                if self.winfo_exists() and self.get().strip():
                    # ✅ Ограничение: максимум 8 Entry
                    if len(urls_entry_objects) >= 9:
                        # print("⚠️ Лимит достигнут — нельзя добавить больше 8 ссылок")
                        # Получаем последний Entry
                        last_entry = urls_entry_objects[-1]
                        # Проверяем, существует ли виджет и пуст ли он
                        if last_entry.winfo_exists():
                            # Уничтожаем виджет
                            last_entry.destroy()
                            # Удаляем из списка
                            urls_entry_objects.pop()
                            # Обновляем список, если изменили
                            # self.update_urls_list()
                        # Какой же я ахуенный...
                        # Обновление всех ссылок, чтобы виджеты порядкового номера и
                        # таймбоксов не создававались
                        self.update_urls_list()
                        return
                    # Если мы ТОЛЬКО печатаем внутри последнего поля entry, то:
                    if self is urls_entry_objects[-1]:
                        # Новая строка определяется как количество существующих полей + 1.
                        target_row = len(urls_entry_objects) + 1

                        """ 
                       ✅ Проверяем, занята ли строка перед созданием нового поля
                         Метод grid_slaves() возвращает список виджетов, которые были добавлены в сетку (grid) 
                         на указанную позицию.
                        ⚠️ Важно: один и тот же виджет может быть добавлен только в одну ячейку сетки. 
                        Но иногда при динамическом создании/удалении могут возникнуть конфликты. 
                        """
                        conflict = self.master.grid_slaves(row=target_row, column=1)
                        if conflict:
                            return  # Не создаём новый Entry, если строка занята

                        new_entry = UrlsEntry(self.master, queue_button=self.queue_button)
                        new_entry.grid(
                            row=target_row,
                            column=1,
                            padx=5,
                            pady=5,
                            sticky="w"
                        )
                        # Событие(bind) можно не переписывать, ибо оно уже есть в UrlsEntry
                        new_entry.bind("<KeyRelease>", new_entry.check_and_add)

                        # ✅ Убедимся, что такой объект ещё не добавлен
                        if new_entry not in urls_entry_objects:
                            urls_entry_objects.append(new_entry)
                        # else:
                            # print("⚠️ Объект уже существует в списке")

            # Если checkbox на очередь ссылок отключён, то:
            elif self.queue_button.get() == 0:
                # Удаляем все Entry, кроме первого
                for entry in urls_entry_objects[1:]:  # Начинаем с индекса 1
                    if entry.winfo_exists():
                        entry.destroy()
                # Очищаем список ОБЪЕКТОВ ENTRY, оставляя только первый элемент
                del urls_entry_objects[1:]

        finally:
            self._adding = False  # ✅ Всегда сбрасываем флаг после выполнения

        # Обновляем urls_lists после всех изменений
        # Метод update_urls_list() проверяет, какие ссылки были добавлены/изменены/удалены.
        self.update_urls_list()