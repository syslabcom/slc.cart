# -*- coding: utf-8 -*-
"""Testing the @@cart view."""

from contextlib import contextmanager
from plone import api
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from Products.statusmessages.interfaces import IStatusMessage
from slc.cart.browser.cart import ERR_LEVEL
from slc.cart.browser.cart import STATUS
from slc.cart.tests.base import FunctionalTestCase
from slc.cart.tests.base import IntegrationTestCase
from urllib2 import HTTPError
from zope.interface import alsoProvides

import json
import unittest2 as unittest


class TestCart(IntegrationTestCase):
    """ Test Cart BrowserView related stuff. """

    def setUp(self):
        """Custom shared utility setup for tests."""
        # prepare the request object
        from slc.cart.interfaces import ISlcCartLayer
        alsoProvides(self.layer['app'].REQUEST, ISlcCartLayer)

        # shortcuts
        self.portal = self.layer['portal']
        self.view = self.portal.restrictedTraverse('@@cart')

        # create test content
        self.item1 = api.content.create(
            container=self.portal, type='Document', id='item1')
        self.item2 = api.content.create(
            container=self.portal, type='Document', id='item2')
        self.item3 = api.content.create(
            container=self.portal, type='Document', id='item3')

    @contextmanager
    def disable_ajax(self):
        """A helper context manager to temporary disable requests via AJAX.
        """
        self.portal.REQUEST["HTTP_X_REQUESTED_WITH"] = ""
        yield
        self.portal.REQUEST["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"

    def test_browser_view_exists(self):
        """Test if @@cart browser view is registered and visible."""
        self.portal.REQUEST['ACTUAL_URL'] = self.portal.REQUEST['URL']
        html = self.view()
        self.failUnless(
            '<h1 class="documentFirstHeading">Cart</h1>' in html)

    def test_get_item_brain_by_UID(self):
        """Test if correct item object is returned for given UID and
        expected Exceptions are raised on errors.
        """

        # existing UIDs
        for obj in [self.item1, self.item2, self.item3]:
            returned_obj = self.view._get_brain_by_UID(
                obj.UID()).getObject()
            self.assertEqual(obj, returned_obj)

        # non-existing UIDs
        ret_val = self.view._get_brain_by_UID('a-non-existing-uid')
        self.assertIsNone(ret_val)

    def test_items(self):
        """Test returning list of brains (meta_data) of items in
        current member's cart.
        """

        # add some items to cart
        self.item1.restrictedTraverse("add-to-cart").render()
        self.item2.restrictedTraverse("add-to-cart").render()
        self.item3.restrictedTraverse("add-to-cart").render()

        # test that correct amount of items are in cart
        self.assertEqual(len(self.view.items), 3)

        # test that all items in cart are indeed Brain objects
        for type_of_object in [str(item.__class__)
                               for item in self.view.items]:
            self.assertEquals(
                type_of_object, "<class 'Products.ZCatalog.Catalog.mybrains'>")

    def test_is_item_in_cart(self):
        """Test boolean method."""

        # for non-AJAX requests a single value is returned
        out = self.item1.restrictedTraverse("is-in-cart").render()
        self.assertFalse(out)

        # test AJAX requests
        self.portal.REQUEST["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"

        response_dict = {"status": STATUS.OK,
                         "body": False,
                         "err_info": None, }

        # test for a non-existing item
        out = self.item1.restrictedTraverse("is-in-cart").render()
        self.assertEquals(out, json.dumps(response_dict))

        # test for an existing item
        response_dict['body'] = True
        self.item1.restrictedTraverse("add-to-cart").render()
        out = self.item1.restrictedTraverse("is-in-cart").render()

        self.assertEquals(out, json.dumps(response_dict))

    def test_item_count(self):
        """Test item_count method."""

        self.assertEqual(int(self.view.item_count()), 0)

        # test AJAX calls
        self.portal.REQUEST["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"

        with self.disable_ajax():
            self.assertEqual(int(self.view.item_count()), 0)

        self.item1.restrictedTraverse("add-to-cart").render()
        with self.disable_ajax():
            self.assertEqual(int(self.view.item_count()), 1)

        self.item2.restrictedTraverse("add-to-cart").render()
        with self.disable_ajax():
            self.assertEqual(int(self.view.item_count()), 2)

        self.item2.restrictedTraverse("remove-from-cart").render()
        with self.disable_ajax():
            self.assertEqual(int(self.view.item_count()), 1)

        # remove same item again, nothing should change
        self.item2.restrictedTraverse("remove-from-cart").render()
        with self.disable_ajax():
            self.assertEqual(int(self.view.item_count()), 1)

    def test_add(self):
        """Test if item is correctly added to the cart."""
        cart = self.portal.restrictedTraverse('cart').cart
        self.assertEqual(len(cart), 0)

        # add new item
        self.item1.restrictedTraverse("add-to-cart").render()
        self.assertIn(self.item1.UID(), cart)
        self.assertEqual(len(cart), 1)

        # add another item
        self.item2.restrictedTraverse("add-to-cart").render()
        self.assertIn(self.item2.UID(), cart)
        self.assertEqual(len(cart), 2)

        # add an item that already exists (nothing should change and
        # no error should be raised)
        self.portal.item1.restrictedTraverse("add-to-cart").render()
        self.assertIn(self.item1.UID(), cart)
        self.assertEqual(len(cart), 2)

    def test_add_ajax(self):
        """Test if item is correctly added to cart and if correct response
        is returned.
        """
        self.portal.REQUEST["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"

        response_dict = {"status": STATUS.OK,
                         "body": None,
                         "err_info": None, }

        cart = self.portal.restrictedTraverse('cart').cart
        self.assertEqual(len(cart), 0)

        # add new item
        out = self.item1.restrictedTraverse("add-to-cart").render()
        self.assertIn(self.item1.UID(), cart)
        self.assertEqual(len(cart), 1)
        response_dict["body"] = 1
        self.assertEqual(out, json.dumps(response_dict))

        # add another item
        out = self.item2.restrictedTraverse("add-to-cart").render()
        self.assertIn(self.item2.UID(), cart)
        self.assertEqual(len(cart), 2)
        response_dict["body"] = 2
        self.assertEqual(out, json.dumps(response_dict))

        # add an item that already exists (nothing should change and
        # no error should be raised)
        out = self.portal.item1.restrictedTraverse("add-to-cart").render()
        self.assertIn(self.item1.UID(), cart)
        self.assertEqual(len(cart), 2)
        response_dict["body"] = 2
        self.assertEqual(out, json.dumps(response_dict))

    def test_cart_limit(self):
        """Test if cart limit is honored when adding an item to cart."""

        # Set a lower limit, since it's 100 by default'
        api.portal.set_registry_record('slc.cart.limit', 1)
        cart = self.portal.restrictedTraverse('cart').cart
        self.assertEqual(len(cart), 0)

        # add a new item
        self.item1.restrictedTraverse("add-to-cart").render()
        self.assertEqual(len(cart), 1)
        messages = IStatusMessage(self.portal.REQUEST)
        self.assertEqual(len(messages.show()), 0)

        # add another item, error message should be displayed
        self.item2.restrictedTraverse("add-to-cart").render()
        messages = IStatusMessage(self.portal.REQUEST)
        message = messages.show()[0].message
        self.assertIn('Cart full (limit is 1 item(s))', message)
        self.assertEqual(len(cart), 1)

    def test_cart_limit_ajax(self):
        """Test if cart limit is honored when adding an item to cart and if
        correct reponse is returned.
        """

        self.portal.REQUEST["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"

        response_dict = {
            "status": STATUS.OK,
            "body": None,
            "err_info": None
        }

        error_response_dict = {
            "status": STATUS.ERROR,
            "body": None,
            "err_info": dict(msg='Cart full (limit is 1 item(s))',
                             level=ERR_LEVEL.WARNING,
                             label="Error",)
        }

        # Set a lower limit, since it's 100 by default'
        api.portal.set_registry_record('slc.cart.limit', 1)
        cart = self.portal.restrictedTraverse('cart').cart
        self.assertEqual(len(cart), 0)

        # add a new item
        out = self.item1.restrictedTraverse("add-to-cart").render()
        response_dict["body"] = 1
        self.assertEqual(out, json.dumps(response_dict))
        self.assertEqual(len(cart), 1)

        # add another item, we should get a reponse with status set to
        # 'ERROR' and an error message
        out = self.item2.restrictedTraverse("add-to-cart").render()
        self.assertEqual(out, json.dumps(error_response_dict))
        self.assertEqual(len(cart), 1)

    def test_remove(self):
        """Test if item is correctly removed from cart and if correct
        response is returned based ob request type (AJAX).
        """
        cart = self.portal.restrictedTraverse('cart').cart

        # add some items ...
        self.item1.restrictedTraverse("add-to-cart").render()
        self.item2.restrictedTraverse("add-to-cart").render()
        self.item3.restrictedTraverse("add-to-cart").render()

        self.assertEqual(len(cart), 3)

        # remove item, normal request
        self.item1.restrictedTraverse("remove-from-cart").render()
        self.assertNotIn(self.item1.UID(), cart)
        self.assertEqual(len(cart), 2)

        # remove item, AJAX request
        self.portal.REQUEST["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"

        response_dict = {"status": STATUS.OK,
                         "body": None,
                         "err_info": None, }

        out = self.item3.restrictedTraverse("remove-from-cart").render()
        response_dict["body"] = 1
        self.assertEqual(out, json.dumps(response_dict))
        self.assertNotIn(self.item1.UID(), cart)
        self.assertEqual(len(cart), 1)

    def test_clear(self):
        """Test that cart is completely cleared."""

        self.portal.REQUEST['ACTUAL_URL'] = self.portal.REQUEST['URL']

        # clear an empty cart
        self.assertEqual(self.view.item_count(), 0)
        self.view.clear()
        self.assertEqual(self.view.item_count(), 0)

        # add some items ...
        self.item1.restrictedTraverse("add-to-cart").render()
        self.item2.restrictedTraverse("add-to-cart").render()
        self.item3.restrictedTraverse("add-to-cart").render()

        self.assertEqual(self.view.item_count(), 3)
        self.view.clear()
        self.assertEqual(self.view.item_count(), 0)

        self.item1.restrictedTraverse("add-to-cart").render()
        self.item2.restrictedTraverse("add-to-cart").render()
        self.item3.restrictedTraverse("add-to-cart").render()

        with self.disable_ajax():
            self.assertEqual(int(self.view.item_count()), 3)

        out = self.view.clear()
        self.assertEqual(out, None)

        with self.disable_ajax():
            self.assertEqual(int(self.view.item_count()), 0)


class TestCartTraversal(FunctionalTestCase):
    """Test traversing to @@cart and its methods/actions."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        # shortcuts
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.browser = Browser(self.portal)

        self.browser.addHeader('Authorization', 'Basic %s:%s' %
                               (TEST_USER_NAME, TEST_USER_PASSWORD,))

    def test_non_existent_action(self):
        """Test NotFound raised when traversing to a non-existent action."""
        # with plone.protect this does not show the 404 page but the CSRF
        # confirmation page
        try:
            import plone.protect
        except ImportError:
            with_protect = False
        else:
            plone.protect  # pyflakes
            with_protect = True

        if with_protect:
            self.browser.open('http://nohost/plone/@@cart/foo')
            self.assertIn('Verify you just performed an action',
                          self.browser.contents)
        else:
            with self.assertRaises(HTTPError):
                self.browser.open('http://nohost/plone/@@cart/foo')
                self.assertIn('This page does not seem to exist',
                              self.browser.contents)

    def test_traverse_to_method(self):
        """Test traversing to a @@cart method.

        Traversable methods are listed in ALLOWED_VIA_URL in cart.py.

        """
        self.browser.open('http://nohost/plone/@@cart/clear')
        self.assertIn('Cart cleared.', self.browser.contents)

        self.browser.open('http://nohost/plone/@@cart/item_count')
        self.assertEquals('', self.browser.contents)

    def test_traverse_to_action(self):
        """Test traversing to a ICartAction."""
        self.browser.open('http://nohost/plone/@@cart/delete')
        self.assertIn('You did not select any documents. Nothing was done.',
                      self.browser.contents)


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
