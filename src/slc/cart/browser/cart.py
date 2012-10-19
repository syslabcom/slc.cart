# -*- coding: utf-8 -*-
"""Download cart for batch processing of items."""

from zope.annotation.interfaces import IAnnotations
from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from slc.cart.interfaces import NoResultError
from StringIO import StringIO

import logging
import zipfile

logger = logging.getLogger("slc.cart")


class CartView(BrowserView):
    """A BrowserView for listing and adding items to cart."""

    template = ViewPageTemplateFile('cart.pt')

    def __call__(self):
        """Request controller. It routes different types of @@cart requests to
        their dedicated handler methods.
        """

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

    def get_cart(self):
        """TODO"""
        # get the zope.annotations object stored on current member object
        annotations = IAnnotations(api.user.get_current())

        # handle first access
        if not isinstance(annotations, dict):
            annotations.setdefault('cart', set())

        return annotations['cart']

    def items(self):
        """
        :returns: Returns Brains (metadata) of items in user's cart.
        :rtype: list of Brains
        """

        # get UIDs
        UIDs = self.get_cart()

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
        return str(len(self.get_cart()))

    def is_item_in_cart(self):
        """
        :returns: Boolean describing if item exists in logged in user's cart.
        :rtype: json bool
        """
        UID = self.request.get('is-item-in-cart')
        UIDs = self.get_cart()

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
        UID = UID or self.request.get('add')
        cart = self.get_cart()

        try:
            UID = api.content.get(uid=UID)  # check if this is a valid UID
            cart.add(UID)
            status = True
            message = "Item added to cart."
        except ValueError:
            status = False
            message = "Item does not exist."

        # TODO

        # if UID in cart:
        #     status = False
        #     message = "Item already in cart."
        # else:
        #     try:
        #         self._get_item_brain_by_UID(UID)
        #     except NoResultError:
        #         status = False
        #         message = "Item does not exist."
        #     else:
        #         cart.append(UID)
        #         member.setMemberProperties({'cart': tuple(cart)})
        #         status = True
        #         message = "Item added to cart."

        return self.template()

    # def remove(self):
    #     """
    #     A method for removing items from cart.

    #     :returns: A 'cart.pt' ViewPageTemplateFile which renders a normal
    #         Plone view.
    #     :rtype: ViewPageTemplateFile
    #     """
    #     member = api.user.get_current()

    #     UID = self.request.get('remove')
    #     cart = list(member.getProperty('cart', ()))

    #     if not UID in cart:
    #         status = False
    #         message = "Item not in cart."
    #     else:
    #         cart.remove(UID)
    #         member.setMemberProperties({'cart': tuple(cart)})
    #         status = True
    #         message = "Item removed from cart."

    #     return self.template()

    # def clear(self):
    #     """
    #     Removes all items from cart.

    #     :returns: A 'cart.pt' ViewPageTemplateFile which renders a normal
    #         Plone view.
    #     :rtype: ViewPageTemplateFile
    #     """
    #     member = api.user.get_current()

    #     member.setMemberProperties({'cart': tuple()})
    #     return self.template()

    # def download(self):
    #     """
    #     :type format: string
    #     :returns: A stream of binary data of a ZIP file of all items in the
    #         cart.
    #     :rtype: StringIO binary stream
    #     """
    #     member = api.user.get_current()

    #     output = StringIO()
    #     zf = zipfile.ZipFile(output, mode='w')

    #     if not member.getProperty('cart'):
    #         api.portal.show_message(
    #             message=u"Cart is empty.",
    #             type="error",
    #             request=self.request,
    #         )
    #         return self.template()

    #     try:
    #         for UID in member.getProperty('cart'):

    #             try:
    #                 brain = self._get_item_brain_by_UID(UID)
    #             except NoResultError as e:
    #                 logger.warn(e.message)
    #                 continue

    #             item = brain.getObject()

    #             zf.writestr(
    #                 "Cart Download Pack/%s.txt" % (item.title),
    #                 item.data
    #             )
    #     finally:
    #         zf.close()

    #     self.context.REQUEST.response.setHeader(
    #         "Content-Type",
    #         "application/zip"
    #     )
    #     self.context.REQUEST.response.setHeader(
    #         'Content-Disposition',
    #         "attachment; filename=cart.zip"
    #     )
    #     return output.getvalue()
