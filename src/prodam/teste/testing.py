# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import prodam.teste


class ProdamTesteLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=prodam.teste)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'prodam.teste:default')


PRODAM_TESTE_FIXTURE = ProdamTesteLayer()


PRODAM_TESTE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PRODAM_TESTE_FIXTURE,),
    name='ProdamTesteLayer:IntegrationTesting'
)


PRODAM_TESTE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PRODAM_TESTE_FIXTURE,),
    name='ProdamTesteLayer:FunctionalTesting'
)


PRODAM_TESTE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PRODAM_TESTE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='ProdamTesteLayer:AcceptanceTesting'
)
