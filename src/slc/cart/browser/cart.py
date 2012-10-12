# -*- coding: utf-8 -*-
"""Download cart for batch processing of items."""

from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from slc.cart.interfaces import NoResultError
from StringIO import StringIO

import json
import logging
import zipfile

logger = logging.getLogger("slc.cart")


class CartView(BrowserView):
    """A BrowserView for listing and adding items to cart.

    - display items in cart: http://localhost:8080/dev/cart
    - add item to cart: http://localhost:8080/dev/cart?add=ecd1ca19a11327b8188f0d35c0b4e5c6
    - remove item from cart: http://localhost:8080/dev/cart?remove=ecd1ca19a11327b8188f0d35c0b4e5c6
    - get number of items in cart: http://localhost:8080/dev/cart?num-of-items=1
    - download ZIP file of all items in the cart: http://localhost:8080/dev/cart?download=1
    - remove all items from cart: http://localhost:8080/dev/cart?clear=1
    """

    template = ViewPageTemplateFile('cart.pt')

    def __call__(self):
        """Request controller. It routes different types of @@cart requests to
        their dedicated handler methods.
        """
        if api.user.is_anonymous():
            self.request.RESPONSE.redirect(
                self.context.absolute_url() + '/login_form'
            )
            return

        # TODO: separate ajax and normal template logic completely (maybe some
        # addon product to handle this easier?)
        # TODO: refactor add/remove to share the same code

        supported_methods = (
            'num-of-items',
            'add',
            'remove',
            'clear',
            'download',
            'is-item-in-cart',
        )

        # if query string is provided, call given method
        for method in supported_methods:
            if method in self.request:
                return getattr(self, method.replace('-', '_'))()

        return self.template()

    def _get_item_brain_by_UID(self, UID):
        """
        Returns portal_catalog brains metadata of an item with the passed UID.

        :param UID: Unique ID of an item.
        :type UID: string
        :raises NoResultError: No item found with this UID.
        :returns: Brain (metadata) of item of passed UID.
        :rtype: Brain
        """

        if not UID:
            raise NoResultError

        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(UID=UID)

        if not brains:
            raise NoResultError("No item found with this UID: %r" % UID)

        return brains[0]

    def items(self):
        """
        :returns: Returns Brains (metadata) of items in user's cart.
        :rtype: list of Brains
        """

        # get UIDs
        member = api.user.get_current()
        UIDs = member.getProperty('cart', ())

        # fetch Catalog Brains for UIDs
        items = []
        for UID in UIDs:

            try:
                brain = self._get_item_brain_by_UID(UID)
            except NoResultError as e:
                logger.warn(e.message)
                continue

            items.append(brain)

        return items

    def num_of_items(self):
        """
        :returns: Number of items in cart.
        :rtype: int
        """
        member = api.user.get_current()
        return str(len(member.getProperty('cart', ())))

    def is_item_in_cart(self):
        """
        :returns: Boolean describing if item exists in logged in user's cart.
        :rtype: json bool
        """
        member = api.user.get_current()

        UID = self.request.get('is-item-in-cart')
        UIDs = member.getProperty('cart', ())

        return 'true' if UID in UIDs else 'false'

    ### Cart items management

    def add(self, UID=None):
        """
        A method for adding items to cart.

        :param UID: Unique ID of an item.
        :type UID: string
        :returns: Normal request: A 'cart.pt' ViewPageTemplateFile which
            renders a normal Plone view.
        :returns: AJAX request: JSON response whether an item was successfull
            added or not.
        :rtype: ViewPageTemplateFile or JSON response
        """
        member = api.user.get_current()

        UID = UID or self.request.get('add')
        cart = list(member.getProperty('cart', ()))

        if UID in cart:
            status = False
            message = "Item already in cart."
        else:
            try:
                self._get_item_brain_by_UID(UID)
            except NoResultError:
                status = False
                message = "Item does not exist."
            else:
                cart.append(UID)
                member.setMemberProperties({'cart': tuple(cart)})
                status = True
                message = "Item added to cart."

        return self._handle_ajax(status, message)

    def remove(self):
        """
        A method for removing items from cart.

        :returns: A 'cart.pt' ViewPageTemplateFile which renders a normal
            Plone view.
        :rtype: ViewPageTemplateFile
        """
        member = api.user.get_current()

        UID = self.request.get('remove')
        cart = list(member.getProperty('cart', ()))

        if not UID in cart:
            status = False
            message = "Item not in cart."
        else:
            cart.remove(UID)
            member.setMemberProperties({'cart': tuple(cart)})
            status = True
            message = "Item removed from cart."

        return self._handle_ajax(status, message)

    def _handle_ajax(self, status, message):
        # On AJAX request return JSON response, else return normal Plone
        # template
        if self.request.get('HTTP_X_REQUESTED_WITH', None) == 'XMLHttpRequest':
            return json.dumps({'return_status': status, 'message': message})
        else:
            api.portal.show_message(
                message=message,
                type=status and 'info' or 'error',
                request=self.request,
            )
            return self.template()

    def clear(self):
        """
        Removes all items from cart.

        :returns: A 'cart.pt' ViewPageTemplateFile which renders a normal
            Plone view.
        :rtype: ViewPageTemplateFile
        """
        member = api.user.get_current()

        member.setMemberProperties({'cart': tuple()})
        return self.template()

    def download(self):
        """
        :type format: string
        :returns: A stream of binary data of a ZIP file of all items in the
            cart.
        :rtype: StringIO binary stream
        """
        member = api.user.get_current()

        output = StringIO()
        zf = zipfile.ZipFile(output, mode='w')

        if not member.getProperty('cart'):
            api.portal.show_message(
                message=u"Cart is empty.",
                type="error",
                request=self.request,
            )
            return self.template()

        try:
            for UID in member.getProperty('cart'):

                try:
                    brain = self._get_item_brain_by_UID(UID)
                except NoResultError as e:
                    logger.warn(e.message)
                    continue

                item = brain.getObject()

                zf.writestr(
                    "Cart Download Pack/%s.txt" % (item.title),
                    item.data
                )
        finally:
            zf.close()

        self.context.REQUEST.response.setHeader(
            "Content-Type",
            "application/zip"
        )
        self.context.REQUEST.response.setHeader(
            'Content-Disposition',
            "attachment; filename=cart.zip"
        )
        return output.getvalue()
