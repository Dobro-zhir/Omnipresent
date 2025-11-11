class UrlsEntryList(list):
    def __init__(self, *args):
        super().__init__(*args)
        self._observers = []

    def add_observer(self, callback):
        self._observers.append(callback)

    def _notify(self):
        for callback in self._observers:
            callback()

        # Переопределяем основные методы, которые могут менять список

    def append(self, value):
        super().append(value)
        self._notify()


    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._notify()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._notify()

    def extend(self, values):
        super().extend(values)
        self._notify()


urls_lists = UrlsEntryList()

