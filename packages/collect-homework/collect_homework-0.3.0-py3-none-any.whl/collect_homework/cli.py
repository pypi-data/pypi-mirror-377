#!/usr/bin/env python

"""
Description: a script to manage a collection of git repositories,
with one folder per student

\b
Config files:
00.ids: where to store the students ids (and optionally reponames)
00.reponame (optional): how the student repo is supposed to be named

\b
Workflow:
0. you start with creating a file `00.ids` containing the github slugs (ids) of the students
   all the ones that you are aware of at least
1. ask each student to create a github repo named like e.g. numerique-homework
   usually repo should be private (so students can't see each other's work),
   in this case, they invite you, the teacher, as a collaborator
2. beware to accept their invitation in a timely manner, as a github
   invitation expires after typically 7 days
3. create a fresh folder, named after the target reponame
   so typically you could put all this in a folder
   $HOME/git/ue12-p23-numerique/numerique-homework
   alternately, if this convention does not suit you, you can instead
   create a file named `00.reponame` containing the name of the repo
   (e.g. numerique-homework)
   this will be used to locate the student repos to be cloned
4. as you receive new invitations, add them to a file named 00.ids if missing
   see below for details on this file format
5. run this script to clone all the repos with
   collect-homework clone
   this can be done several times, the existing folders will be skipped
   so only the missing students are tried again
6. if a student has misspelled their repo name
   e.g. it is called homework-num instead of the expected numerique-homework
   then tweak 00.ids (see the format below)
7. iterate until you have all the slugs and all the repos cloned
8. from then on, use fetch / pull to update all the repos

in the meanwhile, you can use all the functions below

collect-homework --help

\b
collect-homework clone      will clone all repos
collect-homework summary    will output a summary of all repos (nb of commits, last commit date, ...)
collect-homework slugs      will output all slugs on stdout
collect-homework repos      will output all ids on stdout
collect-homework fetch      will fetch all repos
collect-homework pull       will pull all repos
collect-homework log1       will show the (full) last commit of each repo
collect-homework l1         will show the last commit of each repo (one line per commit)
collect-homework ln 4       same on the 4 last commits of each repo
collect-homework urls       will output the (git) urls of the repos
                            with the --http option, will output the http urls instead
collect-homework missing    will output the folders missing
                            i.e. students that have not yet created their repo

you can use the -s option to restrict to one or several students, like so

  collect-homework -s "bobarteam, john/ albert"

the -s option expects exactly one argument, it will then use
either space, comma or slash to cut the student names

Format for 00.ids:

\b
00.ids is supposed to contain, one per line, the github ids of the students
it can contain comments, starting with a #
for each student you can use any of the following formats
 - https://github.com/student/repo
 - student/repo
 - student

when the repo is not provided, it is assumed to be
  either the content of 00.reponame if that file exists
  otherwise the name of the current folder
"""

import sys
import os
from pathlib import Path
import re
import subprocess

import click

from collect_homework.parallel_shells import ParallelShells


CFG_REPONAME = "00.reponame"
CFG_SLUGS = "00.ids"


class Init:
    """
    reads current status
    """

    @staticmethod
    def get_reponame():
        cfg_reponame = Path(CFG_REPONAME)
        if not cfg_reponame.exists():
            return Path(".").absolute().parts[-1]
        with cfg_reponame.open() as f:
            return f.read().strip()

    @staticmethod
    def get_slugs(default_reponame):
        cfg_slugs = Path(CFG_SLUGS)
        result = {}
        with cfg_slugs.open() as f:
            for lineno, line in enumerate(f, 1):
                if line.startswith('#'):
                    continue
                line = line.strip()
                if not line:
                    continue
                if "/" in line:
                    try:
                        if line.endswith("/"):
                            line = line[:-1]
                        if line.endswith(".git"):
                            line = line[:-4]
                        line = line.replace("https://github.com/", "")
                        line = line.replace("git@github.com:", "")
                        slug, reponame = line.split("/")
                    except ValueError:
                        print(f"WARNING: ignoring line {lineno} with error", line)
                        continue
                else:
                    slug = line
                    reponame = default_reponame
                result[slug] = reponame
        return dict(sorted(result.items(), key=lambda x: x[0].lower()))

    @staticmethod
    def get_actual_repos():
        for dir in Path(".").glob("*/.git"):
            yield dir.parent.parts[-1]


# globals

def change_directory():
    """
    travel upwards until we find 00.ids
    otherwise stay in the current directory and issue a warning
    """
    global REPONAME, SLUGS, DIRS

    start = here = Path(".").absolute()
    while True:
        # found 00.ids
        if (here / CFG_SLUGS).exists():
            if start != here:
                print(f"WARNING: working from {here}")
                os.chdir(here)
            REPONAME = Init.get_reponame()
            SLUGS = Init.get_slugs(REPONAME)
            DIRS = list(Init.get_actual_repos())
            return
        # not find at all
        if here.parent == here:
            print(f"warning, config file {CFG_SLUGS} not found")
            REPONAME = "unknown"
            SLUGS = {}
            DIRS = []
            return
        # otherwise go one level up and try again
        here = here.parent

change_directory()


def _git_proxy(message, *git_command):
    """
    Run a git command on all DIRS
    """
    for slug in Init.get_actual_repos():
        if slug not in SLUGS:
            continue
        if message:
            print(f"===== {message} in {slug}")
        command = ["git", "-C", slug, *git_command]
        # print(command)
        subprocess.run(command)

# message not used yet
def _git_proxy_parallel(_message, *git_command):
    """
    Run a git command on all DIRS, but asynchronously
    """
    commands = []
    for slug in Init.get_actual_repos():
        if slug not in SLUGS:
            continue
        command = f"git -C {slug} {' '.join(git_command)}"
        commands.append(command)
    ParallelShells(commands).run()

# the click CLI object
@click.group(chain=True, help=sys.modules[__name__].__doc__)
@click.option('-s', '--students', help="comma-separated")
def cli(students):
    if students is None:
        return
    global SLUGS
    focus_slugs = {}
    students = re.split(r'[,\s]+', students)
    for student in students:
        if not student:
            continue
        if student not in SLUGS and Path(student).exists():
                student = Path(student).absolute().parts[-1]
                print(f"-> using slug {student}")
        if student not in SLUGS:
            print(f"unknown student {student} in {CFG_SLUGS}")
            exit(1)
        focus_slugs[student] = SLUGS[student]
    SLUGS = focus_slugs


# commands
@cli.command('slugs', help="show the slugs, optionally with reponames")
@click.option('-v', '--verbose', is_flag=True, default=False, help="show reponames", )
def slugs(verbose):
    for slug, reponame in SLUGS.items():
        print(f"{slug}/{reponame}" if verbose else slug)

@cli.command('dirs', help="show the repos currently present")
def dirs():
    for dir in sorted(DIRS, key=lambda x: x.lower()):
        print(dir)

@cli.command('missing', help="show the missing directories")
def missing():
    for slug, reponame in SLUGS.items():
        if slug not in DIRS:
            print(slug)

@cli.command('empty', help="show the empty directories")
def empty():
    for slug in DIRS:
        retcod = subprocess.run(f"git -C {slug} log --oneline >& /dev/null",
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                shell=True).returncode
        if retcod != 0:
            print(slug)

@cli.command('clone', help="clone all missing repos")
def clone():
    commands = []
    for slug, reponame in SLUGS.items():
        gitrepo = Path(slug) / ".git"
        if gitrepo.exists() and gitrepo.is_dir():
            print(f"{slug} -- already OK")
            continue
        commands.append(f"git clone git@github.com:{slug}/{reponame}.git {slug}")
    ParallelShells(commands).run()


@cli.command('urls', help="show the urls of the repos")
@click.option('-h', '--http', is_flag=True, default=False, help="show http urls")
def urls(http):
    if not http:
        _git_proxy("", "remote", "get-url", "origin")
    else:
        for slug, reponame in SLUGS.items():
            print(f"https://github.com/{slug}/{reponame}")

@cli.command('status', help="do a full git status on the repos")
def status(): _git_proxy("STATUS", "status")

@cli.command('s', help="do a short git status on the repos (short format, no untracked files)")
def s(): _git_proxy("SHORT STATUS", "status", "--short", "--untracked-files=no")

# so we can pass any extra args to git diff
@cli.command(
    'diff',
    context_settings=dict(ignore_unknown_options=True),
    help="do a git diff on the repos - all extra args are passed to git diff",
)
@click.argument('extra_args', type=click.UNPROCESSED, nargs=-1)
def diff(extra_args): _git_proxy("DIFF", "diff", *extra_args)

@cli.command('pull', help="do a git pull on the repos")
def pull(): _git_proxy_parallel("PULL", "pull")

@cli.command('fetch', help="do a git fetch on the repos")
def fetch(): _git_proxy_parallel("FETCH", "fetch")

@cli.command('reset', help="do a git reset --hard on the repos")
def reset(): _git_proxy("RESET", "reset", "--hard")

@cli.command('merge', help="do a git merge origin/main on the repos")
def merge(): _git_proxy("MERGE", "merge", "origin/main")


FORMAT = """--format=format:'%C(bold blue)%h%C(reset) - %C(bold green)(%ar)%C(reset) %C(dim bold red)%an%C(reset) - %s%C(red)%d%C(reset)'"""

@cli.command('log1', help="show the last commit of each repo - default format")
def log1(): _git_proxy("last commit", "log", "-1")

@cli.command('l1', help="show the last commit of each repo, one-liner")
def l1(): _git_proxy("", "log", "-1", FORMAT )

@cli.command('l5', help="show the 5 latest commits of each repo, one-liner")
def l5(): _git_proxy( "LISTING 5 latest commits", "log", "--oneline", "--all", "--graph", "-5", FORMAT )

@cli.command('ln', help="show the n latest commits of each repo, one-liner")
@click.argument('n', type=int)
def ln(n): _git_proxy( f"LISTING {n} latest commits", "log", "--oneline", "--all", "--graph", f"-{n}", FORMAT )


@cli.command('ls', context_settings=dict(ignore_unknown_options=True), help="runs git ls-files in the repos")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def ls(args):
    args_str = ' '.join(args)
    _git_proxy(f"git ls-files {args_str}", "ls-files", *args)

@cli.command('raw', context_settings=dict(ignore_unknown_options=True), help="runs git what-you-want in the repos")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def raw(args):
    if len(args) == 0:
        print("error: expecting at least one argument, the git subcommand")
        exit(1)
    args_str = ' '.join(args)
    _git_proxy(f"git {args_str}", *args)


# pour a bit of shell in the mix
summary_function = """
function summary() {
    local quiet="$1"; shift
    local verbose="$1"; shift
    local slug="$1"; shift
    # missing repo
    [[ -d $slug ]] || {
        if [[ "$quiet" == False ]]; then printf '%24s' $slug; echo '   --- MISSING ---'; fi
        return
    }
    # empty repo
    git -C $slug log >& /dev/null || {
        if [[ "$quiet" == False ]]; then printf '%24s' $slug; echo '   --- EMPTY ---'; fi
        return
    }
    printf '%24s ' $slug
    local nb_folders=$(find $slug -type d -depth +0 | grep -vE '/.git($|/)' | wc -l)
    local nb_files=$(find $slug -type f | fgrep -v '/.git/' | wc -l)
    local nb_git_files=$(git -C $slug ls-files | wc -l)
    local nb_commits=$(git -C $slug log --oneline | wc -l)
    local dateh=$(git -C $slug log -1 --format='%ah')
    local date=$(git -C $slug log -1 --format='%ar')
    printf "%3d folders - " $nb_folders
    printf "%3d files - " $nb_files
    printf "%3d git files - " $nb_git_files
    printf "%3d commits - " $nb_commits
    if [[ "$verbose" == True ]]; then
        printf "last on %s (%s)" "$dateh" "$date"
    else
        printf "last %s" "$date"
    fi
    echo
}
"""

@cli.command('summary', help="show a summary of the repos")
@click.option('-q', '--quiet', is_flag=True, default=False, help="silent missing repos")
@click.option('-v', '--verbose', is_flag=True, default=False, help="verbose mode")
def summary(quiet, verbose):
    commands = []
    for slug, _ in SLUGS.items():
        commands.append(summary_function + f"summary {quiet} {verbose} {slug}")
    ParallelShells(commands, echo=False).run()
