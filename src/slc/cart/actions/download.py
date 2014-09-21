# -*- coding: utf-8 -*-
"""A Cart Action for downloading all items listed in cart as a ZIP file."""

from five import grok
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from slc.cart import HAS_DEXTERITYCONTENTTYPES
from slc.cart.interfaces import ICartAction
from StringIO import StringIO

import zipfile

if HAS_DEXTERITYCONTENTTYPES:
    from plone.app.contenttypes.interfaces import IFile
    from plone.app.contenttypes.interfaces import IImage
else:
    from zope.interface import Interface

    class IFile(Interface):
        pass

    class IImage(Interface):
        pass


NAME = 'download'
TITLE = u'Download'
WEIGHT = 10


class DownloadAction(grok.Adapter):
    """Download Action implementation for downloading items listed in cart."""
    grok.context(ISiteRoot)
    grok.provides(ICartAction)
    grok.name(NAME)

    name = NAME
    title = TITLE
    weight = WEIGHT

    def run(self):
        """Download cart content.

        Before downloading items are packed into a zip archive (only the
        items that are files are included).

        """
        cart_view = self.context.restrictedTraverse('cart')
        request = self.context.REQUEST
        cart = cart_view.cart

        if not cart:
            api.portal.show_message(
                message=u"Can't download, no items found.",
                request=request,
                type="error"
            )
            request.response.redirect(self.context.absolute_url() + '/@@cart')

        output = StringIO()
        zf = zipfile.ZipFile(output, mode='w')

        try:
            for obj_uuid in cart:
                # make sure obj exists
                obj = api.content.get(UID=obj_uuid)
                if obj is None:
                    continue

                if IFile.providedBy(obj):
                    filename = obj.file.filename
                    data = obj.file.data
                elif IImage.providedBy(obj):
                    filename = obj.image.filename
                    data = obj.image.data
                else:
                    # make sure obj is a file by checking if filename is set
                    filename = obj.getFilename()
                    if not filename:
                        continue
                    data = obj.data

                zf.writestr(filename, data)
        finally:
            zf.close()

        if zf.filelist:
            request.response.setHeader(
                "Content-Type",
                "application/zip"
            )
            request.response.setHeader(
                'Content-Disposition',
                "attachment; filename=download.zip"
            )
            return output.getvalue()
        else:
            api.portal.show_message(
                message="There are no downloadable items in your cart.",
                request=request,
                type="warning")
            portal = api.portal.get()
            request.response.redirect(portal.absolute_url() + '/@@cart')
