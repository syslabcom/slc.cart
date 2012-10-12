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

    def _add_to_cart(self, uid):
        """A helper method to add item to cart."""
        self.portal.REQUEST["add"] = uid
        return self.view.add()

    def _remove_from_cart(self, uid):
        """A helper method to remove items from cart."""
        self.portal.REQUEST["remove"] = uid
        return self.view.remove()

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
            returned_obj = self.view._get_item_brain_by_UID(
                obj.UID()).getObject()
            self.assertEqual(obj, returned_obj)

        # raise NoResultError for non-existing UIDs
        from slc.cart.interfaces import NoResultError
        with self.assertRaises(NoResultError):
            self.view._get_item_brain_by_UID('non-existing-uid')
        self.assertRaises(
            NoResultError, self.view._get_item_brain_by_UID, '')

    def test_items(self):
        """Test returning list of brains (meta_data) of items in
        current member's cart.
        """

        # add some items to cart
        self.member.setMemberProperties({'cart': (
            self.item1.UID(),
            self.item2.UID(),
            self.item3.UID(),
        )})

        # test that correct amount of items are in cart
        self.assertEqual(len(self.view.items()), 3)

        # test that all items in cart are indeed Brain objects
        for type_of_object in [str(item.__class__)
                               for item in self.view.items()]:
            self.assertEquals(
                type_of_object, "<class 'Products.ZCatalog.Catalog.mybrains'>")

    def test_is_item_in_cart_ajax(self):
        """Test boolean method for AJAX calls."""
        self.portal.REQUEST["is-item-in-cart"] = self.item1.UID()
        self.portal.REQUEST["add"] = self.item1.UID()

        # test for a non-existing item
        self.assertEquals(self.view.is_item_in_cart(), 'false')

        # test for an existing item
        self._add_to_cart(self.item1.UID())
        self.assertEquals(self.view.is_item_in_cart(), 'true')

    def test_num_of_items(self):
        """Test len() method for AJAX calls."""
        self.assertEqual(int(self.view.num_of_items()), 0)

        self._add_to_cart(self.item1.UID())
        self.assertEqual(int(self.view.num_of_items()), 1)

        self._add_to_cart(self.item2.UID())
        self.assertEqual(int(self.view.num_of_items()), 2)

        self._remove_from_cart(self.item2.UID())
        self.assertEqual(int(self.view.num_of_items()), 1)

        # remove same item again, nothing should change
        self._remove_from_cart(self.item2.UID())
        self.assertEqual(int(self.view.num_of_items()), 1)

    def test_add(self):
        """Test if item is correctly added to cart and if correct response
        is returned based on request type.
        """
        self.assertEqual(len(self.view.items()), 0)

        # add item, normal request
        out = self._add_to_cart(self.item1.UID())
        self.assertEqual(len(self.view.items()), 1)
        self.assertTrue("Info" in out)

        # item already in cart
        out = self._add_to_cart(self.item1.UID())
        self.assertEqual(len(self.view.items()), 1)
        self.assertTrue("Error" in out)

        # add non-existent item, normal request
        out = self._add_to_cart("non-existent-uid")
        self.assertEqual(len(self.view.items()), 1)
        self.assertTrue("Error" in out)

    def test_add_ajax(self):
        """Test if item is correctly added to cart and if correct response
        is returned based on request type (with AJAX).
        """
        self.portal.REQUEST["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.assertEqual(len(self.view.items()), 0)

        # add an item, AJAX request
        out = self._add_to_cart(self.item1.UID())
        self.assertEqual(len(self.view.items()), 1)
        self.assertTrue(json.loads(out)['return_status'])

        # item already in cart, AJAX
        out = self._add_to_cart(self.item1.UID())
        self.assertEqual(len(self.view.items()), 1)
        self.assertFalse(json.loads(out)['return_status'])

        # add non-existent item, AJAX
        out = self._add_to_cart("non-existent-uid")
        self.assertEqual(len(self.view.items()), 1)
        self.assertFalse(json.loads(out)['return_status'])

    def test_remove(self):
        """Test if item is correctly removed from cart and if correct
        response is returned based ob request type (AJAX).
        """

        # first add some items to cart
        self.member.setMemberProperties({'cart': (
            self.item1.UID(),
            self.item2.UID(),
            self.item3.UID(),
        )})
        self.assertEqual(len(self.view.items()), 3)

        # remove item, normal request
        self.portal.REQUEST["remove"] = self.item1.UID()
        out = self.view.remove()
        self.assertEqual(len(self.view.items()), 2)
        self.assertTrue("Info" in out)

        # remove item, AJAX request
        self.portal.REQUEST["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.portal.REQUEST["remove"] = self.item2.UID()
        out = self.view.remove()
        self.assertEqual(len(self.view.items()), 1)
        self.assertTrue(json.loads(out)['return_status'])

        # try to remove non-existent item, AJAX request
        self.portal.REQUEST["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        self.portal.REQUEST["remove"] = "non-existent-uid"
        out = self.view.remove()
        self.assertEqual(len(self.view.items()), 1)
        self.assertFalse(json.loads(out)['return_status'])

        # try to remove non-existent item, normal request
        self.portal.REQUEST["HTTP_X_REQUESTED_WITH"] = ""
        out = self.view.remove()
        self.assertEqual(len(self.view.items()), 1)
        self.assertTrue("Error" in out)

    def test_clear(self):
        """Test that cart is completely cleared."""
        self.assertEqual(int(self.view.num_of_items()), 0)
        self.view.clear()
        self.assertEqual(int(self.view.num_of_items()), 0)

        self._add_to_cart(self.item1.UID())
        self._add_to_cart(self.item2.UID())
        self.assertEqual(int(self.view.num_of_items()), 2)

        self.view.clear()
        self.assertEqual(int(self.view.num_of_items()), 0)

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
