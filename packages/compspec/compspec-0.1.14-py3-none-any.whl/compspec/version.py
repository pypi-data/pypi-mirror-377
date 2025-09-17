__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022-2024, Vanessa Sochat"
__license__ = "MIT"

__version__ = "0.1.14"
AUTHOR = "Vanessa Sochat"
AUTHOR_EMAIL = "vsoch@users.noreply.github.com"
NAME = "compspec"
PACKAGE_URL = "https://github.com/compspec/compspec"
KEYWORDS = "diff, comparison, composition, specification, abi, compatibility, symbols"
DESCRIPTION = "Compatibility specifications and models"
LICENSE = "LICENSE"

################################################################################
# Global requirements

INSTALL_REQUIRES = (
    ("clingo", {"min_version": None}),
    ("pyaml", {"min_version": None}),
    ("jsonschema", {"min_version": None}),
    ("requests", {"min_version": None}),
    ("argparse-dataclass", {"min_version": None}),
)

TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)
INSTALL_REQUIRES_ALL = INSTALL_REQUIRES + TESTS_REQUIRES
