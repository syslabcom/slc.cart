# -*- coding: utf-8 -*-
"""A Cart Action for deleting all items listed in cart."""

from five import grok
from OFS.CopySupport import _cb_encode
from OFS.CopySupport import cookie_path
from OFS.Moniker import Moniker
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from slc.cart.interfaces import ICartAction

NAME = 'cut'
TITLE = u'Cut'
WEIGHT = 17


class CutAction(grok.Adapter):
    """Cut Action implementation that performs "cut" on the items in cart."""
    grok.context(ISiteRoot)
    grok.provides(ICartAction)
    grok.name(NAME)

    name = NAME
    title = TITLE
    weight = WEIGHT

    def run(self):
        """Cut all items currently in cart and add them to clipboard."""
        cart_view = self.context.restrictedTraverse('cart')
        request = self.context.REQUEST
        cart = cart_view.cart

        # create a list of "Monik-ed" object paths for those objects
        # that we will store into clipboard
        obj_list = []

        for obj_uuid in cart:
            obj = api.content.get(UID=obj_uuid)
            if obj is None:
                # An object that is in cart was apparently deleted by someone
                # else and dosn't exist anymore, so there's nothing to do.
                continue

            if obj.wl_isLocked():
                continue  # TODO: write to log? error?

            if not obj.cb_isMoveable():
                continue  # TODO: write to log? error?

            m = Moniker(obj)
            obj_list.append(m.dump())

        # now store cutdata into a cookie
        # TODO: what if there's nothing in the list?
        ct_data = (1, obj_list)
        ct_data = _cb_encode(ct_data)  # probably means "clipboard encode"?

        response = request.response
        path = '{0}'.format(cookie_path(request))
        response.setCookie('__cp', ct_data, path=path)
        request['__cp'] = ct_data

        api.portal.show_message(
            message="{0} item(s) cut.".format(len(obj_list)),
            request=request,
            type="info")

        portal = api.portal.get()
        response.redirect(portal.absolute_url() + '/@@cart')
