# Motllo

[![PyPI version](https://badge.fury.io/py/motllo.svg)](https://badge.fury.io/py/motllo)

Repository templates just like I like them

- [Motivation](#motivation)
- [Description](#description)
- [Example](#example)
- [Usage](#usage)
- [Is it safe to use?](#is-it-safe-to-use)
- [Next steps](#next-steps)

## Motivation


It can be due to a bit of OCD and a bit of Knuth. 

- Most "project template" systems (that let you create a repository with
  everything set up to use a library) need a specific repository for it
  ([cookiecutter](https://cookiecutter.readthedocs.io/en/1.7.2/),
  [giter8](http://www.foundweekends.org/giter8/), [GitHub's own template
  repositories](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/creating-a-template-repository)).
  This feels weird to me, like needing a house to build a new house.
- I prefer more compact stuff I can read. Even better if I can document

So, here's `motllo`

```
[1284; del ll. mŏdŭlus 'mesura; mòdul', dimin. de modus 'mesura']
 	
m 1 1 TECNOL METAL·L ART Peça amb una cavitat en la qual hom introdueix 
una substància en forma de pols, de pasta o líquida per tal que, en 
passar a l'estat sòlid, agafi la forma de la cavitat. 
```

## Description

Motllo can convert a folder structure/repository (it more or less handles
`.gitignore` rules) into a Markdown document with:

- A "Tree structure" section
- Optionally, replacements to apply to the structure via the command line tool
- A tree representation of the folder structure you want (similar to the one
  generated by the `tree` UNIX utility, but in Python, thanks to a
  [Stackoverflow answer](https://stackoverflow.com/a/59109706) by [Aaron
  Hall](https://twitter.com/aaronchall)) inside of a code block
- Optionally, section links
- Sections, titled with the filepath described in the tree
- Optionally, replacement blocks for this filepath
- Code blocks (with possibly text describing what they are there for). All code
  blocks within a section are merged into that file

## Example

You can see an example of a basic Python CLI tool (like this one) as a template,
with replacements and comments [here](examples/python_cli.md).

I plan on adding more examples at some point. New examples welcome!

## Usage

The most easy uses are

```
motllo markdown . -o some_markdown.md
```

to generate the Markdown template from a repository, which will respect nested
and global `.gitignore ` and then

```
motllo build markdown_template.md -o /wherever/ -r "project:cool-new-project" -r "version:0.0.1"
```

Here are the commands as shown in the CLI

```
Usage: motllo [OPTIONS] COMMAND [ARGS]...

Options:
  --debug  Set log level to debug
  --help   Show this message and exit.

Commands:
  build     Build a file/folder structure based on a Markdown document at...
  markdown  Generate a Markdown template from a folder or repository at PATH
  tree      Generate only the visual folder tree (like the UNIX tree...
```
---
```
Usage: motllo markdown [OPTIONS] PATH

  Generate a Markdown template from a folder or repository at PATH

Options:
  -x, --max-length INTEGER      Maximum amount of lines to write in the
                                markdown, for each file. Use -1 for `all of
                                them`

  -o, --output TEXT             Destination markdown file  [required]
  --ignore TEXT                 Glob patterns to ignore, comma separated
                                between quotes like "*.py,*.c,*.scala"

  --gitignore / --no-gitignore  Use local and global gitignores, yes by
                                default

  --help                        Show this message and exit.
```
---
```
Usage: motllo build [OPTIONS] PATH

  Build a file/folder structure based on a Markdown document at PATH

Options:
  -o, --output TEXT     Destination path to create everything  [required]
  -r, --replace TEXT    Multiple replacement rules separated by colons, like
                        -r "$PROJ:world_domination", -r"$TOOLS:python"

  --dry-run / --commit  Dry run by default so you can see what it does
  --help                Show this message and exit.
```
---
```
Usage: motllo tree [OPTIONS] PATH

  Generate only the visual folder tree (like the UNIX tree command)

Options:
  --gitignore / --no-gitignore  Use local and global gitignores, yes by
                                default

  --help                        Show this message and exit.
```

## Is it safe to use?

Well, in dry run mode it will tell you what it will write, so pretty much yes.
Don't blame me if it fails. Of course, I'd be happy to see it fail in the wild
and improve it.

## Next steps

I want to refactor big chunks of the internals (I don't like parts of the API),
and add some more testing. I was a bit liberal with the final stages: I tested
the tree-to-folder pretty extensively, but I didn't really test
`tree-to-markdown` or` markdown-to-tree` as thoroughly as I would like. The
latter should be pretty easy.

I will probably spin out the markdown parser (which was stolen from the one I
wrote for [bear-note-graph](https://github.com/rberenguel/bear-note-graph)) into
its own library