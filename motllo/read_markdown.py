import logging
import sys
from pathlib import Path

from motllo.markdown_parser import (MARKDOWN_PARSER, BareCodeBlock, CodeBlock,
                                    HeadingBlock, ListBlock)
from motllo.ops import Folder
from motllo.tree_parser import TreeParser

logger = logging.getLogger("motllo.read_markdown")

TREE_KEY = "Markdown Tree Structure"


def structure_filler(folder, file_contents, file_replacements):
    """Populate a folder tree structure with file contents"""
    for item in folder.iterdir():
        if item.is_dir():
            structure_filler(item, file_contents, file_replacements)
        else:
            if item.as_posix().startswith("/."):
                cleaned = item.as_posix().replace("/./", "/")
            else:
                cleaned = item.as_posix()
            if cleaned not in file_contents.keys():
                raise Exception(f"Damn file not there {cleaned}")
            item.set_contents(file_contents[cleaned])
            if cleaned not in file_replacements.keys():
                logger.debug("No replacements found for marker %s", cleaned)
            else:
                item.set_replacements(file_replacements[cleaned])


def replace_replacements(file_replacement, replacements, to_be_replaced):
    replaced = to_be_replaced
    common_keys = [key for key in file_replacement.keys() if key in replacements.keys()]
    for key in common_keys:
        old_value = file_replacement[key]
        new_value = replacements[key]
        replaced = replaced.replace(old_value, new_value)
    return replaced


def parse_markdown_to_structure(markdown, replacements):
    """Convert a parsed Markdown document into a folder structure"""
    file_marker = None
    replacement_marker = None
    file_contents = {}
    file_replacements = {}
    required_keys = {}
    for item in markdown:
        if (
            isinstance(item, HeadingBlock)
            and item.text.strip().lower() == "tree structure"
        ):
            file_marker = TREE_KEY
        elif (
            isinstance(item, HeadingBlock)
            and item.text.strip().lower() != "replacements"
        ):
            filename = item.text.strip()
            file_marker = filename.replace("`", "")
        elif (
            isinstance(item, HeadingBlock)
            and item.text.strip().lower() == "replacements"
        ):
            replacement_marker = file_marker
        elif isinstance(item, ListBlock) and replacement_marker is not None:
            if ":" not in item.text:
                continue
            logger.info(
                "Found a replacement block %s for section `%s`",
                item.text,
                replacement_marker,
            )
            key, in_code = item.text.split(":")
            in_code = in_code.replace("`", "")
            key = key.replace("`", "")
            required_keys[key] = True
            replacer = {key: in_code.strip()}
            logger.debug("Replacer: %s", replacer)
            if replacement_marker not in file_replacements.keys():
                file_replacements[replacement_marker] = replacer
            else:
                file_replacements[replacement_marker].update(replacer)
        elif isinstance(item, (CodeBlock, BareCodeBlock)):
            contents = item.text.strip()
            if file_marker not in file_contents.keys():
                file_contents[file_marker] = contents
            else:
                file_contents[file_marker] += "\n\n" + contents
    for key in required_keys.keys():
        if key not in replacements.keys():
            logger.warning(
                "You have provided no replacement for `%s` in the CLI (use the -r flag)",
                key,
            )

    replaced_file_contents = {}
    for marker in file_contents.keys():
        logger.debug("File marker %s", marker)
        contents = file_contents[marker]
        if (
            replacements is not None
            and file_replacements.get(TREE_KEY, None) is not None
        ):
            new_file_marker = replace_replacements(
                file_replacements[TREE_KEY], replacements, marker
            )
            if new_file_marker != marker:
                logger.info(
                    "Replaced file reference `%s` with `%s`", marker, new_file_marker
                )
            replaced_file_contents[new_file_marker] = contents
        else:
            replaced_file_contents[marker] = contents

    if TREE_KEY not in replaced_file_contents.keys():
        logger.error(
            "Tree structure section not found in the Markdown document. This is required"
        )
        sys.exit(-1)
    tree_lines = [
        l for l in replaced_file_contents[TREE_KEY].split("\n") if l != ""
    ]  # This is pretty crappy
    replaced_tree = []
    if replacements is not None and file_replacements.get(TREE_KEY, None) is not None:
        for line in tree_lines:
            replaced_tree += [
                replace_replacements(file_replacements[TREE_KEY], replacements, line)
            ]
    else:
        replaced_tree = tree_lines
    try:
        structure = TreeParser(replaced_tree)()
    except IndexError as idx:
        logger.error("Failed processing the tree. Tree looks like:")
        for line in replaced_tree:
            logger.error(line)
        logger.warning(
            "Please make sure your tree has no additional spaces, spacing is important. Full exception follows"
        )
        logger.warning(idx, exc_info=True)
        sys.exit(-1)
    logger.debug(file_replacements)
    structure_filler(structure, replaced_file_contents, file_replacements)
    return structure


def process_markdown(path: Path, replacements):
    """Convert markdown into a structure"""
    with open(path) as markdown_path:
        all_lines = markdown_path.read()
    markdown, _ = MARKDOWN_PARSER.parse(all_lines)
    return parse_markdown_to_structure(markdown, replacements)


def materialise_structure(
    structure: Folder,
    path: Path,
    dry_run=True,
    replacements=None,
    ignore_existing_folders=False,
):
    """Materialise or dry run the folder structure"""
    logger.debug("Replacements: %s", replacements)
    location = path / Path(structure.as_posix())
    logger.info("🗃  %s", location)
    if not dry_run:
        try:
            location.mkdir()
        except FileExistsError:
            if ignore_existing_folders:
                logger.warning(
                    "Folder %s already exists and will not be recreated", location
                )
            else:
                logger.error(
                    "The destination folder %s already exists. Either delete it, use a new path or pass the --ignore-existing-folders flag",
                    location,
                )
                sys.exit(-1)

    for item in structure.iterdir():
        if item.is_dir():
            materialise_structure(item, path, dry_run, replacements)
        else:
            location = path / Path(item.as_posix())

            logger.info(
                "📁 %s (%s characters)", location, len("".join(item.contents)),
            )
            if replacements is not None and item.replacements is not None:
                new_contents = []
                for line in item.contents:
                    new_contents += [
                        replace_replacements(item.replacements, replacements, line)
                    ]
                item.set_contents("\n".join(new_contents))
                logger.info("Replacements applied to %s", item.name)
            if not dry_run:
                if location.exists():
                    logger.error(
                        "File %s already exists at that location. Delete it first",
                        location,
                    )
                    sys.exit(-1)
                with location.open("w") as destination:
                    for line in item.contents:
                        destination.write(line)
                        destination.write("\n")
