#!/usr/bin/env python

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

"""This package provides taurus Qt models

Pure PyQt view based widgets can be used to display the contents of the several
model classes provided here.

Displaying the device list in a :class:`PyQt5.Qt.QTreeView`::

    view = Qt.QTreeView()
    db = taurus.Database()
    model = taurus.qt.qtcore.TaurusDbDeviceModel()
    model.setDataSource(db)
    view.setModel(model)

Same example but in a :class:`PyQt5.Qt.QTableView`::

    view = Qt.QTableView()
    db = taurus.Database()
    model = taurus.qt.qtcore.TaurusDbPlainDeviceModel()
    model.setDataSource(db)
    view.setModel(model)

And now inside a :class:`PyQt.Qt.QComboBox`::

    view = Qt.QComboBox()
    db = taurus.Database()
    model = taurus.qt.qtcore.TaurusDbPlainDeviceModel()
    model.setDataSource(db)
    view.setModel(model)
"""

from .taurusmodel import (
    TaurusBaseModel,
    TaurusBaseProxyModel,
    TaurusBaseTreeItem,
)
from .taurusdatabasemodel import (
    TaurusTreeDevicePartItem,
    TaurusTreeDeviceDomainItem,
    TaurusTreeDeviceFamilyItem,
    TaurusTreeDeviceMemberItem,
    TaurusTreeSimpleDeviceItem,
    TaurusTreeDeviceItem,
    TaurusTreeAttributeItem,
    TaurusTreeServerNameItem,
    TaurusTreeServerItem,
    TaurusTreeDeviceClassItem,
    TaurusDbBaseModel,
    TaurusDbSimpleDeviceModel,
    TaurusDbPlainDeviceModel,
    TaurusDbDeviceModel,
    TaurusDbSimpleDeviceAliasModel,
    TaurusDbPlainServerModel,
    TaurusDbServerModel,
    TaurusDbDeviceClassModel,
    TaurusDbBaseProxyModel,
    TaurusDbDeviceProxyModel,
    TaurusDbServerProxyModel,
    TaurusDbDeviceClassProxyModel,
)

__all__ = [
    "TaurusBaseTreeItem",
    "TaurusBaseModel",
    "TaurusBaseProxyModel",
    "TaurusTreeDevicePartItem",
    "TaurusTreeDeviceDomainItem",
    "TaurusTreeDeviceFamilyItem",
    "TaurusTreeDeviceMemberItem",
    "TaurusTreeSimpleDeviceItem",
    "TaurusTreeDeviceItem",
    "TaurusTreeAttributeItem",
    "TaurusTreeServerNameItem",
    "TaurusTreeServerItem",
    "TaurusTreeDeviceClassItem",
    "TaurusDbBaseModel",
    "TaurusDbSimpleDeviceModel",
    "TaurusDbPlainDeviceModel",
    "TaurusDbDeviceModel",
    "TaurusDbSimpleDeviceAliasModel",
    "TaurusDbPlainServerModel",
    "TaurusDbServerModel",
    "TaurusDbDeviceClassModel",
    "TaurusDbBaseProxyModel",
    "TaurusDbDeviceProxyModel",
    "TaurusDbServerProxyModel",
    "TaurusDbDeviceClassProxyModel",
]
__docformat__ = "restructuredtext"
