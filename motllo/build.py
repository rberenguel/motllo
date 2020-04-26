from pathlib import Path
from typing import List, Optional

from motllo.ops import Folder, tree, tree_links
from motllo.traverser import Traverser


def gitignore(path: Path, for_path=True):
    """Parse a gitignore to keep pathlib happy"""
    if not path.exists():
        return []
    globs = []
    with path.open() as gitignore_file:
        lines = gitignore_file.read().split("\n")
    clean_globs = [l for l in lines if not l.startswith("#") and l != ""]
    globs = [f"{g}/*" if g.endswith("**") else g for g in clean_globs]
    if for_path:
        globs = [f"{path.parent}/{g}" for g in globs]
    return globs


def global_gitignore():
    """Parse global gitignore"""
    return gitignore(Path.home() / ".gitignore_global", for_path=False)


def project_gitignore(path: Path):
    """Parse all project gitignores (including in folders)"""
    ignores = []
    for item in path.iterdir():
        if item.name == ".gitignore":
            ignores += gitignore(item, for_path=True)
        if item.is_dir():
            ignores += project_gitignore(item)
    return ignores


def full_gitignore(path: Path):
    """Combined gitignores"""
    return project_gitignore(path) + global_gitignore()


SUFFIX_TO_LANG = {
    "py": "python",
    "sbt": "scala",
    "scala": "scala",
    "toml": "toml",
    "json": "json",
    "lock": "toml",
    "yaml": "yaml",
}

LANG_TO_ELLIPSIS = {
    "python": "# ...",
    "scala": "// ...",
    "toml": "[...]",
    "json": "...",
}


def language(suffix):
    """Get language for Markdown code block"""
    return SUFFIX_TO_LANG.get(suffix, "")


def ellipsis(suffix):
    """Comment-level ellipsis for the files"""
    return LANG_TO_ELLIPSIS.get(language(suffix), "...")


def build_file_markdown(current: Folder, base="", max_length=15):
    """Generate markdown out of the folder structure"""
    markdown: List[str] = []
    for item in current.iterdir():
        if item.is_dir():
            markdown += build_file_markdown(item, base=item.name, max_length=max_length)
        else:
            if base.startswith("/"):
                base = base[1:]
            if base == "":
                basename = f"{item.name}"
            else:
                basename = f"{base}/{item.name}"
            markdown += [""] + [f"# `{basename}`"]
            if item.contents is not None:
                markdown += [""] + [f"```{language(item.suffix)}"]
                if item.suffix != "md":
                    if len(item.contents) > max_length >= 0:
                        markdown += (
                            item.contents[0 : max_length - 1]
                            + [""]
                            + [ellipsis(item.suffix)]
                        )
                    else:
                        markdown += item.contents
                else:
                    markdown += [
                        "Content from Markdown files is ignored, since the output would break parsing"
                    ]
                markdown += ["```"]
    return markdown


def build_tree(path: Path, ignore_globs: Optional[List[str]]):
    """Build the tree from a path, given a glob"""
    structure = Traverser(ignore_globs=ignore_globs)(path)
    structure = structure.prune()
    return structure


def text_tree(path: Path, ignore_globs: Optional[List[str]]):
    """Generate the textual tree representation only"""
    structure = build_tree(path, ignore_globs)
    return "\n".join(list(tree(structure)))


def build_markdown(structure: Folder, max_length):
    """Generate markdown from a path, given ignore files"""
    built_tree = tree(structure)
    markdown = [""] + ["# Tree structure"]
    markdown += [""] + ["```"] + list(built_tree) + ["```"] + [""]
    markdown += list(tree_links(structure))
    markdown += [""] + build_file_markdown(structure, base="", max_length=max_length)
    return markdown


def write_markdown(markdown: List[str], path: Path):
    """Write final markdown to a path"""
    with path.open("w") as destination:
        for line in markdown:
            destination.write(line)
            destination.write("\n")
