from motllo.ops import Folder, File, tree
from motllo.tree_parser import TreeParser
import random
from string import ascii_uppercase
import pytest


def test_tree_descent():
    mbp = Folder(
        "",
        [
            File("foo"),
            Folder("bar", [File("baz"), File("foobar")]),
            File("zzz"),
            Folder("meh", [File("buzz")]),
        ],
    )
    all_lines = list(tree(mbp))
    print("Original")
    print("\n".join(all_lines))
    parsed = TreeParser(all_lines)()
    print(parsed)
    all_lines = list(tree(parsed))
    print("parsed back")
    print("\n".join(all_lines))
    assert parsed == mbp


@pytest.mark.parametrize("execution_number", range(5))
@pytest.mark.parametrize("depth", range(5))
@pytest.mark.parametrize("width", range(5))
def test_randomised_tree_descent(execution_number, depth, width):
    sl = [l for l in ascii_uppercase * 50]
    random.shuffle(sl)

    def random_tree(depth, width):
        if depth == 0:
            return [File(sl.pop()) for _ in range(width)]
        folder_indexes = random.sample(range(width), random.randint(0, width - 1) + 1)
        results = [File(sl.pop()) for _ in range(width)]
        for index in folder_indexes:
            results[index] = Folder(sl.pop(), contents=random_tree(depth - 1, width))
        return results

    randomised = Folder("", contents=random_tree(3, 3))
    all_lines = [line for line in tree(randomised)]
    parsed = TreeParser(all_lines)()
    print(randomised)
    print("Randomised:")
    print("\n".join(all_lines))
    print(parsed)
    print("Parsed:")
    print("\n".join([l for l in tree(parsed)]))
    assert parsed == randomised
