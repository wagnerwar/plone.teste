# -*- coding: utf-8 -*-

from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collections import OrderedDict
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from collective.cover.tiles.configuration_view import IDefaultConfigureForm
from plone.app.uuid.utils import uuidToObject
from plone.directives import form
from plone.namedfile.field import NamedBlobImage as NamedImage
from plone.tiles.interfaces import ITileDataManager
from plone.tiles.interfaces import ITileType
from plone.uuid.interfaces import IUUID
from prodam.tiles import _
from zope import schema
from zope.component import queryUtility
from zope.schema import getFieldsInOrder
from Products.CMFPlone.utils import safe_unicode

class IAnuncioTile(IPersistentCoverTile, form.Schema):
    uuid = schema.TextLine(
        title=_(u'UUID'),
        readonly=True,
    )
    total = schema.List(
        title=_(u'Numero de itens para se exibir'),
        value_type=schema.TextLine(),
        required=False,
    )

    header = schema.TextLine(
        title=_(u'Header'),
        required=False,
    )
    form.omitted('description')
    form.no_omit(IDefaultConfigureForm, 'description')
    description = schema.Text(
        title=_(u'Description'),
        required=False,
    )

    form.omitted('title')
    form.no_omit(IDefaultConfigureForm, 'title')
    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

class AnuncioTile(PersistentCoverTile):
    index = ViewPageTemplateFile('templates/anunciotile.pt')

    def accepted_ct(self):
        """ Return a list of content types accepted by the tile.
        """
        return ['Collection']

    def populate_with_object(self, obj):
        super(AnuncioTile, self).populate_with_object(obj)  # check permission

        if obj.portal_type in self.accepted_ct():
            header = safe_unicode('Anuncio')  # use collection's title as header

            data_mgr = ITileDataManager(self)
            data_mgr.set({
                'header': header,
                'uuid': IUUID(obj)
            })

    def is_empty(self):
        return self.data.get('uuid', None) is None or \
            uuidToObject(self.data.get('uuid')) is None

    def show_header(self):
        return self._field_is_visible('header')


    def remove_relation(self):
        data_mgr = ITileDataManager(self)
        old_data = data_mgr.get()
        if 'uuid' in old_data:
            old_data.pop('uuid')
        data_mgr.set(old_data)

    def thumbnail(self, item):
        """Return a thumbnail of an image if the item has an image field and
        the field is visible in the tile.
        :param item: [required]
        :type item: content object
        """
        scale = 'large'  # we need the name only: 'mini'
        scales = item.restrictedTraverse('@@images')
        return scales.scale('image', scale)


    def results(self):
        self.configured_fields = self.get_configured_fields()
        size_conf = [i for i in self.configured_fields if i['id'] == 'total']
        size = size_conf


        uuid = self.data.get('uuid', None)
        obj = uuidToObject(uuid)
        print(obj.results(batch=False))
        if uuid and obj:
            results = obj.results(batch=False)
            return results
        else:
            self.remove_relation()
            return []
