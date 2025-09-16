# -*- coding: utf-8 -*-

# ###########################################################################
#
# This file is part of Taurus
#
# http://taurus-scada.org
#
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
#
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
#
# ###########################################################################

"""This module exposes the Qt module
"""

from .QtCore import *  # noqa: F403,F401
from .QtGui import *  # noqa: F403,F401

# Fixes for PyQt6 for QtWidgets module needs to be loaded
# here, since enums from QtWidgets are to be propagate to Qt
# namespace.
from .QtWidgets import *  # noqa: F403,F401
