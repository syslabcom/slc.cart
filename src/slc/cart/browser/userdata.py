"""Components for personal information and preferences."""

from slc.cart import _
from plone.app.users.browser.personalpreferences import UserDataConfiglet
from plone.app.users.browser.personalpreferences import UserDataPanelAdapter
from plone.app.users.userdataschema import IUserDataSchema
from plone.app.users.userdataschema import IUserDataSchemaProvider
from zope import schema
from zope.formlib.widget import DisplayWidget
from zope.interface import implements


class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        """Return our custom userdata schema."""
        return ISlcCartUserDataSchema


class ISlcCartUserDataSchema(IUserDataSchema):
    """ Use all the fields from the default user data schema, and add various
    extra fields.
    """
    cart = schema.Tuple(
        title=_(u'label_car', default=u'Cart'),
    )


class SlcCartUserDataPanelAdapter(UserDataPanelAdapter):
    """Makes the custom user data fields available in the personal
    information view.
    """
    def get_cart(self):
        return self.context.getProperty('cart', ())

    def set_cart(self, value):
        return self.context.setMemberProperties({'cart': value})
    cart = property(get_cart, set_cart)


class UIDsListDisplayWidget(DisplayWidget):

    def __call__(self):
        """A custom widget for displaying Tuples in a simple list."""
        result = '<ul>'
        view = self.context.context
        for item in self.context.get(view):
            result += ('<li><a href="resolveuid/%s/view">%s</a></li>'
                       % (item, item))
        result += '</ul>'
        return result


class SlcCartUserDataConfiglet(UserDataConfiglet):
    """Customize @@user-information view."""

    def __call__(self):
        # Tuple fields don't have Widgets so we have to use our own
        self.form_fields['cart'].custom_widget = UIDsListDisplayWidget
        self.form_fields['cart'].for_display = True

        return super(SlcCartUserDataConfiglet, self).__call__()
