from pathlib import Path
from typing import Literal


class DOMSource:
    def __init__(
        self,
        type: Literal["xml", "html"],
        path: str | None = None,
        content: str | None = None,
        encoding: str = "utf-8",
    ):
        """Instantiates the DOM Source object, path takes predence over content if both are present"""
        if path is None and content is None:
            return ValueError("path or content must be set")

        if path is not None and not Path(path).exists():
            return FileNotFoundError(f"file not found in path: {path}")

        if path is not None:
            self.source: Literal["path", "content"] = "path"
        else:
            self.source = "content"

        self.type: Literal["xml", "html"] = type
        self.path: str | None = path
        self.content: str | None = content
        self.encoding: str = encoding


class HTMLSource(DOMSource):
    def __init__(
        self,
        path: str | None = None,
        content: str | None = None,
        encoding: str = "utf-8",
    ):
        super().__init__("html", path, content, encoding)


class XMLSource(DOMSource):
    def __init__(
        self,
        path: str | None = None,
        content: str | None = None,
        encoding: str = "utf-8",
    ):
        super().__init__("xml", path, content, encoding)
