from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Anuncios(BrowserView):

    index = ViewPageTemplateFile("overrides/anuncio.pt")

    def getAnuncios(self):
        catalog = getToolByName(self, 'portal_catalog')
        results = catalog(portal_type='anuncio')
        print(results)
        return results

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
