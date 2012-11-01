# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from plone import api
from slc.cart.tests.base import IntegrationTestCase

import unittest2 as unittest


class TestInstall(IntegrationTestCase):
    """Test installation of slc.cart into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

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

    # actions.xml
    def test_cart_actions_added(self):
        """Test if cart actions are added to user and document actions."""
        actions_tool = api.portal.get_tool('portal_actions')

        # Check if 'cart' has been added to user actions
        user_actions = actions_tool.user.listActions()
        self.assertEquals(len(user_actions), 9)

        ids = [a.getId() for a in user_actions]
        self.assertIn('cart', ids)

    # registry.xml
    def test_registry_records_added(self):
        """Test if registry records have been added."""
        limit = api.portal.get_registry_record('slc.cart.limit')

        self.assertEquals(limit, 100)


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
