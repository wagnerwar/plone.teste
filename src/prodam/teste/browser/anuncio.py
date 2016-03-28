from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

class Anuncios(BrowserView):

    index = ViewPageTemplateFile("overrides/anuncio.pt")

    def getAnuncios(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(portal_type='anuncio')
        return results

    def render(self):
        return self.index()

    def thumbnail(self, item):
        """Return a thumbnail of an image if the item has an image field and
        the field is visible in the tile.
        :param item: [required]
        :type item: content object
        """
        scale = 'large'  # we need the name only: 'mini'
        scales = item.restrictedTraverse('@@images')
        return scales.scale('image', scale)
        
    def __call__(self):
        return self.render()
