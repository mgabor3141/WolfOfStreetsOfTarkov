from PyQt5.QtCore import QAbstractNativeEventFilter, QAbstractEventDispatcher
from pyqtkeybind import keybinder


class WinEventFilter(QAbstractNativeEventFilter):
    def __init__(self, _keybinder):
        self.keybinder = _keybinder
        super().__init__()

    def nativeEventFilter(self, event_type, message):
        ret = self.keybinder.handler(event_type, message)
        return ret, 0


def init_hotkey(win):
    keybinder.init()
    keybinder.register_hotkey(win.winId(), "Ctrl+Alt+B", win.toggle_buying)

    # Install a native event filter to receive events from the OS
    win_event_filter = WinEventFilter(keybinder)
    event_dispatcher = QAbstractEventDispatcher.instance()
    event_dispatcher.installNativeEventFilter(win_event_filter)
