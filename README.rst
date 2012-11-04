=============
slc.cart
=============

:Framework: `Plone 4.2 <http://plone.org>`_
:Bug tracker: https://github.com/syslabcom/slc.cart/issues
:Source: https://github.com/syslabcom/slc.cart
:Documentation:
:Code status:

    .. image:: http://travis-ci.org/niteoweb/slc.cart.png
       :align: left
       :target: http://travis-ci.org/niteoweb/slc.cart

.. topic:: Summary

    A module for batch processing the objects in Plone site. Objects can be
    added to cart and then various batch actions can be perfomed on them with
    a single click, such as download, delete and copy.



Installation
============

To install ``slc.cart`` ... TODO:


Basic usage
===========

After successful installation two changes immediately become visible:

* In site's ``portal_actions`` menu a link to Cart becomes available. This
  link also displays the current number of items in cart (in parentheses).

  .. image:: docs/images/portal_actions.png

* ``Add to Cart`` / ``Remove from Cart`` link appears in document byline of
  the objects, for which the link is applicable.

  .. image:: docs/images/document_byline.png

The link in ``portal_actions`` points to a new ``@@cart view``, which lists
the curent cart contents and provides links to various actions that can be
performed in batch on the items in cart.

.. image:: docs/images/cart_actions.png

List of Actions
---------------

``Copy``
  Add items in cart to clipboard. This is similar to Plone's `copy` operation
  with the advantage that the items (obejcts) being copied do not have to
  reside in the same container, they can be scattered all over the site.

``Cut``
  Very similar to `Copy` action, but items in cart are `cut` to clipboard
  instead. The difference becomes apparent on subsequent `Paste` operation -
  if the items have been cut, they will be removed from their original
  containers, while the copy operation would not touch the original object
  instances in their containers.

``Download``
  Download all items currently in cart (packed in a ZIP archive).

  NOTE: Only the items that are "downloadable" will be included in the
  archive. For example images, PDF documents and other files are all fine,
  while content types such as News Items and Folders will be skipped.

``Delete``
  Delete all items that are currently in cart from the portal. Also empty the
  cart iteslf along the way. Be careful though to not accidentally delete
  something you really didn't intend to.

``Clear Cart``
  This one is self-explanatory. Remove all items from cart so that it becomes
  empty, while not affecting the items themselves in any way.


Known Issues and TODOs
======================

* Localization support
* Testing in a production environment
