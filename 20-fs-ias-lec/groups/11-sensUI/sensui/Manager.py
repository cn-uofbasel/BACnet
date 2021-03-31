
class Manager:

    def __init__(self, items):
        if items is not None:
            self.__items = items
        else:
            self.__items = {}

    def containsId(self, id):
        return id is not None and id in self.__items

    def contains(self, item):
        return item is not None and item.id in self.__items

    def get(self, id):
        if self.containsId(id):
            return self.__items[id]

    def replace(self, item):
        if self.contains(item):
            self.__items[item.id] = item

    def add(self, item):
        if item is not None:
            self.__items[item.id] = item

    def delete(self, id):
        if self.containsId(id):
            del self.__items[id]

    def forAll(self, func, *args, **kwargs):
        self.forAllItems(self.__items, func, *args, **kwargs)

    def forAllItems(self, items, func, *args, **kwargs):
        if func is not None:
            for item in items.values():
                func(item, *args, **kwargs)

    def getAll(self):
        return self.__items

