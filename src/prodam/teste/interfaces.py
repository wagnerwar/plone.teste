# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.interfaces import IViewletManager

class IProdamTesteLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class ILogoViewletManager(IViewletManager):
    """Viewlet de logo"""

class IFooterViewletManager(IViewletManager):
    """Viewlet do rodape"""
