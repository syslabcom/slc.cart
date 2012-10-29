# -*- coding: utf-8 -*-
"""A Cart Action for deleting all items listed in cart."""

from five import grok
from slc.cart.interfaces import ICartAction
from Products.CMFCore.interfaces import ISiteRoot

NAME = 'delete'
TITLE = u'Delete'
WEIGHT = 20


class DeleteAction(grok.Adapter):
    """Delete Action implementation that deletes items listed in cart."""
    grok.context(ISiteRoot)
    grok.provides(ICartAction)
    grok.name(NAME)

    name = NAME
    title = TITLE
    weight = WEIGHT

    def run(self):
        """TODO:
        """
        print 'delete stuff here'
