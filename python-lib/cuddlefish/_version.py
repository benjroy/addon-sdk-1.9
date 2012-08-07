
# This file helps to compute a version number in source trees obtained from
# git-archive tarball (such as those provided by githubs download-from-tag
# feature). Distribution tarballs (build by setup.py sdist) and build
# directories (produced by setup.py build) will contain a much shorter file
# that just contains the computed version number.

# This file is released into the public domain. Generated by versioneer-0.6
# (https://github.com/warner/python-versioneer)

# these strings will be replaced by git during git-archive
git_refnames = " (HEAD, 1.9rc1, 1.9, origin/stabilization, stabilization)"
git_full = "4dfc2b654725e382eaa7b8a53b6910d2bb05f52f"


import subprocess

def run_command(args, cwd=None, verbose=False):
    try:
        # remember shell=False, so use git.cmd on windows, not just git
        p = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=cwd)
    except EnvironmentError, e:
        if verbose:
            print "unable to run %s" % args[0]
            print e
        return None
    stdout = p.communicate()[0].strip()
    if p.returncode != 0:
        if verbose:
            print "unable to run %s (error)" % args[0]
        return None
    return stdout


import sys
import re
import os.path

def get_expanded_variables(versionfile_source):
    # the code embedded in _version.py can just fetch the value of these
    # variables. When used from setup.py, we don't want to import
    # _version.py, so we do it with a regexp instead. This function is not
    # used from _version.py.
    variables = {}
    try:
        for line in open(versionfile_source,"r").readlines():
            if line.strip().startswith("git_refnames ="):
                mo = re.search(r'=\s*"(.*)"', line)
                if mo:
                    variables["refnames"] = mo.group(1)
            if line.strip().startswith("git_full ="):
                mo = re.search(r'=\s*"(.*)"', line)
                if mo:
                    variables["full"] = mo.group(1)
    except EnvironmentError:
        pass
    return variables

def versions_from_expanded_variables(variables, tag_prefix):
    refnames = variables["refnames"].strip()
    if refnames.startswith("$Format"):
        return {} # unexpanded, so not in an unpacked git-archive tarball
    refs = set([r.strip() for r in refnames.strip("()").split(",")])
    for ref in list(refs):
        if not re.search(r'\d', ref):
            refs.discard(ref)
            # Assume all version tags have a digit. git's %d expansion
            # behaves like git log --decorate=short and strips out the
            # refs/heads/ and refs/tags/ prefixes that would let us
            # distinguish between branches and tags. By ignoring refnames
            # without digits, we filter out many common branch names like
            # "release" and "stabilization", as well as "HEAD" and "master".
    for ref in sorted(refs):
        # sorting will prefer e.g. "2.0" over "2.0rc1"
        if ref.startswith(tag_prefix):
            r = ref[len(tag_prefix):]
            return { "version": r,
                     "full": variables["full"].strip() }
    # no suitable tags, so we use the full revision id
    return { "version": variables["full"].strip(),
             "full": variables["full"].strip() }

def versions_from_vcs(tag_prefix, versionfile_source, verbose=False):
    # this runs 'git' from the root of the source tree. That either means
    # someone ran a setup.py command (and this code is in versioneer.py, thus
    # the containing directory is the root of the source tree), or someone
    # ran a project-specific entry point (and this code is in _version.py,
    # thus the containing directory is somewhere deeper in the source tree).
    # This only gets called if the git-archive 'subst' variables were *not*
    # expanded, and _version.py hasn't already been rewritten with a short
    # version string, meaning we're inside a checked out source tree.

    try:
        here = os.path.abspath(__file__)
    except NameError:
        # some py2exe/bbfreeze/non-CPython implementations don't do __file__
        return {} # not always correct

    # versionfile_source is the relative path from the top of the source tree
    # (where the .git directory might live) to this file. Invert this to find
    # the root from __file__.
    root = here
    for i in range(len(versionfile_source.split("/"))):
        root = os.path.dirname(root)
    if not os.path.exists(os.path.join(root, ".git")):
        return {}

    GIT = "git"
    if sys.platform == "win32":
        GIT = "git.cmd"
    stdout = run_command([GIT, "describe", "--tags", "--dirty", "--always"],
                         cwd=root)
    if stdout is None:
        return {}
    if not stdout.startswith(tag_prefix):
        if verbose:
            print "tag '%s' doesn't start with prefix '%s'" % (stdout, tag_prefix)
        return {}
    tag = stdout[len(tag_prefix):]
    stdout = run_command([GIT, "rev-parse", "HEAD"], cwd=root)
    if stdout is None:
        return {}
    full = stdout.strip()
    if tag.endswith("-dirty"):
        full += "-dirty"
    return {"version": tag, "full": full}


def versions_from_parentdir(parentdir_prefix, versionfile_source, verbose=False):
    try:
        here = os.path.abspath(__file__)
        # versionfile_source is the relative path from the top of the source
        # tree (where the .git directory might live) to _version.py, when
        # this is used by the runtime. Invert this to find the root from
        # __file__.
        root = here
        for i in range(len(versionfile_source.split("/"))):
            root = os.path.dirname(root)
    except NameError:
        # try a couple different things to handle py2exe, bbfreeze, and
        # non-CPython implementations which don't do __file__. This code
        # either lives in versioneer.py (used by setup.py) or _version.py
        # (used by the runtime). In the versioneer.py case, sys.argv[0] will
        # be setup.py, in the root of the source tree. In the _version.py
        # case, we have no idea what sys.argv[0] is (some
        # application-specific runner).
        root = os.path.dirname(os.path.abspath(sys.argv[0]))
    # Source tarballs conventionally unpack into a directory that includes
    # both the project name and a version string.
    dirname = os.path.basename(root)
    if not dirname.startswith(parentdir_prefix):
        if verbose:
            print "dirname '%s' doesn't start with prefix '%s'" %                   (dirname, parentdir_prefix)
        return None
    return {"version": dirname[len(parentdir_prefix):], "full": ""}

tag_prefix = ""
parentdir_prefix = "addon-sdk-"
versionfile_source = "python-lib/cuddlefish/_version.py"

def get_versions():
    variables = { "refnames": git_refnames, "full": git_full }
    ver = versions_from_expanded_variables(variables, tag_prefix)
    if not ver:
        ver = versions_from_vcs(tag_prefix, versionfile_source)
    if not ver:
        ver = versions_from_parentdir(parentdir_prefix, versionfile_source)
    if not ver:
        ver = {"version": "unknown", "full": ""}
    return ver

