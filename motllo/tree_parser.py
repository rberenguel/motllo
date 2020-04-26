import logging
from typing import List, Optional

from motllo.ops import File, Folder

logger = logging.getLogger("motllo.parse_tree")


def find_file_depth(line: str):
    """Find how deep in a hierarchy a file is by checking the tree"""
    for idx, item in enumerate(line):
        if item not in ["│", "├", "─", "└"] and not item.isspace():
            return idx // 4 - 1
    return -1


def nodename(line: Optional[str]):
    """Extract the file/folder name out of the tree representation"""
    if line is None:
        raise Exception("A node name can't be None. Please report this as an issue")
    return line[(find_file_depth(line) + 1) * 4 :]


class TreeParser:
    """Converts a text-tree into a tree of folders and files"""

    def __init__(self, tree):
        self._result = []
        self._previous_depth = -1
        self._previous_line: Optional[str] = ""
        self._tree = tree

    def _handle_folder(self):
        logger.debug("Adding a folder for Prev: %s", self._previous_line)
        if len(self._result) > 0:
            basename = self._result[-1].basename
        else:
            basename = ""
        self._result += [Folder(nodename(self._previous_line), basename=basename)]

    def __call__(self):
        self._parse(self._tree)
        if len(self._result) > 1:
            raise Exception(
                f"Some folders have not been folded properly, please report this issue, {self._result}"
            )
        return self._result[0]

    def _fold_folders(self):
        logger.debug("Closing and folding opened folders, %s", self._result)
        last = self._result.pop()
        self._result[len(self._result) - 1].append_to_contents(last)

    def _handle_last_line_of_folder(self, line):
        logger.debug("Adding last line of a folder and closing it, %s", line)
        last = self._result.pop()
        basename = last.basename
        last.append_to_contents(File(nodename(self._previous_line), basename=basename))
        self._result[self._previous_depth - 1].append_to_contents(last)
        self._previous_line = line

    def _close_opened_folders(self, line, _counter):
        counter = _counter
        logger.debug(
            "Closing and folding %s folders with Prev: %s, Cur: %s",
            counter,
            self._previous_line,
            line,
        )
        self._handle_last_line_of_folder(line)
        counter -= 1
        while counter > 0:
            self._fold_folders()
            counter -= 1

    def _add_to_open_folder(self, line, depth):
        logger.debug("Adding previous to folder, rolling line to next")
        if depth > len(self._result) - 1:
            raise Exception(f"Depth larger than result: {depth} | {self._result}")
        basename = self._result[depth].basename
        self._result[depth].append_to_contents(
            File(nodename(self._previous_line), basename=basename)
        )
        self._previous_line = line

    def _parse(self, tree: List[str]):
        """Parses a tree"""
        if len(tree) == 0:
            self._result = None
        for line in tree:
            logger.debug("Result: %s", self._result)
            depth = find_file_depth(line)
            logger.debug("Prev: %s Cur: %s Depth: %s", self._previous_line, line, depth)
            if depth > self._previous_depth:
                self._handle_folder()
                self._previous_line = line
            elif depth < self._previous_depth:
                self._close_opened_folders(line, self._previous_depth - depth)
            else:
                self._add_to_open_folder(line, depth)
            self._previous_depth = depth
        if self._previous_depth > 0:
            self._close_opened_folders(None, self._previous_depth)
        if self._previous_depth == 0 and self._previous_line is not None:
            logger.debug(
                "Closing and folding the final item with %s", self._previous_line
            )
            basename = self._result[self._previous_depth].basename
            self._result[self._previous_depth].append_to_contents(
                File(nodename(self._previous_line), basename=basename)
            )
