from motllo.ops import Folder, File, tree
from motllo.markdown import build_tree, build_markdown
from motllo.build import _process_markdown
import random
from string import ascii_uppercase
import pytest


RANGE = 5


@pytest.mark.parametrize("execution_number", range(RANGE))
@pytest.mark.parametrize("depth", range(RANGE))
@pytest.mark.parametrize("width", range(RANGE))
def test_randomised_idempotent(execution_number, depth, width):
    sl = [l for l in ascii_uppercase * 2 * RANGE * RANGE * RANGE * RANGE]
    random.shuffle(sl)

    def random_tree(depth, width):
        """More complex random tree. We need to make sure there are no duplicate files
or folders, and that they have content"""

        def purge_repeated_files(results):
            def rename_if_needed(fil, nrf):
                if fil.name in nrf:
                    doubled = fil.name + fil.name
                    fil._rename(doubled)
                    rename_if_needed(fil, nrf)

            non_repeated_filenames = []
            cleaned_results = []
            for fil in results:
                rename_if_needed(fil, non_repeated_filenames)
                non_repeated_filenames += [fil.name]
                cleaned_results += [fil]
            return cleaned_results

        if depth == 0:
            results = [
                File(sl.pop()).set_contents("contents=" + sl.pop())
                for _ in range(width)
            ]
            return purge_repeated_files(results)
        folder_indexes = random.sample(range(width), random.randint(0, width - 1) + 1)
        results = [
            File(sl.pop()).set_contents("contents=" + sl.pop()) for _ in range(width)
        ]
        cleaned_results = purge_repeated_files(results)
        for index in folder_indexes:
            cleaned_results[index] = Folder(
                sl.pop(), contents=random_tree(depth - 1, width)
            )
        cleaned_folders = purge_repeated_files(cleaned_results)
        return cleaned_folders

    randomised = Folder("", contents=random_tree(1 + depth, 1 + width))
    all_lines = [line for line in tree(randomised)]
    markdown = "\n".join(
        build_markdown(
            build_tree(randomised, ignore_globs=None, include_globs=None), max_length=15
        )
    )
    structure = _process_markdown(markdown, replacements=None)
    new_markdown = "\n".join(
        build_markdown(
            build_tree(structure, ignore_globs=None, include_globs=None), max_length=15
        )
    )

    assert structure == randomised
