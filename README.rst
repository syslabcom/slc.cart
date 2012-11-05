=======================================
Cart-like end-user support for batching
=======================================

An add-on for batch processing of objects in a Plone site. Objects can be added
to a "cart" and then various batch actions can be perfomed on them with a
single click, such as download, delete and copy.

* `Source code @ GitHub <http://github.com/syslabcom/slc.cart>`_
* `Releases @ PyPI <http://pypi.python.org/pypi/slc.cart>`_
* `Continuous Integration @ Travis-CI
  <http://travis-ci.org/syslabcom/slc.cart>`_


Installation
============

To install ``slc.cart`` you simply add ``slc.cart`` to the list of eggs in your
buildout, run buildout and restart Plone. Then, install `slc.cart` using the
Add-ons control panel.


Usage
=====

After successful installation two changes immediately become visible:

* In site's `Personal tools` menu a link to Cart becomes available. This link
  also displays the current number of items in cart (in parentheses).

  .. image:: https://github.com/syslabcom/slc.cart/raw/master/docs/images/portal_actions.png

* ``Add to Cart`` / ``Remove from Cart`` links appear in document byline of
  those objects, for which the link is applicable.

  .. image:: https://github.com/syslabcom/slc.cart/raw/master/docs/images/document_byline.png

The link in `Personal tools` menu points to a new ``@@cart`` view, which lists
the curent Cart contents and provides links to various actions that can be
performed in batch on all items in Cart.

.. image:: https://github.com/syslabcom/slc.cart/raw/master/docs/images/cart_actions.png


List of Actions
---------------

``Copy``
  Add items in cart to clipboard. This is similar to Plone's `copy` operation
  with the advantage that items (objects) being copied do not have to reside in
  the same container, they can be scattered all over the site.

``Cut``
  Very similar to `Copy` action, but items in cart are `cut` to clipboard
  instead. The difference becomes apparent on subsequent `Paste` operation -
  if the items have been cut, they will be removed from their original
  containers, while the copy operation would not touch the original object
  instances in their containers.

``Download``
  Download all items currently in cart (packed in a ZIP archive).

  NOTE: Only items that are "downloadable" will be included in the archive. For
  example images, PDF documents and other files are all fine, while content
  types such as News Items and Folders will be skipped.

``Delete``
  Delete all items that are currently in cart from the portal. Also empty the
  cart itself along the way. Be careful not to accidentally delete something
  you really didn't intend to.

``Clear Cart``
  This one is self-explanatory. Remove all items from cart so that it becomes
  empty, while not affecting items themselves in any way.


Providing a custom action
-------------------------

You can provide your own Cart action in your own package by creating an adapter
for ``ISiteRoot`` that provides the ``ICartAction`` interface. All actions
in `slc.cart` are already made this way so take them as a point of reference.


