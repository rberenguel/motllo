import logging
from pathlib import Path

import click
from colorlog import ColoredFormatter  # type: ignore

from motllo.build import (build_markdown, build_tree, full_gitignore,
                          text_tree, write_markdown)
from motllo.read_markdown import materialise_structure, process_markdown

logger = logging.getLogger("motllo")


def configure_logger():
    """Fancy logging is nicer"""
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)s - %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "yellow",
            "INFO": "cyan",
            "WARNING": "purple",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@click.group()
@click.option("--debug", help="Set log level to debug", is_flag=True)
def cli(debug):
    """Motllo generates Markdown files that can be used as repository/folder templates and can also convert them into a full folder/repository structure. Use the `markdown` command to convert any path into a Markdown file, that is then almost completely editable (and human readable!). You can then run the `build` command using that file to recreate the repository anywhere.

    The goal is to have templates that are small, self-contained and literate. In each section of the Markdown document you can intersperse prose with code, and all code blocks will be weaved together, try it out!

    With motllo you can create templates that can be stored together, easy to read and modify on a whim.
    """
    configure_logger()
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


@click.argument("path")
@click.option(
    "--gitignore/--no-gitignore",
    default=True,
    help="Use local and global gitignores, yes by default",
)
@click.option(
    "--ignore",
    help='Glob patterns to ignore, comma separated between quotes like "*.py,*.c,*.scala"',
)
@click.option("-o", "--output", help="Destination markdown file", required=True)
@click.option(
    "-x",
    "--max-length",
    help="Maximum amount of lines to write in the markdown, for each file. Use -1 for `all of them`. Defaults to 15",
    type=int,
    default=15,
)
@cli.command()
def markdown(path, gitignore, ignore, output, max_length):
    """Generate a Markdown template from a folder or repository at PATH"""
    ppath = Path(path)
    opath = Path(output)
    if ignore is not None:
        ignore_globs = ignore.split(",")
    else:
        ignore_globs = []
    if gitignore:
        gitignore_globs = full_gitignore(ppath) + ["output"]
    else:
        gitignore_globs = []
    all_ignore_globs = gitignore_globs + ignore_globs
    if len(all_ignore_globs) == 0:
        all_ignore_globs = None
    try:
        structure = build_tree(Path.cwd() / ppath, ignore_globs=all_ignore_globs)
    except Exception as exc:
        logger.error("Uncaught exception building the tree: %s", exc)
    try:
        generated_markdown = build_markdown(structure, max_length)
    except Exception as exc:
        logger.error("Uncaught exception generating the Markdown: %s", exc)
    try:
        write_markdown(generated_markdown, opath)
    except Exception as exc:
        logger.error("Problem writing Markdown file: %s", exc)


@click.argument("path")
@click.option(
    "--dry-run/--commit",
    default=True,
    help="Dry run by default so you can see what it does",
)
@click.option(
    "--ignore-existing-folders",
    is_flag=True,
    default=False,
    help="Ignore if the destination folder already exists",
)
@click.option(
    "-r",
    "--replace",
    help='Multiple replacement rules separated by colons, like -r "$PROJ:world_domination", -r"$TOOLS:python"',
    multiple=True,
)
@click.option(
    "-o", "--output", help="Destination path to create everything", required=True
)
@cli.command()
def build(path, dry_run, output, replace, ignore_existing_folders):
    """Build a file/folder structure based on a Markdown document at PATH"""
    ppath = Path(path)
    opath = Path(output)
    if dry_run:
        logger.info("Dry run materialising %s to %s", ppath, opath)
        logger.info(
            "The following files and folders will be created, according to the replacements you may have specified"
        )
    replacements = {}
    for rule in replace:
        key, value = rule.split(":")
        replacements.update({key: value})
    try:
        structure = process_markdown(ppath, replacements=replacements)
    except Exception as exc:
        logger.exception("Uncaught exception processing Markdown at path: %s", exc)
    try:
        materialise_structure(
            structure,
            opath,
            dry_run=dry_run,
            replacements=replacements,
            ignore_existing_folders=ignore_existing_folders,
        )
    except Exception as exc:
        logger.exception("Uncaught exception materialising Markdown at path: %s", exc)


@click.argument("path")
@click.option(
    "--gitignore/--no-gitignore",
    default=True,
    help="Use local and global gitignores, yes by default",
)
@cli.command()
def tree(path, gitignore):
    """Generate only the visual folder tree (like the UNIX tree command)"""
    ppath = Path(path)
    if gitignore:
        ignore_globs = full_gitignore(ppath)
    else:
        ignore_globs = None
    try:
        only_tree = text_tree(Path.cwd() / ppath, ignore_globs=ignore_globs)
    except Exception as exc:
        logger.exception("Uncaught exception generating the tree: %s", exc)
    click.echo(only_tree)


if __name__ == "__main__":
    cli()
