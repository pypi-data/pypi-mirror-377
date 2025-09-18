##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Implementations of the basic policy components.

"""
__docformat__ = "reStructuredText"


import zope.component
import zope.intid.interfaces
from zope.dublincore import interfaces as dublincoreinterfaces

import zc.sourcefactory.browser.source
import zc.sourcefactory.interfaces


# Term policies


@zope.interface.implementer(zc.sourcefactory.interfaces.ITermPolicy)
class BasicTermPolicy:
    """A basic term policy.

    createTerm creates a FactoredTerm object.

    getTitle uses IDCDescriptiveProperties.title and falls back to
    `str`-representation of the value.
    """

    def createTerm(self, source, value, title, token, request):
        return zc.sourcefactory.browser.source.FactoredTerm(
            value, title, token)

    def getTitle(self, value):
        try:
            md = dublincoreinterfaces.IDCDescriptiveProperties(value)
        except TypeError:
            md = None

        if md:
            title = md.title
        elif isinstance(value, bytes):
            title = value.decode()
        else:
            title = str(value)
        return title


@zope.interface.implementer(zc.sourcefactory.interfaces.ITermPolicy)
class BasicContextualTermPolicy(BasicTermPolicy):
    """A basic contextual term policy.

    All methods are deferred to the BasicTermPolicy by removing the context
    argument.

    """

    def createTerm(self, context, source, value, title, token, request):
        return super().createTerm(
            source, value, title, token, request)

    def getTitle(self, context, value):
        return super().getTitle(value)


# Token policies

@zope.interface.implementer(zc.sourcefactory.interfaces.ITokenPolicy)
class BasicTokenPolicy:
    """A basic token policy.

    getToken adapts the value to IToken

    getValue iterates over the source comparing the tokens of the values to the
    token.
    """

    def getValue(self, source, token):
        for value in source:
            if source.factory.getToken(value) == token:
                return value
        raise KeyError("No value with token '%s'" % token)

    def getToken(self, value):
        return zc.sourcefactory.interfaces.IToken(value)


@zope.interface.implementer(zc.sourcefactory.interfaces.IContextualTokenPolicy)
class BasicContextualTokenPolicy(BasicTokenPolicy):
    """A basic contextual token policy.

    This implements a fallback to the context-free token policy but satisfies
    the contextual interfaces.

    """

    def getValue(self, context, source, token):
        for value in source:
            if source.factory.getToken(context, value) == token:
                return value
        raise KeyError("No value with token '%s'" % token)

    def getToken(self, context, value):
        return super().getToken(value)


@zope.interface.implementer(zc.sourcefactory.interfaces.ITokenPolicy)
class IntIdTokenPolicy:
    """A token policy based on intids."""

    def getValue(self, source, token):
        iid = int(token)
        value = self.intids.getObject(iid)
        if value in self.source:
            return value
        else:
            raise LookupError("no value matching token: %r" % token)

    def getToken(self, value):
        return str(self.intids.getId(value))

    # We can't use zope.cachedescriptors.property.Lazy for this since
    # the source factory exists across the entire process, and is used
    # across different requests.  Using Lazy for this would result in
    # the wrong ZODB connection being used in most threads.
    #
    @property
    def intids(self):
        return zope.component.getUtility(
            zope.intid.interfaces.IIntIds)


# Value policies

@zope.interface.implementer(zc.sourcefactory.interfaces.IValuePolicy)
class BasicValuePolicy:
    """An abstract basic value policy.

    `getValues()` is not implemented.

    The filter allows all values.
    """

    def filterValue(self, value):
        return True


@zope.interface.implementer(
    zc.sourcefactory.interfaces.IContextualValuePolicy)
class BasicContextualValuePolicy(BasicValuePolicy):
    """An abstract basic value policy.

    `getValues()` is not implemented.

    The filter allows all values.
    """

    def filterValue(self, context, value):
        return True


# Standard combined policies

class BasicSourcePolicy(BasicValuePolicy, BasicTokenPolicy, BasicTermPolicy):
    pass


class BasicContextualSourcePolicy(
        BasicContextualValuePolicy,
        BasicContextualTokenPolicy,
        BasicContextualTermPolicy):
    pass


class IntIdSourcePolicy(BasicValuePolicy, IntIdTokenPolicy, BasicTermPolicy):
    pass
