# -*- coding: utf-8 -*-
"""Download cart for batch processing of items."""

from collections import namedtuple
from five import grok
from plone import api
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import ISiteRoot
from slc.cart.interfaces import ICartAction
from slc.cart.interfaces import NoResultError
from zExceptions import NotFound
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapter
from zope.component import getAdapters
from zope.publisher.interfaces import IPublishTraverse

import json
import logging

logger = logging.getLogger("slc.cart")
grok.templatedir('templates')

STATUS = namedtuple('STATUS', ['OK', 'ERROR'])(*range(2))
"""Response status codes."""

ERR_LEVEL = namedtuple('ERR_LEVEL', ['WARNING', 'ERROR'])(*range(1, 3))
"""Error severity levels."""


ALLOWED_VIA_URL = [
    'item_count',
    'clear',
]
"""Attributes that we allow to be traversable via URL."""


class Cart(grok.View):
    """A BrowserView for listing items in cart."""

    grok.implements(IPublishTraverse)
    grok.context(ISiteRoot)
    grok.require('slc.cart')

    action = None

    def publishTraverse(self, request, name):
        """A custom publishTraverse method.

        This enables us to use URL traversal to run cart actions. Examples:
        @@cart/delete, @@cart/download, etc. URL access is only allowed for
        attributes listed in ALLOWED_VIA_URL.

        """
        if name in ALLOWED_VIA_URL:
            return getattr(self, name)
        else:
            self.action = name
            return getattr(self, '_run_action')

    ##################
    # Helper methods #
    ##################

    @property
    def cart(self):
        """Return a list of items currently in cart.

        Also initialize the cart along the way if necessary.

        :return: list of UUIDs of all the items in cart
        :rtype: list of strings
        """
        # get the zope.annotations object stored on current member object
        annotations = IAnnotations(api.user.get_current())
        return annotations.setdefault('cart', set())

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

    def _run_action(self):
        """Run a cart action.

        :param name: name of the action
        :type name: string
        :return: (nothing)
        """
        if not self.action in [name for name, action in self.actions]:
            raise NotFound()
        action = getAdapter(self.context, ICartAction, name=self.action)
        return action.run()

    ###########################
    # Methods used in cart.pt #
    ###########################

    @property
    def items(self):
        """Return metadata about items currently in cart.

        :return: Return Brains (metadata) of items in user's cart.
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

    @property
    def actions(self):
        """Get a sorted list of actions users can perform on cart items.

        Actions are sorted by their weight attribute in ascending order.

        :return: Actions that users can perform on cart items.
        :rtype: sorted list of (name, action) tuples
        """
        actions = getAdapters((self.context, ), ICartAction)
        return sorted(actions, key=lambda action: action[1].weight)

    #############################################
    # Methods also accessible via URL traversal #
    #############################################

    def item_count(self):
        """Return the number of items currently in cart.

        :return: The number of items currently in cart.
        :rtype: int

        """
        if self.request.get('HTTP_X_REQUESTED_WITH', None) == 'XMLHttpRequest':
            response_dict = {"status": STATUS.OK,
                             "body": len(self.cart),
                             "err_info": None, }
            return json.dumps(response_dict)
        else:
            return len(self.cart)

    def clear(self):
        """Remove all items from cart and redirect back to @@cart view.

        :return: redirect to @@cart
        """
        annotations = IAnnotations(api.user.get_current())
        annotations['cart'] = set()

        api.portal.show_message(
            message="Cart cleared.",
            type='info',
            request=self.request, )

        self.request.response.redirect(self.context.absolute_url() + '/@@cart')


class AddToCart(grok.View):
    """A BrowserView for adding an item to the cart."""

    grok.context(IContentish)
    grok.require('slc.cart')
    grok.name('add-to-cart')

    def render(self):
        portal = api.portal.get()
        cart = portal.restrictedTraverse('cart').cart
        limit = api.portal.get_registry_record('slc.cart.limit')

        if len(cart) >= limit:
            status = STATUS.ERROR
            body = None
            message = "Cart full (limit is {0} item(s))".format(limit)
            err_info = dict(msg=message,
                            level=ERR_LEVEL.WARNING,
                            label="Error")
        else:
            cart.add(api.content.get_uuid(obj=self.context))
            status = STATUS.OK
            body = len(cart)
            err_info = None

        if self.request.get('HTTP_X_REQUESTED_WITH', None) == 'XMLHttpRequest':

            response_dict = {"status": status,
                             "body": body,
                             "err_info": err_info, }
            return json.dumps(response_dict)
        else:
            if err_info:
                api.portal.show_message(
                    message=err_info['msg'],
                    type='error',
                    request=self.request, )
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
            response_dict = {"status": STATUS.OK,
                             "body": len(cart),
                             "err_info": None, }
            return json.dumps(response_dict)
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
        is_in_cart = UID in cart

        if self.request.get('HTTP_X_REQUESTED_WITH', None) == 'XMLHttpRequest':
            response_dict = {"status": STATUS.OK,
                             "body": is_in_cart,
                             "err_info": None, }
            return json.dumps(response_dict)
        else:
            return is_in_cart
