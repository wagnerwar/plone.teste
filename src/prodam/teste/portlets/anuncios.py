# -*- coding: utf-8 -*-

from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from zope.interface import implements
from twitter import Api
from Products.CMFCore.utils import getToolByName

class IAnuncios(IPortletDataProvider):
    header = schema.TextLine(
        title=_(u'Portlet header'),
        description=_(u'Title of the rendered portlet'),
        required=True)

    count = schema.TextLine(
        title=_(u'Numero de itens para exibir'),
        description=_(u'Numero de anuncios para exibir'),
        required=True)

class Assignment(base.Assignment):
    implements(IAnuncios)

    def __init__(self, header=u'', count=1):
        self.header = header
        self.count = count

    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return 'Anuncios'

class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/anuncios.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return True

    def getTitle(self):
        if self.data.header:
            return self.data.header
        else:
            return 'Anuncios'

    def getAnuncios(self):
        count = self.data.count
        catalog = getToolByName(self.context, 'portal_catalog') 
        dados = catalog.searchResults({'portal_type': 'anuncio','review_state': 'published','sort_on': 'modified','limit': count})
        if(dados):
            return dados
        else:
            return False

class AddForm(base.AddForm):
    form_fields = form.Fields(IAnuncios)
    label = _(u'Adicionar portlets de anuncio')
    description = _(u'Adicionando portlet de anuncio')

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IAnuncios)
    label = _(u'Editando portlets de anuncios')
    description = _(u'Editando portlets de anuncio')
