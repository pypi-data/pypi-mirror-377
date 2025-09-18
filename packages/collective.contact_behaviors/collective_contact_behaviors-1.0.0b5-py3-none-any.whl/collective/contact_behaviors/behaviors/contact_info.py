from collective.contact_behaviors import _
from plone.autoform.directives import read_permission
from plone.autoform.interfaces import IFormFieldProvider
from plone.schema.email import Email
from plone.supermodel import directives
from plone.supermodel import model
from zope import schema
from zope.interface import provider


PERMISSION = "collective.contact_behaviors.contact_info.view"


@provider(IFormFieldProvider)
class IContactInfo(model.Schema):
    directives.fieldset(
        "contact_info",
        label=_("label_contact_info", default="Contact Information"),
        fields=(
            "office_phone",
            "contact_phone",
            "fax",
            "contact_email",
            "contact_website",
        ),
    )

    read_permission(
        office_phone=PERMISSION,
        contact_phone=PERMISSION,
        fax=PERMISSION,
        contact_email=PERMISSION,
        contact_website=PERMISSION,
    )

    contact_phone = schema.TextLine(
        title=_("label_contact_phone", default="Mobile"),
        description=_(
            "description_contact_phone",
            default=("Internationalized mobile number with country code and area code"),
        ),
        required=False,
    )

    contact_email = Email(
        title=_("label_contact_email", default="E-mail"), required=False
    )

    contact_website = schema.URI(
        title=_("label_contact_website", default="Website"), required=False
    )

    office_phone = schema.TextLine(
        title=_("label_office_phone", default="Phone"),
        required=False,
    )

    fax = schema.TextLine(
        title=_("label_fax", default="Fax"),
        required=False,
    )
