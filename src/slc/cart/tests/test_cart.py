"""Testing the  Download cart."""

from plone import api
from Products.CMFCore.utils import getToolByName
from slc.cart.tests.base import IntegrationTestCase
#from StringIO import StringIO
from zope.interface import alsoProvides

import json
import unittest2 as unittest
#import zipfile


class TestCart(IntegrationTestCase):
    """ Test Cart BrowserView related stuff. """

    def setUp(self):
        """Custom shared utility setup for tests."""
        # prepare the request object
        from slc.cart.interfaces import ISlcCartLayer
        alsoProvides(self.layer['app'].REQUEST, ISlcCartLayer)

        # shortcuts
        self.portal = self.layer['portal']
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        self.workflow = getToolByName(self.portal, "portal_workflow")
        self.view = self.portal.unrestrictedTraverse('@@cart')
        self.member = self.portal.portal_membership.getAuthenticatedMember()

        # create test content
        self.item1 = api.content.create(
            container=self.portal, type='Document', id='item1')
        self.item2 = api.content.create(
            container=self.portal, type='Document', id='item2')
        self.item3 = api.content.create(
            container=self.portal, type='Document', id='item3')

    #def _add_to_cart(self, uid):
        #"""A helper method to add item to cart."""
        #self.portal.REQUEST["add"] = uid
        #return self.view.add()

    #def _remove_from_cart(self, uid):
        #"""A helper method to remove items from cart."""
        #self.portal.REQUEST["remove"] = uid
        #return self.view.remove()

    def test_browser_view_exists(self):
        """Test if @@cart browser view is registered and visible."""
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
        self.assertEqual(len(self.view.items()), 3)

        # test that all items in cart are indeed Brain objects
        for type_of_object in [str(item.__class__)
                               for item in self.view.items()]:
            self.assertEquals(
                type_of_object, "<class 'Products.ZCatalog.Catalog.mybrains'>")

    def test_is_item_in_cart_ajax(self):
        """Test boolean method for AJAX calls."""
        self.portal.REQUEST["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"

        # test for a non-existing item
        out = self.item1.restrictedTraverse("is-in-cart").render()
        self.assertEquals(out, 'false')

        # test for an existing item
        self.item1.restrictedTraverse("add-to-cart").render()
        out = self.item1.restrictedTraverse("is-in-cart").render()
        self.assertEquals(out, 'true')

    def test_item_count(self):
        """Test len() method for AJAX calls."""
        self.assertEqual(int(self.view.item_count()), 0)

        self.item1.restrictedTraverse("add-to-cart").render()
        self.assertEqual(int(self.view.item_count()), 1)

        self.item2.restrictedTraverse("add-to-cart").render()
        self.assertEqual(int(self.view.item_count()), 2)

        self.item2.restrictedTraverse("remove-from-cart").render()
        self.assertEqual(int(self.view.item_count()), 1)

        # remove same item again, nothing should change
        self.item2.restrictedTraverse("remove-from-cart").render()
        self.assertEqual(int(self.view.item_count()), 1)

    def test_add(self):
        """Test if item is correctly added to the cart.
        """
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
        from slc.cart.browser.cart import STATUS

        self.portal.REQUEST["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        cart = self.portal.restrictedTraverse('cart').cart
        self.assertEqual(len(cart), 0)

        # add new item
        out = self.item1.restrictedTraverse("add-to-cart").render()
        self.assertIn(self.item1.UID(), cart)
        self.assertEqual(len(cart), 1)
        self.assertEqual(out, str(STATUS.OK))

        # add another item
        out = self.item2.restrictedTraverse("add-to-cart").render()
        self.assertIn(self.item2.UID(), cart)
        self.assertEqual(len(cart), 2)
        self.assertEqual(out, str(STATUS.OK))

        # add an item that already exists (nothing should change and
        # no error should be raised)
        out = self.portal.item1.restrictedTraverse("add-to-cart").render()
        self.assertIn(self.item1.UID(), cart)
        self.assertEqual(len(cart), 2)
        self.assertEqual(out, str(STATUS.OK))

    def test_remove(self):
        """Test if item is correctly removed from cart and if correct
        response is returned based ob request type (AJAX).
        """
        from slc.cart.browser.cart import STATUS

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
        out = self.item3.restrictedTraverse("remove-from-cart").render()
        self.assertEqual(out, str(STATUS.OK))
        self.assertNotIn(self.item1.UID(), cart)
        self.assertEqual(len(cart), 1)

    def test_clear(self):
        """Test that cart is completely cleared."""

        from slc.cart.browser.cart import STATUS

        cart = self.portal.restrictedTraverse('cart').cart

        # clear an empty cart
        self.assertEqual(len(cart), 0)
        self.view.clear()
        self.assertEqual(len(cart), 0)

        # add some items ...
        self.item1.restrictedTraverse("add-to-cart").render()
        self.item2.restrictedTraverse("add-to-cart").render()
        self.item3.restrictedTraverse("add-to-cart").render()

        self.assertEqual(len(cart), 3)
        self.view.clear()
        self.assertEqual(len(cart), 0)

        # test clear AJAX
        self.item1.restrictedTraverse("add-to-cart").render()
        self.item2.restrictedTraverse("add-to-cart").render()
        self.item3.restrictedTraverse("add-to-cart").render()

        self.portal.REQUEST["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.assertEqual(self.view.item_count(), 3)
        out = self.view.clear()
        self.assertEqual(out, str(STATUS.OK))
        self.assertEqual(self.view.item_count(), 0)

    #def test_download(self):
    #    """Test ZIP archiving a batch of items in cart."""

    #    # Try downloading with an empty cart
    #    output = self.view.download()
    #    self.assertTrue("Error" in output)

    #    # Now add an item to the cart
    #    self._add_to_cart(self.item1.UID())
    #    output = self.view.download()
    #    self.assertEqual(
    #        self.view.request.response['content-type'], "application/zip")
    #    self.assertTrue(
    #        "Cart" in self.view.request.response['content-disposition'])

    #    zf = zipfile.ZipFile(StringIO(output))
    #    self.assertEqual(len(zf.namelist()), 1)


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
