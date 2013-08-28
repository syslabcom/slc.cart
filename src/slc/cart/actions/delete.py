# -*- coding: utf-8 -*-
"""A Cart Action for deleting all items listed in cart."""

from five import grok
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from slc.cart.interfaces import ICartAction

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
        """Delete all items currently in cart and clear the cart's contents."""
        cart_view = self.context.restrictedTraverse('cart')
        request = self.context.REQUEST
        if len(cart_view.items) == 0:
            api.portal.show_message(
                message="You did not select any documents. Nothing was done.",
                request=request,
                type="warning")
            return

        handled = list()
        for item in cart_view.items:
            obj = api.content.get(UID=item['UID'])
            if obj is None:
                # An object that is in cart was apparently deleted by someone
                # else and dosn't exist anymore, so there's nothing to do.
                continue
            api.content.delete(obj)
            handled.append('"%s"' % item['Title'])

        api.portal.show_message(
            message="The following items have been deleted: %s" % ', '.join(
                sorted(handled)),
            request=request,
            type="success")

        cart_view.clear()
