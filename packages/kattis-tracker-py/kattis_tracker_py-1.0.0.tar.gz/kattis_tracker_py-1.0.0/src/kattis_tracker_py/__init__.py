# SPDX-FileCopyrightText: 2025-present Christian <chrille_0313@hotmail.com>
#
# SPDX-License-Identifier: MIT

from importlib.metadata import version as get_version

__version__ = get_version(__package__)

from .client import KattisTrackerClient
