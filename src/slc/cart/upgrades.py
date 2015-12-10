from plone import api
from slc.cart.browser.cart import CartSet
from zope.annotation.interfaces import IAnnotations
import logging

log = logging.getLogger(__name__)


def migrate_to_cartset(context):
    for user in api.user.get_users():
        annotations = IAnnotations(user)
        old_cart = annotations.get('cart', None)
        if old_cart is not None:
            try:
                annotations['cart'] = CartSet(old_cart)
            except:
                log.info('Discarding broken old cart: ' + str(old_cart))
                annotations['cart'] = CartSet()
            log.info('Migrated cart for ' + user.id)
