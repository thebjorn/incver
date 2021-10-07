# -*- coding: utf-8 -*-
"""
Update a package's version number.
"""
from __future__ import print_function
import io
import warnings
from dkcode.configs.dkbuildyml import raw_read_dkbuild_yml

from dkrepo.gitrepo import GitRepository
from invoke import task
from dkpkg import Package


def files_with_version_numbers(pkg=None):
    pkg = pkg or Package()
    root = pkg.root
    default = {
        root / 'setup.py',
        root / 'package.json',
        root / 'package.ini',
        root / 'package.yaml',
        root / 'dkbuild.yml',
        root / 'docs' / 'conf.py',
        root / 'src' / 'version.js',
        root / 'js' / 'version.js',
        root / 'styles' / 'index.less',
        root / 'styles' / 'index.scss',
        root / 'less' / 'index.less',
        pkg.source / '__init__.py',
        pkg.source / '_version.py',
        pkg.source / 'package.json',
    }
    return default


def _replace_version(fname, cur_version, new_version):
    """Replace the version string ``cur_version`` with the version string
       ``new_version`` in ``fname``.
    """
    if not fname.exists():
        return False

    with io.open(fname, encoding='u8') as fp:
        txt = fp.read()

    if cur_version not in txt:  # pragma: nocover
        # warnings.warn("Did not find %r in %r" % (cur_version, fname))
        return False

    if new_version in txt:
        warnings.warn("new version string %s already in file %s" % (
            new_version, fname
        ))

    occurences = txt.count(cur_version)
    if occurences > 2:  # pragma: nocover
        warnings.warn(
            "Found version string (%r) multiple times in %r, skipping" % (
                cur_version, fname
            )
        )
    if fname.endswith('package.json'):
        txt = txt[:200].replace(cur_version, new_version, 1) + txt[200:]
    else:
        txt = txt.replace(cur_version, new_version)

    with io.open(fname, 'w', encoding='u8') as fp:
        fp.write(txt)
    return 1


def _getversion(c):
    return c.run('python setup.py --version', hide=True).stdout.strip()


@task()
def version(c):
    """Return the current version of the package.
    """
    pkg = Package()
    with pkg.root.cd():
        version = _getversion(c)
        print(version)
        return version


@task(
    autoprint=True,
    help=dict(
        major="update major version number (set minor and patch to 0)",
        minor="update minor version number (set patch to 0)",
        patch="(default) update patch version",
        tag="create a tag (git only)"
    )
)
def upversion(c, major=False, minor=False, patch=False, tag=False):
    """Update package version (default patch-level increase).
    """
    # while it may be tempting to make this task auto-tag the new version,
    # this is generally a bad idea (bumpversion did this, and it was a mess)
    pkg = Package()
    if not (major or minor or patch):
        patch = True  # pragma: nocover
    txt_version = _getversion(c)
    cur_version = [int(n, 10) for n in txt_version.split('.')]
    if major:
        cur_version[0] += 1
        cur_version[1] = 0
        cur_version[2] = 0
    elif minor:
        cur_version[1] += 1
        cur_version[2] = 0
    elif patch:
        cur_version[2] += 1
    new_version = '.'.join([str(n) for n in cur_version])

    changed = 0
    changed_files = []
    addlfiles = set()
    dkbuild = raw_read_dkbuild_yml()
    if 'versioned' in dkbuild['package']:
        addlfiles = {pkg.root / fname for fname in dkbuild['package']['versioned']}
    for fname in addlfiles | files_with_version_numbers():
        was_changed = _replace_version(fname, txt_version, new_version)
        changed += was_changed
        if was_changed:
            changed_files.append(fname)
    if changed == 0:
        warnings.warn("I didn't change any files...!")  # pragma: nocover
    else:
        print("changed version to %s in %d files" % (new_version, changed))
        for fname in changed_files:
            print('  ', fname)

    if tag and changed and GitRepository.is_vcs(pkg.root):
        with pkg.root.abspath().cd():
            c.run('git add ' + " ".join(f.relpath(pkg.root) for f in changed_files))
            c.run('git commit -m "upversion"')
            # c.run('git commit -am "upversion"')
            c.run('git tag -a v{version} -m "Version {version}"'.format(
                version=new_version
            ))
            c.run('git push')
            c.run('git push origin v{version}'.format(version=new_version))

    return new_version
