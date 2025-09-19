#!/usr/bin/env python
#
# Copyright (c) 2023 Katonic Pty Ltd. All rights reserved.
#
import importlib_metadata


def get_installed_version(package, module=None):
    """
    Obtains the installed package version using `importlib_metadata.version`. If it fails, use
    `__import__(module or package).__version__`.
    """
    try:
        version = importlib_metadata.version(package)
    except importlib_metadata.PackageNotFoundError:
        # Note `importlib_metadata.version(package)` is not necessarily equal to
        # `__import__(package).__version__`. See the example for pytorch below.
        #
        # Example
        # -------
        # $ pip install torch==1.9.0
        # $ python -c "import torch; print(torch.__version__)"
        # 1.9.0+cu102
        # $ python -c "import importlib_metadata; print(importlib_metadata.version('torch'))"
        # 1.9.0
        version = __import__(module or package).__version__

    return version
