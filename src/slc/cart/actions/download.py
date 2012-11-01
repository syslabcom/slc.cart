# -*- coding: utf-8 -*-
"""A Cart Action for downloading all items listed in cart as a ZIP file."""

from five import grok
from plone import api
from Products.CMFCore.interfaces import ISiteRoot
from slc.cart.interfaces import ICartAction
from StringIO import StringIO

import zipfile

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

                # make sure obj is a file by checking if filename is set
                filename = obj.getFilename()
                if not filename:
                    continue

                zf.writestr(filename, obj.data)
        finally:
            zf.close()

        request.response.setHeader(
            "Content-Type",
            "application/zip"
        )
        request.response.setHeader(
            'Content-Disposition',
            "attachment; filename=CartContents.zip"
        )
        return output.getvalue()
