from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

class Anuncios(BrowserView):

    index = ViewPageTemplateFile("overrides/anuncio.pt")

    def getAnuncios(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(portal_type='anuncio')
        print(results)
        return results

    def render(self):
        return self.index()


    def getImage(self,item):
        return  self.context.absolute_url_path()
        
    def __call__(self):
        return self.render()
