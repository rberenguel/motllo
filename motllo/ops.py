from typing import Any, Dict, List, Optional


class Node:
    """Just to make mypy happy"""


class Contents:
    """Simulated context manager for file.open for tests and helpers"""

    def __init__(self, contents=None):
        self.contents = contents

    def read(self):
        """Just returns the contents"""
        return self.contents

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class File(Node):
    """Simulated File node, mimicking the API from Path needed to test and process a tree"""

    def __init__(
        self, path, basename="", replacements: Optional[List[Dict[str, str]]] = None
    ):
        self._path = path
        self.name = path
        self.contents: Optional[List[str]] = None
        self.replacements = replacements
        splitted = self.name.split(".")
        if len(splitted) < 2:
            self.suffix = None
        else:
            self.suffix = splitted[-1]
        self.basename = basename

    def as_posix(self):
        """Not really posix, but useful to generate links in the markdown result"""
        if self.basename == "":
            return self.name
        return self.basename + "/" + self.name

    def open(self, mode="meh"):
        """Simulates a content open"""
        if self.contents is None:
            return Contents(contents=mode)
        return Contents(contents=self.contents)

    def set_contents(self, contents):
        """Addts content as lines"""
        self.contents = contents.strip().split("\n")
        return self

    def set_replacements(self, replacements):
        """Adds replacement rules"""
        self.replacements = replacements
        return self

    @staticmethod
    def is_dir():
        """What do you think this is"""
        return False

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return str(self) == str(other)


class Folder(Node):
    """Simulated File node, mimicking the API from Path needed to test and process a tree"""

    def __init__(self, path, contents: List[Any] = None, depth=0, basename=""):
        self._path = path
        if contents is None:
            self._contents = []
        else:
            self._contents = contents
        self._depth = depth
        self.name = path
        if basename == "":
            self.basename = path
        else:
            self.basename = basename + "/" + path
        self.suffix = ""

    def __repr__(self):
        return self.name + f"[{self.iterdir()}]"

    def as_posix(self):
        "Returns a kind of _as_posix, used to generate basenames and linkx"
        return self.basename

    def append_to_contents(self, node: Node):
        """Adds files or folders to a folder"""
        self._contents += [node]

    def prune(self):
        """Removes empty folders"""
        for item in self.iterdir():
            if item.is_dir():
                item.prune()
        self._contents = list(
            filter(lambda x: not (x.is_dir() and x.is_empty()), self._contents)
        )
        return self

    def is_empty(self):
        """Obvious"""
        return len(self._contents) == 0

    @staticmethod
    def is_dir():
        """🙄"""
        return True

    def iterdir(self):
        """Returns the contents so we can iterate inside"""
        return self._contents

    def __eq__(self, other):
        return str(self) == str(other)


SPACE = "    "
BRANCH = "│   "
TEE = "├── "
LST = "└── "


def tree(base: Folder, prefix: str = ""):
    """From https://stackoverflow.com/a/59109706 by https://twitter.com/aaronchall
    """
    contents = list(base.iterdir())
    pointers = [TEE] * (len(contents) - 1) + [LST]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name
        if path.is_dir():
            extension = BRANCH if pointer == TEE else SPACE
            yield from tree(path, prefix=prefix + extension)


def url(path):
    """Generate a Markdown link for a file/folder"""
    urlable = path.as_posix().replace("/", "").replace(".", "").lower()
    if path.is_dir():
        return f"`{path.name}`"
    return f"[`{path.name}`](#{urlable})"


def tree_links(base: Folder, prefix: str = ""):
    """Generate a table of contents based on the tree itself"""
    contents = list(base.iterdir())
    pointers = ["- "] * len(contents)
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + url(path)
        if path.is_dir():
            yield from tree_links(path, prefix=prefix + SPACE)
