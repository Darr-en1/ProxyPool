import inspect
import pkgutil

from .base import BaseCrawler

# load classes subclass of BaseCrawler
classes = []
for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(name).load_module(name)  # type: ignore
    for class_name, value in inspect.getmembers(module):
        globals()[class_name] = value
        if (
            inspect.isclass(value)
            and issubclass(value, BaseCrawler)
            and value is not BaseCrawler
            and not getattr(value, "ignore", False)
        ):
            classes.append(value)
