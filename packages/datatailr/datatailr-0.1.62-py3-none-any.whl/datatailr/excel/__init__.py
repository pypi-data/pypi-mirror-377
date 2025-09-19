# type: ignore

# noqa: F401
try:
    from dt.excel import Addin
    from dt.excel import Queue
except ImportError:

    class DummyAddin:
        def __init__(self, name: str, description: str) -> None:
            self.name = name
            self.description = description

        def expose(self, **kwargs):
            def decorator(func):
                return func

            return decorator

        def run(self):
            pass

    class DummyQueue:
        def __init__(self) -> None:
            pass

        def push(self, value) -> None:
            pass

    Addin = DummyAddin
    Queue = DummyQueue


__all__ = ["Addin", "Queue"]
