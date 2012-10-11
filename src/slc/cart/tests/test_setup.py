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


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
