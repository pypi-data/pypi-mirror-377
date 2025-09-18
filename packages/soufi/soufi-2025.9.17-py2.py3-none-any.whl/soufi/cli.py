# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.

"""A simple testing CLI to find and download source."""

import functools
import os
import shutil
import sys
import warnings

from soufi import exceptions, finder

try:
    import click
    import pylru
except ImportError:
    sys.exit("CLI support not installed; please install soufi[cli]")

warnings.formatwarning = lambda msg, *x, **y: f"WARNING: {msg}\n"

# Configure a small-ish in-memory LRU cache to speed up operations
LRU_CACHE = pylru.lrucache(size=512)


class Finder:
    @classmethod
    def find(cls, finder):
        source = finder.find()
        click.echo(source)
        return source

    @classmethod
    def ubuntu(cls, name, version, timeout=None):
        click.echo("Logging in to Launchpad")
        ubuntu_finder = finder.factory(
            "ubuntu",
            name,
            version,
            finder.SourceType.os,
            cache_backend="dogpile.cache.memory",
            cache_args=dict(cache_dict=LRU_CACHE),
            timeout=timeout,
        )
        click.echo("Finding source in Launchpad")
        return cls.find(ubuntu_finder)

    @classmethod
    def debian(cls, name, version, timeout=None):
        debian_finder = finder.factory(
            "debian", name, version, finder.SourceType.os
        )
        return cls.find(debian_finder)

    @classmethod
    def npm(cls, name, version, timeout=None):
        npm_finder = finder.factory(
            "npm", name, version, finder.SourceType.npm, timeout=timeout
        )
        return cls.find(npm_finder)

    @classmethod
    def python(cls, name, version, pyindex=None, timeout=None):
        python_finder = finder.factory(
            "python",
            name=name,
            version=version,
            s_type=finder.SourceType.python,
            pyindex=pyindex,
            timeout=timeout,
        )
        return cls.find(python_finder)

    @classmethod
    def centos(
        cls,
        name,
        version,
        repos=None,
        source_repos=None,
        binary_repos=None,
        timeout=None,
    ):
        optimal = "optimal" in repos
        centos_finder = finder.factory(
            "centos",
            name=name,
            version=version,
            s_type=finder.SourceType.os,
            repos=repos,
            optimal_repos=optimal,
            source_repos=source_repos,
            binary_repos=binary_repos,
            cache_backend="dogpile.cache.memory",
            cache_args=dict(cache_dict=LRU_CACHE),
            timeout=timeout,
        )
        return cls.find(centos_finder)

    @classmethod
    def almalinux(
        cls,
        name,
        version,
        repos=None,
        source_repos=None,
        binary_repos=None,
        timeout=None,
    ):
        alma_finder = finder.factory(
            "almalinux",
            name=name,
            version=version,
            s_type=finder.SourceType.os,
            source_repos=source_repos,
            binary_repos=binary_repos,
            cache_backend="dogpile.cache.memory",
            cache_args=dict(cache_dict=LRU_CACHE),
            timeout=timeout,
        )
        return cls.find(alma_finder)

    @classmethod
    def alpine(cls, name, version, aports_dir, timeout=None):
        alpine_finder = finder.factory(
            "alpine",
            name=name,
            version=version,
            s_type=finder.SourceType.os,
            aports_dir=aports_dir,
            cache_backend="dogpile.cache.memory",
            cache_args=dict(cache_dict=LRU_CACHE),
            timeout=timeout,
        )
        return cls.find(alpine_finder)

    @classmethod
    def go(cls, name, version, goproxy, timeout=None):
        go_finder = finder.factory(
            "go",
            name=name,
            version=version,
            s_type=finder.SourceType.go,
            goproxy=goproxy,
            timeout=timeout,
        )
        return cls.find(go_finder)

    @classmethod
    def java(cls, name, version, timeout=None):
        java_finder = finder.factory(
            "java",
            name=name,
            version=version,
            s_type=finder.SourceType.java,
            timeout=timeout,
        )
        return cls.find(java_finder)

    @classmethod
    def gem(cls, name, version, timeout=None):
        gem_finder = finder.factory(
            "gem",
            name=name,
            version=version,
            s_type=finder.SourceType.gem,
            timeout=timeout,
        )
        return cls.find(gem_finder)

    @classmethod
    def photon(
        cls, name, version, source_repos=None, binary_repos=None, timeout=None
    ):
        photon_finder = finder.factory(
            "photon",
            name=name,
            version=version,
            s_type=finder.SourceType.os,
            source_repos=source_repos,
            binary_repos=binary_repos,
            cache_backend="dogpile.cache.memory",
            cache_args=dict(cache_dict=LRU_CACHE),
            timeout=timeout,
        )
        return cls.find(photon_finder)

    @classmethod
    def rhel(
        cls, name, version, source_repos=None, binary_repos=None, timeout=None
    ):
        rhel_finder = finder.factory(
            "rhel",
            name=name,
            version=version,
            s_type=finder.SourceType.os,
            source_repos=source_repos,
            binary_repos=binary_repos,
            cache_backend="dogpile.cache.memory",
            cache_args=dict(cache_dict=LRU_CACHE),
            timeout=timeout,
        )
        return cls.find(rhel_finder)

    @classmethod
    def crate(cls, name, version, timeout=None):
        crate_finder = finder.factory(
            "crate",
            name=name,
            version=version,
            s_type=finder.SourceType.crate,
            timeout=timeout,
        )
        return cls.find(crate_finder)

    @classmethod
    def phppecl(cls, name, version, timeout=None):
        pecl_finder = finder.factory(
            "phppecl",
            name=name,
            version=version,
            s_type=finder.SourceType.phppecl,
            timeout=timeout,
        )
        return cls.find(pecl_finder)

    @classmethod
    def phpcomposer(cls, name, version, timeout=None):
        composer_finder = finder.factory(
            "phpcomposer",
            name=name,
            version=version,
            s_type=finder.SourceType.phpcomposer,
            timeout=timeout,
        )
        return cls.find(composer_finder)


def make_archive_from_discovery_source(disc_src, fname):
    try:
        with disc_src.make_archive() as in_fd, open(fname, "wb") as out_fd:
            # copyfileobj copies in chunks, so as not to exhaust memory.
            shutil.copyfileobj(in_fd, out_fd)
    except exceptions.DownloadError as e:
        click.echo(str(e))
        click.get_current_context().exit(255)


@click.command()
@click.argument("distro")
@click.argument("name")
@click.argument("version")
@click.option(
    "--pyindex",
    default="https://pypi.org/pypi/",
    help="Python package index if getting Python",
    show_default=True,
)
@click.option(
    "--aports",
    default=None,
    help="Path to a checked-out aports directory if getting Alpine",
    show_default=True,
)
@click.option(
    "--repo",
    default=(),
    multiple=True,
    help="For CentOS/Almalinux, name of repo to use instead of defaults. "
    "Use 'optimal' to use an extended optimal set. May be repeated.",
)
@click.option(
    "--source-repo",
    default=(),
    multiple=True,
    help="For Yum-based distros, URL of a source repo mirror to use "
    "for lookups instead of the distro defaults. May be repeated. "
    "On CentOS, this causes --repo to be ignored.",
)
@click.option(
    "--binary-repo",
    default=(),
    multiple=True,
    help="For Yum-based distros, URL of a binary repo mirror to use "
    "for lookups instead of the distro defaults. May be repeated. "
    "On CentOS, this causes --repo to be ignored.",
)
@click.option(
    "--goproxy",
    default="https://proxy.golang.org/",
    help="GOPROXY to use when downloading Golang module source",
    show_default=True,
)
@click.option(
    "--output",
    "-o",
    help="Download the source archive and write to this file name",
    default=None,
)
@click.option(
    "-O",
    "auto_output",
    is_flag=True,
    default=False,
    help="Download the source archive and write to a default file name."
    "The names vary according to the source type and the archive type, "
    "but will generally follow the format: "
    "{name}-{version}.{distro/type}.tar.[gz|xz] "
    "(This option takes precedence over -o/--output)",
)
@click.option(
    "--timeout",
    type=click.IntRange(1),
    default=30,
    help="Timeout when making requests.  Must be greater than zero.",
    show_default=True,
)
def main(
    distro,
    name,
    version,
    pyindex,
    aports,
    repo,
    goproxy,
    output,
    auto_output,
    source_repo,
    binary_repo,
    timeout,
):
    """Find and optionally download source files.

    Given a binary name and version, will find and print the URL(s) to the
    source file(s).

    If the --output option is present, the URLs are all downloaded and
    combined into a LZMA-compressed tar file and written to the file
    name specifed.  If the original source is already an archive then that
    archive is used instead.

    The sources currently supported are 'debian', 'ubuntu', 'rhel', 'centos',
    'alpine', 'photon', 'java', 'go', 'python', 'create', 'phppecl',
    'phpcomposer', and 'npm', one of which must be specified as the DISTRO
    argument.
    """
    try:
        func = functools.partial(
            getattr(Finder, distro), name, version, timeout=timeout
        )
    except AttributeError:
        click.echo(f"{distro} not available")
        click.get_current_context().exit(255)
    if distro == "alpine" and aports is None:
        click.echo("Must provide --aports for Alpine")
        click.get_current_context().exit(255)
    try:
        if distro == "python":
            disc_source = func(pyindex=pyindex)
        elif distro == "alpine":
            disc_source = func(aports_dir=aports)
        elif distro == "centos":
            disc_source = func(
                repos=repo, source_repos=source_repo, binary_repos=binary_repo
            )
        elif distro in ("photon", "rhel"):
            disc_source = func(
                source_repos=source_repo, binary_repos=binary_repo
            )
        elif distro == "go":
            disc_source = func(goproxy=goproxy)
        else:
            disc_source = func()
    except exceptions.SourceNotFound:
        click.echo("source not found")
        click.get_current_context().exit(255)

    if auto_output is not False or output is not None:
        fname = output
        if auto_output:
            name = name.replace(os.sep, ".")
            fname = f"{name}-{version}.{distro}{disc_source.archive_extension}"
        make_archive_from_discovery_source(disc_source, fname)


if __name__ == "__main__":
    main()
