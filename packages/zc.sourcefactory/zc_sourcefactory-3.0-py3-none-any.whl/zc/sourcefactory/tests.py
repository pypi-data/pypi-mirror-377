##############################################################################
#
# Copyright (c) 2006 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unit tests
"""
import doctest
import unittest

import ZODB.interfaces
import ZODB.utils
import zope.component
import zope.interface
from zope.component import testing
from zope.configuration import xmlconfig
from zope.site import folder
from zope.site.interfaces import IFolder

import zc.sourcefactory


class ConnectionStub:

    _id = 0

    def __call__(self, obj):
        return self

    def add(self, obj):
        self._id += 1
        obj._p_oid = ZODB.utils.p64(self._id)


def setUp(test):
    testing.setUp(test)
    xmlconfig.XMLConfig('ftesting.zcml', zc.sourcefactory)()
    zope.component.provideAdapter(
        ConnectionStub(), (IFolder,), ZODB.interfaces.IConnection)
    test.globs['rootFolder'] = folder.rootFolder()


def tearDown(test):
    testing.tearDown(test)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt'),
        doctest.DocFileSuite('mapping.txt'),
        doctest.DocFileSuite('constructors.txt'),
        doctest.DocFileSuite('adapters.txt', setUp=setUp, tearDown=tearDown,
                             optionflags=doctest.ELLIPSIS),
    ))
