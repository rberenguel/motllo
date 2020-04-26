from motllo.traverser import Traverser
from motllo.ops import Folder, File


def test_traverse_path():
    # The File/Folder hierarchy in path_traverser emulates pathlib's Path, so this needs to match
    mbp = Folder("base", [File("foo"), Folder("bar", [File("baz"), File("foobar")])])
    traversed = Traverser()(mbp)
    assert traversed == mbp
