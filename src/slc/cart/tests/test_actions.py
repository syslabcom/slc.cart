"""Testing the  Download cart."""

from plone import api
from slc.cart.tests.base import IntegrationTestCase
from zope.interface import alsoProvides

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
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        self.workflow = getToolByName(self.portal, "portal_workflow")
        self.cart_view = self.portal.unrestrictedTraverse('@@cart')
        self.member = self.portal.portal_membership.getAuthenticatedMember()

        # create test content # TODO: should have some files! not just documents
        # so that they get included in the zip and downloaded!
        self.item1 = api.content.create(
            container=self.portal, type='Document', id='item1')
        self.item2 = api.content.create(
            container=self.portal, type='Document', id='item2')
        self.item3 = api.content.create(
            container=self.portal, type='Document', id='item3')

    def test_delete(self):
        """Test if delete action correctly deletes all items present in
        cart (and nothing else) and also clears the cart itself.
        """
        # add some (but not all) items to cart
        self.item1.restrictedTraverse("add-to-cart").render()
        self.item3.restrictedTraverse("add-to-cart").render()

        self.assertEquals(self.cart_view.item_count(), 2)

        # now delete all items in cart and see what happens
        self.cart_view.action = 'delete'
        self.cart_view._run_action()

        # test that items 1 and 3 were indeed deleted, while item 2 was not
        self.assertIsNone(self.portal.get('item1'))
        self.assertIsNone(self.portal.get('item3'))
        self.assertIsNotNone(self.portal.get('item2'))

        # the cart itself should now be empty
        self.assertEquals(self.cart_view.item_count(), 0)

    def test_download(self):
        """TODO:
        """
        pass

    def test_copy(self):
        """TODO:
        """
        pass

    def test_cut(self):
        """TODO:
        """
        pass


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
