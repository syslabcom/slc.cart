# -*- coding: utf-8 -*-
"""A Cart Action for downloading all items listed in cart as a ZIP file."""

from five import grok
from slc.cart.interfaces import ICartAction
from Products.CMFCore.interfaces import ISiteRoot

NAME = 'download'
TITLE = u'Download'
WEIGHT = 10


class DownloadAction(grok.Adapter):
    """Download Action implementation for downloading items listed in cart."""
    grok.context(ISiteRoot)
    grok.provides(ICartAction)
    grok.name(NAME)

    name = NAME
    title = TITLE
    weight = WEIGHT

    def run(self):
        """TODO:
        """
        print 'download stuff here'
