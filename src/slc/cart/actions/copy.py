# -*- coding: utf-8 -*-
"""A Cart Action for deleting all items listed in cart."""

from five import grok
from OFS.CopySupport import _cb_encode
from OFS.CopySupport import cookie_path
from OFS.Moniker import Moniker
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from slc.cart.interfaces import ICartAction

NAME = 'copy'
TITLE = u'Copy'
WEIGHT = 15


class CopyAction(grok.Adapter):
    """Copy Action implementation that copies items in cart to clipboard."""
    grok.context(ISiteRoot)
    grok.provides(ICartAction)
    grok.name(NAME)

    name = NAME
    title = TITLE
    weight = WEIGHT

    def run(self):
        """Copy all items currently in cart to clipboard
        """
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

            if not obj.cb_isCopyable():
                # TODO: write something to log?
                continue

            m = Moniker(obj)
            obj_list.append(m.dump())

        # now store copydata into a cookie
        # TODO: what if there's nothing in the list?
        cp_data = (0, obj_list)
        cp_data = _cb_encode(cp_data)  # probably means "clipboard encode"?

        response = request.response
        path = '{0}'.format(cookie_path(request))
        response.setCookie('__cp', cp_data, path=path)
        request['__cp'] = cp_data

        api.portal.show_message(
            message="Copied {0} object(s)".format(len(obj_list)),
            request=request,
            type="info")

        portal = api.portal.get()
        response.redirect(portal.absolute_url() + '/@@cart')