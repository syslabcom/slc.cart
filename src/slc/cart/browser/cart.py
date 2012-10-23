# -*- coding: utf-8 -*-
"""Download cart for batch processing of items."""

from Products.CMFCore.interfaces import IContentish
from collections import namedtuple
from five import grok
from plone import api
from slc.cart.interfaces import NoResultError
from zope.annotation.interfaces import IAnnotations
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import json
import logging

logger = logging.getLogger("slc.cart")
grok.templatedir('.')

STATUS = namedtuple('STATUS', ['OK', 'ERROR'])(*range(2))
"""Response status codes."""


class CartView(BrowserView):
    """A BrowserView for listing items in cart."""

    template = ViewPageTemplateFile('cart.pt')

    def __call__(self):
        """Must be here as a convention."""
        return self.template()

    def _get_brain_by_UID(self, UID):
        """Return portal_catalog brains metadata of an item with the specified
        UID.

        :param UID: Unique ID of an item.
        :type UID: string
        :returns: Brain (metadata) of item of passed UID.
        :rtype: Brain

        """
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(UID=UID)

        return brains[0] if brains else None

    @property
    def cart(self):
        """TODO"""
        # get the zope.annotations object stored on current member object
        annotations = IAnnotations(api.user.get_current())
        return annotations.setdefault('cart', set())

    def items(self):
        """TODO:

        :returns: Return Brains (metadata) of items in user's cart.
        :rtype: list of Brains
        """
        items = []
        for UID in self.cart:
            brain = self._get_brain_by_UID(UID)
            if brain:
                items.append(brain)
            else:
                msg = "An item in cart (UID: {0}) not found in the catalog."
                logger.warn(NoResultError(msg.format(UID)))

        return items

    def item_count(self):
        """Return the number of items currently in cart.

        :return: The number of items currently in cart.
        :rtype: int

        """
        if self.request.get('HTTP_X_REQUESTED_WITH', None) == 'XMLHttpRequest':
            return json.dumps(len(self.cart))
            return json.dumps(STATUS.OK)  # TODO: rewrite so thatou get a proper json dict! (status, body, err_msg)
        # NOTE: else simply don't return anything, because it's not meant
        # to be used for non-AJAX requests anyway


    def clear(self):
        """Remove all items from cart and display the @@cart view or return
        OK when requested via AJAX.

        This method is accessable via URL traversal (@@cart/clear).

        :return: A 'cart.pt' ViewPageTemplateFile which renders a normal
            Plone view or a JSON status.OK
        :rtype: ViewPageTemplateFile or JSON response

        """
        annotations = IAnnotations(api.user.get_current())
        annotations['cart'] = set()

        if self.request.get('HTTP_X_REQUESTED_WITH', None) == 'XMLHttpRequest':
            return json.dumps(STATUS.OK)  # TODO: rewrite so thatou get a proper json dict! (status, body, err_msg)
        else:
            return self.template()


class AddToCart(grok.View):
    """A BrowserView for adding an item to the cart."""

    grok.context(IContentish)
    grok.require('slc.cart')
    grok.name('add-to-cart')

    def render(self):
        portal = api.portal.get()
        cart = portal.restrictedTraverse('cart').cart
        cart.add(api.content.get_uuid(obj=self.context))

        if self.request.get('HTTP_X_REQUESTED_WITH', None) == 'XMLHttpRequest':
            return json.dumps(STATUS.OK)
        else:
            self.request.response.redirect(portal.absolute_url() + '/@@cart')


class RemoveFromCart(grok.View):
    """A BrowserView for removing an item from the cart."""

    grok.context(IContentish)
    grok.require('slc.cart')
    grok.name('remove-from-cart')

    def render(self):
        portal = api.portal.get()
        cart = portal.restrictedTraverse('cart').cart
        cart.discard(api.content.get_uuid(obj=self.context))

        if self.request.get('HTTP_X_REQUESTED_WITH', None) == 'XMLHttpRequest':
            return json.dumps(STATUS.OK)
        else:
            self.request.response.redirect(portal.absolute_url() + '/@@cart')


class IsInCart(grok.View):
    """A BrowserView for checking if an item is already in the cart."""

    grok.context(IContentish)
    grok.require('slc.cart')
    grok.name('is-in-cart')

    def render(self):
        portal = api.portal.get()
        cart = portal.restrictedTraverse('cart').cart
        UID = api.content.get_uuid(obj=self.context)

        if self.request.get('HTTP_X_REQUESTED_WITH', None) == 'XMLHttpRequest':
            return json.dumps(UID in cart)
        # NOTE: else simply don't return anything, because it's not meant
        # to be used for non-AJAX requests anyway
