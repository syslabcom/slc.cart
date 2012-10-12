# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from slc.cart.tests.base import IntegrationTestCase
from Products.CMFCore.utils import getToolByName

import unittest2 as unittest


class TestInstall(IntegrationTestCase):
    """Test installation of slc.cart into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = getToolByName(self.portal, 'portal_quickinstaller')

    def test_product_installed(self):
        """Test if slc.cart is installed with portal_quickinstaller."""
        self.failUnless(self.installer.isProductInstalled('slc.cart'))

    def test_uninstall(self):
        """Test if slc.cart is cleanly uninstalled."""
        self.installer.uninstallProducts(['slc.cart'])
        self.failIf(self.installer.isProductInstalled('slc.cart'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ISlcCartLayer is registered."""
        from slc.cart.interfaces import ISlcCartLayer
        from plone.browserlayer import utils
        self.failUnless(ISlcCartLayer in utils.registered_layers())

    # jsregistry.xml
    def test_js_registered(self):
        """Test if JavaScript files are registered with portal_javascript."""
        resources = self.portal.portal_javascripts.getResources()
        ids = [r.getId() for r in resources]

        self.assertIn('++resource++slc.cart/cart.js', ids)

    # jsregistry.xml
    def test_ajaxified_search_results_disabled(self):
        """By default, plone.app.search reloads search results with AJAX. This
        means that our custom jQuery code that runs on document.ready does not
        work on subsequent searches. This test checks that AJAX loading of
        search results is disabled, to make our custom code work.
        """
        resources = self.portal.portal_javascripts.getResources()
        search_js = [r for r in resources
                     if r.getId() == '++resource++search.js'][0]
        self.assertFalse(search_js.getEnabled())

    # memberdata_properties.xml
    def test_fields_added_to_member(self):
        """Test that extra fields are added to member properties."""
        memberdata = self.portal.portal_memberdata

        self.assertTrue(hasattr(memberdata, 'cart'))
        self.assertEquals(
            str(memberdata.getProperty('cart').__class__), "<type 'tuple'>")

    # actions.xml
    def test_cart_action_added(self):
        """Test if cart action is added to user actions."""
        actions_tool = getToolByName(self.portal, 'portal_actions')

        actions = actions_tool.user.listActions()
        self.assertEquals(len(actions), 9)

        titles = [a.title for a in actions]
        self.assertIn('Cart', titles)


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
