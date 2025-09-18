# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates
# All rights reserved.

import re

from bs4 import BeautifulSoup

import soufi.finders.yum as yum_finder
from soufi import finder

VAULT = "https://repo.almalinux.org/vault"
# AlmaLinux does their very best to be a faithful CentOS clone.  Up to and
# including this little gem.  See the CentosFinder for an explanation.
CURRENT = "https://repo.almalinux.org/almalinux"
# Rather than aimlessly poke around their CDN, use this hopefully-sensible
# list of search dirs when looking for repodata
DEFAULT_SEARCH = ('BaseOS', 'AppStream', 'extras', 'cloud', 'devel')


class AlmaLinuxFinder(yum_finder.YumFinder):
    """Find AlmaLinux source files.

    By default, Iterates over the index at https://repo.almalinux.org/vault/
    """

    distro = finder.Distro.almalinux.value

    def _get_vault_repo_versions(self):
        response = self.get_url(VAULT)
        soup = BeautifulSoup(response.text, "html.parser")
        versions = []
        # AlmaLinux Vault is fond of symlinking the current point release to a
        # directory with just the major version number, e.g., `6.10/`->`6/`.
        # This means that such directories are inherently unstable and their
        # contents are subject to change without notice, so we'll ignore
        # them in favour of the "full" names.
        for link in soup.find_all("a", href=re.compile(r"^./\d+\.\d")):
            version = link.get("href").rstrip("/")
            if '-beta' in version:
                # Ignore beta releases; we may want to make this a switchable
                # behaviour.
                continue
            if re.match(r"^./\d+\.\d+", version):
                versions.append(version[2:])
        return sorted(versions, reverse=True)  # Sort to prioritize newer

    def _get_dirs(self):
        """Get all the possible Vault dirs that could match."""
        versions = self._get_vault_repo_versions()
        # Dir names are just the versions.
        return versions

    def get_source_repos(self):
        """Determine which source search paths are valid.

        Spams the vault with HEAD requests and keeps the ones that hit.

        This is implemented as a generator so that the methods in the
        YumFinder base class can "load as it goes", rather than having to
        do a ton of discovery up-front that might end up being wasted.
        Absolutely everything is cached, so the relative overhead of having
        to run the generator over when re-walking the list of repos is minimal.
        """
        for dir in self._get_dirs():
            for subdir in DEFAULT_SEARCH:
                url = f"{VAULT.rstrip('/')}/{dir}/{subdir}/Source/"
                if self.test_url(url + "repodata/"):
                    yield url

    def get_binary_repos(self):
        """Determine which binary search paths are valid.

        Spams the vault with HEAD requests and keeps the ones that hit.

        This is also implemented as a generator.  See get_source_repos().
        """

        def _find_valid_repo_url(dir, subdir):
            vault_url = f"{VAULT.rstrip('/')}/{dir}/{subdir}/x86_64/"
            current_url = f"{CURRENT.rstrip('/')}/{dir}/{subdir}/x86_64/"
            for url in vault_url, current_url:
                if self.test_url(url + "os/repodata/"):
                    yield url + "os/"
                    break

        for dir in self._get_dirs():
            for subdir in DEFAULT_SEARCH:
                yield from _find_valid_repo_url(dir, subdir)
