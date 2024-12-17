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
        """Executes all callables if hook is not disabled."""
        if self.disabled:
            return
        for c in self.__callables:
            c()

    def emit_(self):
        """Calls call method."""
        self.__call__()

    def connect_(self, func: callable):
        """Appends callable to callables and counts."""
        if func in self.__callables:
            return
        self.__callables.append(func)
        self.__increment_callables_count__(1)

    def disconnect_(self, func: callable):
        """Removes callable from callables and counts."""
        self.__callables.remove(func)
        self.__increment_callables_count__(-1)

    def __increment_callables_count__(self, n: int):
        """Increments (or decrements) count of callables."""
        self.callables_count += n
        self.disabled = self.callables_count == 0


class __QtHook__(__CallbackHook__, QObject):
    """Implements callback like system using signals designed for QT applications (useful for communicating across threads)."""
    __sig: Signal = Signal()

    def __init__(self):
        __CallbackHook__.__init__(self)
        QObject.__init__(self)

    def __call__(self):
        """Emits signal if self is not disabled."""
        if self.disabled:
            return
        self.__sig.emit()

    def connect_(self, func: callable):
        """Connects callable function to signal and increments callables count."""
        self.__sig.connect(func)
        self.__increment_callables_count__(1)

    def disconnect_(self, func: callable):
        """Disconnects callable function to signal and decrements callables count."""
        self.__sig.disconnect(func)
        self.__increment_callables_count__(-1)


HookType: UnionType = __CallbackHook__ | __QtHook__
def Hook(running_in_qt_app: bool = False) -> HookType:
    """Returns an instance of __CallbackHook__ or __QtHook__ based on if the application is a Qt app or not."""
    return __CallbackHook__() if not running_in_qt_app else __QtHook__()


def Binder(func: callable, *args, **kwargs) -> callable:
    """Returns a function with bound arguments."""
    return lambda: func(*args, **kwargs)
