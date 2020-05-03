from motllo.traverser import Traverser
from motllo.ops import Folder, File


def test_traverse_path():
    # The File/Folder hierarchy in path_traverser emulates pathlib's Path, so this needs to match
    empty = File.EMPTY_CONTENTS.format(mode="r")
    mbp = Folder(
        "base",
        [
            File("foo").set_contents(empty),
            Folder(
                "bar",
                [File("baz").set_contents(empty), File("foobar").set_contents(empty)],
            ),
        ],
    )
    traversed = Traverser()(mbp)
    assert traversed == mbp
