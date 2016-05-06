# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from zope.interface import implements
from plone import namedfile
class INoticias(IPortletDataProvider):
    header = schema.TextLine(
        title=_(u'Portlet header'),
        description=_(u'Title of the rendered portlet'),
        required=True)
    
    show_news = schema.Bool(
        title=_(u'Show portlet header'),
        description=_(u''),
        required=True,
        default=False)
    
    count = schema.TextLine(
        title=_(u'Count elements'),
        description=_(u'Count of the news'),
        required=True)

    footer_text = schema.TextLine(
        title=_(u'Footer text'),
        description=_(u'Title of the footer portlet'),
        required=True)

    footer_link = schema.TextLine(
        title=_(u'Footer link'),
        description=_(u'Link of the footer portlet'),
        required=True)


class Assignment(base.Assignment):

    implements(INoticias)

    def __init__(self, header=u'', show_news=False, count=4, footer_text='',footer_link='/Prefeitura/noticia'):
        self.header = header
        self.show_news = show_news
        self.count = count
        self.footer_text = footer_text
        self.footer_link = footer_link

    @property
    def title(self):
        if self.header:
            return self.header
        else:
            return 'WAWA News'


class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/noticias.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def render(self):
        return self._template()

    def getTitle(self):
        if self.data.header:
            return self.data.header
        else:
            return 'Wawa New'

    @property
    def getFooterText(self):
        return self.data.footer_text

    @property
    def getFooterLink(self):
        return self.data.footer_link


    @property
    def getShowNews(self):
        return self.data.show_news

    @property
    def getNews(self):
        count = self.data.count
        portal_catalog = getToolByName(self, 'portal_catalog')
        news = portal_catalog(portal_type='News Item',review_state='published',sort_limit=int(count))
        return news


    def getImage(self,noticia):
        print(isinstance(noticia.image,namedfile.NamedBlobImage))
        if(isinstance(noticia.image,namedfile.NamedBlobImage)):
            return noticia.absolute_url()+'/@@images/image/thumb'
        else:
            return 'testa'

class AddForm(base.AddForm):
    form_fields = form.Fields(INoticias)
    label = _(u'Add Portlet News')
    description = _(u'Add Portlet News.')

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(INoticias)
    label = _(u'Edit portlet news')
    description = _(u'Edit Portlet News')
