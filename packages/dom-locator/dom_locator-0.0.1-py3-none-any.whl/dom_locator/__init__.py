__version__ = "0.0.1"

# Import core components
from .exceptions import ElementNotFoundError
from .dom_source import DOMSource, HTMLSource, XMLSource
from .locator import Locator

__all__ = [
    # Core classes
    "DOMSource",
    "HTMLSource",
    "XMLSource",
    "Locator",
    # Exceptions
    "ElementNotFoundError",
]
