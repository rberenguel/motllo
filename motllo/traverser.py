import logging
from pathlib import Path
from typing import List, Optional

from motllo.ops import File, Folder

logger = logging.getLogger("motllo.path_traverser")


def matches_glob(path: Path, globs: List[str]):
    """Checks if the path is matched by a list of globs"""
    if globs is None:
        return False
    for glob in globs:
        if path.match(glob):
            return True
    return False


class Traverser:
    """Traverser of (real or simulated) folder hierarchy. Callable class, configuration is passed to the constructor"""

    def __init__(self, ignore_globs=None):
        self.ignore_globs = ignore_globs
        self.initial_path: Optional[Path] = None

    def __call__(self, initial_path) -> Folder:
        self.initial_path = initial_path
        return self._traverser(self.initial_path, depth=0)

    def _handle_dir(self, path: Path, depth: int) -> Folder:
        logger.debug("Found folder: %s", path.name)
        return self._traverser(path, depth)

    def _handle_file(self, path: Path, base_path: Path) -> File:
        logger.debug("Found file: %s", path.name)
        with path.open("r") as data:
            try:
                contents = data.read()
            except Exception as exc:
                msg = f"Could not read file {path}, {exc}"
                logger.error(msg)
                contents = msg
        if self.initial_path is None:
            initial_as_posix = ""
        else:
            initial_as_posix = self.initial_path.as_posix()
        return File(
            path.name, basename=base_path.as_posix().replace(initial_as_posix, ""),
        ).set_contents(contents)

    def _traverser(self, base_path, depth=0):
        tree = []
        first_level = list(base_path.iterdir())
        logger.debug("Here is the first level: %s", first_level)
        for path in first_level:
            if matches_glob(path, self.ignore_globs):
                continue
            if path.is_dir():
                tree += [self._handle_dir(path, depth + 1)]
            else:
                tree += [self._handle_file(path, base_path)]
        return Folder(base_path.name, tree, depth)
