"""JAX TPU Embedding versioning utilities

For releases, the version is of the form:
  xx.yy.zz

For nightly builds, the date of the build is added:
  xx.yy.zz-devYYYMMDD
"""

_base_version = "0.1.0"
_version_suffix = "dev20250915"

# Git commit corresponding to the build, if available.
__git_commit__ = "9887a161131135b1d5bf90b4c27c5f1352a6da67"

# Library version.
__version__ = _base_version + _version_suffix

