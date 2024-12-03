from PySide6.QtCore import Signal, QObject
from types import UnionType
# TODO document code and explain why this is needed.

class __CallbackHook__:
    """Implements a traditional callback system for non-QT applications."""
    def __init__(self):
        self.__callables: list[callable] = []
        self.callables_count: int = 0
        self.disabled: bool = True

    def __call__(self):
        if self.disabled:
            return
        for c in self.__callables:
            c()

    def emit_(self):
        self.__call__()

    def connect_(self, func: callable):
        if func in self.__callables:
            return
        self.__callables.append(func)
        self.__increment_callables_count__(1)

    def disconnect_(self, func: callable):
        self.__callables.remove(func)
        self.__increment_callables_count__(-1)

    def __increment_callables_count__(self, n: int):
        self.callables_count += n
        self.disabled = self.callables_count == 0


class __QtHook__(__CallbackHook__, QObject):
    """Implements callback like system using signals designed for QT applications (useful for communicating across threads)."""
    __sig: Signal = Signal()

    def __init__(self):
        __CallbackHook__.__init__(self)
        QObject.__init__(self)

    def __call__(self):
        if self.disabled:
            return
        self.__sig.emit()

    def connect_(self, func: callable):
        self.__sig.connect(func)
        self.__increment_callables_count__(1)

    def disconnect_(self, func: callable):
        self.__sig.disconnect(func)
        self.__increment_callables_count__(-1)


HookType: UnionType = __CallbackHook__ | __QtHook__
def Hook(running_in_qt_app: bool = False) -> HookType:
    return __CallbackHook__() if not running_in_qt_app else __QtHook__()


def Binder(func: callable, *args, **kwargs) -> callable:
    return lambda: func(*args, **kwargs)
