# -*- coding: utf-8 -*-
"""A Cart Action for deleting all items listed in cart."""

from five import grok
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from slc.cart import _
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
        """Delete all items currently in cart and clear the cart's contents.
        """
        request = self.context.REQUEST
        cart_view = self.context.restrictedTraverse('cart')
        cart = cart_view.cart

        # NOTE: we must iterate over a copy because we modify the original cart
        for obj_uuid in cart.copy():
            obj = api.content.get(UID=obj_uuid)
            if obj is None:
                # TODO: what if an item does not exist in the portal anymore?
                # if it was deleted by someone else for instance? log a warning?
                pass
            else:
                # TODO: what about race conditions if an item is deleted just
                # before we try to? try-except?
                api.content.delete(obj)

        api.portal.show_message(
            message=_(u"All the items in cart were successfully deleted."),
            request=request,
            type="info")

        cart_view.clear()
