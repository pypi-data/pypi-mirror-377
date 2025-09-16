# Changelog

## 0.3.0 - 2025-09-16

- add `ls` subcommand to wrap git ls-files files in the repositories
- add `raw` subcommand to wrap any git command in the repositories

## 0.2.4 - 2025-09-11

- move up the tree until it finds a 00.ids file
- slightly different way to handle students option if not exactly one from 00.ids
- verbose option to summary

## 0.2.3 - 2025-03-28

- add `empty` command to list empty repositories
- add `--http` option to  the `urls` command; useful to batch-open repositories in a browser

## 0.2.2 - 2024-11-04

- bugfix - clone was looking for a git folder, instead of a .git folder
- redo botched release (0.2.1 never made it to pypi)

## 0.2.0 - 2024-10-29

- support for ssh urls

## 0.1.4 - 2024-10-14

- extra arguments to the diff command are passed to git diff as-is

## 0.1.3 - 2024-10-14

- add a help message to all commands
- new summary --quiet option

## 0.1.2 - 2024-10-13

- first public release
