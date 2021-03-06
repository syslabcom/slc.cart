# -*- coding: utf-8 -*-
"""A Cart Action for downloading all items listed in cart as a ZIP file."""

from Products.ATContentTypes.interfaces.interfaces import IATContentType
from Products.CMFCore.interfaces import ISiteRoot
from StringIO import StringIO
from datetime import datetime
from five import grok
from plone import api
from slc.cart.interfaces import ICartAction

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

                # check if this is a document and potentially has a pdf set
                if obj.portal_type == "Document" and obj.restrictedTraverse('pdf', None):
                    data = obj.restrictedTraverse('pdf')()
                    if obj.REQUEST.response.status != 200:
                        if obj.REQUEST.response.status == 302:
                            del obj.REQUEST.response.headers['location']
                        obj.REQUEST.response.status = 200
                        # ignore and continue - showing a portal message here is
                        # useless as we probably won't return html
                        continue
                    data = data.read()
                    filename = '%s.pdf' % obj.getId()
                else:
                    # make sure obj is a file by checking if filename is set
                    if IATContentType.providedBy(obj):
                        filename = obj.getFilename()
                        if not filename:
                            continue
                        data = obj.data
                    else:
                        blobfile = obj.file
                        filename = blobfile.filename
                        data = blobfile.data

                zf.writestr(filename, data)
        finally:
            zf.close()

        if zf.filelist:
            request.response.setHeader(
                "Content-Type",
                "application/zip"
            )
            now = datetime.now()
            zipfilename = "download-%s-%s-%s.zip" % (now.year, now.month, now.day)
            request.response.setHeader(
                'Content-Disposition',
                "attachment; filename=%s" % zipfilename
            )
            return output.getvalue()
        else:
            api.portal.show_message(
                message="There are no downloadable items in your cart.",
                request=request,
                type="warning")
            portal = api.portal.get()
            request.response.redirect(portal.absolute_url() + '/@@cart')
