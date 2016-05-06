from plone.app.layout.viewlets import common as base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api

class LogoViewlet(base.ViewletBase):
    index = ViewPageTemplateFile('browser/overrides/logo.pt')
    
    def getUrl(self):
        url = self.context.portal_url.getPortalObject().absolute_url()
        return url

class FooterViewlet(base.ViewletBase):
    index = ViewPageTemplateFile('browser/overrides/footer.pt')
    
    def getRecurso(self,caminho):
        return self.getPortal().restrictedTraverse(caminho)    

    def getPortal(self):
        return api.portal.get()

    def getWagnerRodape(self):
        api = self.getPortal()
        print(api['wagner-rodape'].objectIds())
        return api['wagner-rodape']

    def getPortalCatalog(self):
        return api.portal.get_tool(name='portal_catalog')       
