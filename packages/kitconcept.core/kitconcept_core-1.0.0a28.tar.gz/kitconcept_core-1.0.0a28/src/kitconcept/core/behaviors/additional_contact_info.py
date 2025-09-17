from kitconcept.core import _
from plone.autoform.directives import read_permission
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import directives
from plone.supermodel import model
from zope import schema
from zope.interface import provider


PERMISSION = "kitconcept.core.behaviors.additional_contact_info.view"


@provider(IFormFieldProvider)
class IAdditionalContactInfo(model.Schema):
    read_permission(contact_building=PERMISSION, contact_room=PERMISSION)

    contact_building = schema.TextLine(
        title=_("label_contact_building", default="Building"),
        required=False,
    )

    contact_room = schema.TextLine(
        title=_("label_contact_room", default="Room"), required=False
    )

    address = schema.Text(
        title=_("label_address", default="Address"),
        required=False,
    )

    office_phone = schema.TextLine(
        title=_("label_office_phone", default="Office Phone"),
        required=False,
    )

    fax = schema.TextLine(
        title=_("label_fax", default="Fax"),
        required=False,
    )

    directives.fieldset(
        "contact_location",
        label=_(
            "label_contact_location",
            default="Location",
        ),
        fields=("contact_building", "contact_room", "address"),
    )
    directives.fieldset(
        "contact_info",
        label=_(
            "label_contact_info",
            default="Contact Information",
        ),
        fields=("office_phone", "fax"),
    )
