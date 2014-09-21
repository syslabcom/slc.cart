# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory

import pkg_resources

try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    HAS_DEXTERITYCONTENTTYPES = False
else:
    HAS_DEXTERITYCONTENTTYPES = True

_ = MessageFactory('slc.cart')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
