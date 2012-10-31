# -*- coding: utf-8 -*-
"""A Cart Action for deleting all items listed in cart."""

from five import grok
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from slc.cart.interfaces import ICartAction

import logging

logger = logging.getLogger("slc.cart")

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
        cart = cart_view.cart

        for obj_uuid in cart:
            obj = api.content.get(UID=obj_uuid)
            if obj is None:
                # An object that is in cart was apparently deleted by someone
                # else and dosn't exist anymore, so there's nothing to do.
                pass
            else:
                try:
                    api.content.delete(obj)
                except Exception, e:
                    # The operation most likely failed because obj was deleted
                    # right before we tried to delete it. That's OK, because
                    # it is deleted now, so there's nothing more to do. But we
                    # still write it to log in case we masked some other error
                    # that could be relevant
                    logger.info(e)
                    pass

        api.portal.show_message(
            message="All items in cart were successfully deleted.",
            request=request,
            type="info")

        cart_view.clear()
