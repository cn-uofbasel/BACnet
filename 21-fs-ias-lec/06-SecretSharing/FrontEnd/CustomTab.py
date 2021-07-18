from PyQt5.QtWidgets import QTabWidget, QTabBar

class TabBar(QTabBar):
    def __init__(self, expanded=-1, parent=None):
        super(TabBar, self).__init__(parent)
        self._expanded = expanded

    def tabSizeHint(self, index):
        size = super(TabBar, self).tabSizeHint(index)
        if index == self._expanded:
            offset = self.width()
            for index in range(self.count()):
                offset -= super(TabBar, self).tabSizeHint(index).width()
            size.setWidth(max(size.width(), size.width() + offset))
        return size


class TabWidget(QTabWidget):
    def __init__(self, expanded=-1, parent=None):
        super(TabWidget, self).__init__(parent)
        self.setTabBar(TabBar(expanded, self))

    def resizeEvent(self, event):
        self.tabBar().setMinimumWidth(self.width())
        super(TabWidget, self).resizeEvent(event)

