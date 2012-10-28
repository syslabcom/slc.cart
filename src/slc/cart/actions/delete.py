# -*- coding: utf-8 -*-
"""A Cart Action for deleting all items listed in cart."""

from five import grok
from slc.cart.interfaces import ICartAction
from Products.CMFCore.interfaces import ISiteRoot

NAME = 'delete'
TITLE = u'Delete'


class DeleteAction(grok.Adapter):
    """Delete Action implementation that deletes items listed in cart."""
    grok.context(ISiteRoot)
    grok.provides(ICartAction)
    grok.name(NAME)

    name = NAME
    title = TITLE

    def run(self):
        """TODO:
        """
        print 'delete stuff here'
