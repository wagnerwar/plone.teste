from plone.autoform.interfaces import IFormFieldProvider
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope.interface import provider


@provider(IFormFieldProvider)
class IBNoticia(model.Schema):
    """Behavior interface to make a type support related items.
    """

    bnoticias = RelationList(
        title=u"Noticias relacionadas",
        default=[],
        value_type=RelationChoice(title=u"Noticias acerca do anuncio", source=ObjPathSourceBinder(portal_type='anuncio')),
        required=False,)
