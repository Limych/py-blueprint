#!/usr/bin/env python
"""Library module setup."""

import re
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    """PyTest controller."""

    # Code from here:
    # https://docs.pytest.org/en/latest/goodpractices.html#manual-integration

    # pylint: disable=attribute-defined-outside-init
    def finalize_options(self):
        """Finalize test command options."""
        TestCommand.finalize_options(self)
        # we don't run integration tests which need an actual blueprint_client device
        self.test_args = ["-m", "not integration"]
        self.test_suite = True

    # pylint: disable=import-outside-toplevel,import-error
    def run_tests(self):
        """Run tests."""
        # import here, cause outside the eggs aren't loaded
        import shlex

        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


def load_requirements(fpath: str) -> list:
    """Load requirements from file."""
    with open(fpath, encoding="utf8") as f_req:
        data = list(f_req)
    imp = re.compile(r"^(-r|--requirement)\s+(\S+)")
    reqs = []
    for i in data:
        # pylint: disable=invalid-name
        m = imp.match(i)
        if m:
            reqs.extend(load_requirements(m.group(2)))
        else:
            reqs.append(i)

    return reqs


with open("blueprint_client/const.py", encoding="utf-8") as file:
    src = file.read()
metadata = dict(re.findall(r'([a-z]+) = "([^"]+)"', src, re.IGNORECASE))
metadata.update(dict(re.findall(r"([a-z]+) = '([^']+)'", src, re.IGNORECASE)))
docstrings = re.findall(r'"""(.*?)"""', src, re.MULTILINE | re.DOTALL)

NAME = "blueprint_client"

PACKAGES = [x for x in find_packages() if x not in ["scripts", "tests"]]

VERSION = metadata["VERSION"]
AUTHOR_EMAIL = metadata.get("AUTHOR", "Unknown <no@email.com>")
WEBSITE = metadata.get("WEBSITE", "")
LICENSE = metadata.get("LICENSE", "")
DESCRIPTION = docstrings[0]

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

with open("README.md", encoding="utf-8") as file:
    LONG_DESCRIPTION = file.read()
    LONG_DESCRIPTION_TYPE = "text/markdown"

# Extract name and e-mail ("Firstname Lastname <mail@example.org>")
AUTHOR, EMAIL = re.match(r"(.*) <(.*)>", AUTHOR_EMAIL).groups()

REQUIREMENTS = load_requirements("requirements.txt")
TEST_REQUIREMENTS = load_requirements("requirements-test.txt")

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    license=LICENSE,
    url=WEBSITE,
    packages=PACKAGES,
    install_requires=REQUIREMENTS,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_TYPE,
    classifiers=CLASSIFIERS,
    cmdclass={"pytest": PyTest},
    test_suite="tests",
    tests_require=TEST_REQUIREMENTS,
)
