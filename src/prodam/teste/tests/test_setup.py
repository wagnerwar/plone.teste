# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from prodam.teste.testing import PRODAM_TESTE_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that prodam.teste is properly installed."""

    layer = PRODAM_TESTE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if prodam.teste is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'prodam.teste'))

    def test_browserlayer(self):
        """Test that IProdamTesteLayer is registered."""
        from prodam.teste.interfaces import (
            IProdamTesteLayer)
        from plone.browserlayer import utils
        self.assertIn(IProdamTesteLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = PRODAM_TESTE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['prodam.teste'])

    def test_product_uninstalled(self):
        """Test if prodam.teste is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'prodam.teste'))
