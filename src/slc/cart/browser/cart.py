# -*- coding: utf-8 -*-
"""Download cart for batch processing of items."""

from collections import namedtuple
from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from slc.cart.interfaces import NoResultError
from zope.annotation.interfaces import IAnnotations

import json
import logging

logger = logging.getLogger("slc.cart")


class CartView(BrowserView):
    """A BrowserView for listing and adding items to cart."""

    template = ViewPageTemplateFile('cart.pt')

    STATUS = namedtuple('STATUS', ['OK', 'ERROR'])(*range(2))
    """Response status codes."""

    def __call__(self):
        """Request controller. It routes different types of @@cart requests to
        their dedicated handler methods.
        """

        supported_methods = (
            'item-count',
            'add',
            'remove',
            'clear',
            'download',
            'contains',
        )

        # if query string is provided, call given method
        for method in supported_methods:
            if method in self.request:
                return getattr(self, method.replace('-', '_'))()

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

    def _get_cart(self):
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
        for UID in self._get_cart():
            brain = self._get_brain_by_UID(UID)
            if brain:
                items.append(brain)
            else:
                msg = "An item in cart (UID: {0}) not found in the catalog."
                logger.warn(NoResultError(msg.formtat(UID)))

        return self._prepare_response(self.STATUS.OK, items)

    def item_count(self):
        """Return the number of items currently in cart.

        :return: The number of items currently in cart.
        :rtype: ViewPageTemplateFile or JSON response
        """
        count = len(self._get_cart())
        return self._prepare_response(self.STATUS.OK, count)

    def contains(self, UID=None):
        """Check if an item exists in the cart.

        :return: Boolean describing if item exists in logged in user's cart.
        :rtype: ViewPageTemplateFile or JSON response
        """
        UID = UID or self.request.get('contains')
        cart = self._get_cart()

        response_body = (UID in cart)
        return self._prepare_response(self.STATUS.OK, response_body)

    def add(self, UID=None):
        """A method for adding items to cart.

        :param UID: Unique ID of an item.
        :type UID: string
        :return: Normal request: A 'cart.pt' ViewPageTemplateFile which
            renders a normal Plone view.
        :return: AJAX request: JSON response describing whether the item
            was added or not (an item might not be added if it can't be found
            in the database)
        :rtype: ViewPageTemplateFile or JSON response
        """
        UID = UID or self.request.get('add')
        cart = self._get_cart()

        if self._get_brain_by_UID(UID):
            cart.add(UID)
            return self._prepare_response(self.STATUS.OK, True)
        else:
            return self._prepare_response(self.STATUS.OK, False)

    def remove(self, UID=None):
        """
        A method for removing items from cart.

        :return: A 'cart.pt' ViewPageTemplateFile which renders a normal
            Plone view.
        :rtype: ViewPageTemplateFile or JSON response
        """
        UID = UID or self.request.get('remove')
        cart = self._get_cart()
        cart.discard(UID)

        return self._prepare_response(self.STATUS.OK)

    def clear(self):
        """
        Remove all items from cart.

        :return: A 'cart.pt' ViewPageTemplateFile which renders a normal
            Plone view.
        :rtype: ViewPageTemplateFile or JSON response
        """
        annotations = IAnnotations(api.user.get_current())
        annotations['cart'] = set()

        return self._prepare_response(self.STATUS.OK)

    def _prepare_response(self, status, body=None):
        """Prepare response based on the request type (AJAX, non-AJAX).

        On AJAX request return a JSON-formatted response, otherwise return
        a normal Plone response - a ViewPageTemplateFile.

        :param status: status code indicating whether a request was
            successfully processed or not
        :type status: int
        :param body: the body of the response
        :type body: any JSON-serializable type
        :return: A 'cart.pt' ViewPageTemplateFile which renders a normal
            Plone view or a response formatted as a JSON string.
        :rtype: ViewPageTemplateFile or string
        """
        if body is None:
            body = ""

        if self.request.get('HTTP_X_REQUESTED_WITH', None) == 'XMLHttpRequest':
            response_dict = dict(status=status, body=body)
            return json.dumps(response_dict)
        else:
            return self.template()

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
