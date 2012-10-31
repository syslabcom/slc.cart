# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Attribute
from zope.interface import Interface


class ISlcCartLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class ICartAction(Interface):
    """Specification of what a Cart Action needs to provide."""

    name = Attribute('Short id if the action, used in URLs, lookups, etc.')
    title = Attribute('User friendly title of the Cart Action.')
    weight = Attribute('An integer used for sorting the actions.')

    def run():
        """Perform the action."""


# Exceptions
class NoResultError(Exception):
    """Exception if catalog returns zero results."""
