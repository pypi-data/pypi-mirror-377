# Copyright (c) 2022 Cisco Systems, Inc. and its affiliates
# All rights reserved.

import soufi.finders.yum as yum_finder
from soufi import finder

DEFAULT_REPO = "https://cdn-ubi.redhat.com/content/public/ubi/dist"


class RHELFinder(yum_finder.YumFinder):
    """Find Red Hat Enterprise Linux source files.

    By default, uses the public UBI index at https://cdn-ubi.redhat.com
    """

    distro = finder.Distro.rhel.value

    # From: https://access.redhat.com/articles/4238681
    default_search_dirs = (
        'ubi9/9/x86_64/base',
        'ubi9/9/x86_64/appstream',
        'ubi9/9/x86_64/codeready-builder',
        'ubi8/8/x86_64/base',
        'ubi8/8/x86_64/appstream',
        'ubi8/8/x86_64/codeready-builder',
        'ubi/server/7/7Server/x86_64',
        'ubi/server/7/7Server/x86_64/extras',
        'ubi/server/7/7Server/x86_64/optional',
        'ubi/server/7/7Server/x86_64/rhscl/1',
        'ubi/atomic/7/7Server/x86_64',
    )

    def get_source_repos(self):
        for dir in self.default_search_dirs:
            yield f"{DEFAULT_REPO}/{dir}/source/SRPMS"

    def get_binary_repos(self):
        for dir in self.default_search_dirs:
            yield f"{DEFAULT_REPO}/{dir}/os"
