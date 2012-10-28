# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Attribute
from zope.interface import Interface


class ISlcCartLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


# Cart Action specification
class ICartAction(Interface):
    """Definition of a Cart Action."""

    name = Attribute('Short id if the action, used in URLs, lookups, etc.')
    title = Attribute('User friendly title of the Cart Action.')

    def run():
        """Perform the action."""


# Exceptions
class NoResultError(Exception):
    """Exception if catalog returns zero results."""
