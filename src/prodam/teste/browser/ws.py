# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import socket
import traceback
import sys
from Products.Five import BrowserView
from plone import api
from StringIO import StringIO
from bs4 import BeautifulSoup
from cookielib import CookieJar
from gzip import GzipFile
from plone.memoize import ram
from time import localtime
from time import time
from twitter import Api
from urllib import urlencode
from urllib2 import HTTPCookieProcessor
from urllib2 import HTTPError
from urllib2 import ProxyHandler
from urllib2 import Request
from urllib2 import build_opener
try:
    import cPickle as pickle
except ImportError:
    import pickle


url_direct = {'r7': 'http://esportes.r7.com/automobilismo/feed.xml'}


class StringCookieJar(CookieJar):
    def __init__(self, string=None, policy=None):
        CookieJar.__init__(self, policy)
        if string:
            self._cookies = pickle.loads(string)


class WawaWs(BrowserView):
    """
    return: content to site url_direct
    """
    soup = None
    tree = None

    def __init__(self, context, request, state=None, proxy=None, max_retries=3):
        """Classe para fazer scrap class spagora args:
        @state: Estado de scrapper anterior obtido via .get_state()
        @proxy: Proxy HTTP
        """
        self.context = context
        self.request = request
        self.max_retries = max_retries
        if state:
            self._form_data = state['form_data']
            self._cj = StringCookieJar(state['cookies'])
        else:
            self._cj = StringCookieJar()

        cookie_handler = HTTPCookieProcessor(self._cj)
        if proxy is None:
            self._opener = build_opener(cookie_handler)
        else:
            proxy_handler = ProxyHandler({'http': proxy, })
            self._opener = build_opener(cookie_handler, proxy_handler)



    """
    ##########################################################################
                           Manipulação de títulos
    ##########################################################################
    """

    def getContent(self, url, data=None, referer=None):
        """
        return content cookie html in response decode utf-8 to BeautifulSoup
        """
        encoded_data = urlencode(data) if data else None
        # if referer is None: url
        default_headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.2.9) Gecko/20100824 Firefox/3.6.9 ( .NET CLR 3.5.30729; .NET4.0E)',
                           'Accept-Language': 'pt-br;q=0.5',
                           'Accept-Charset': 'utf-8;q=0.7,*;q=0.7',
                           'Accept-Encoding': 'gzip',
                           'Connection': 'close',
                           'Cache-Control': 'no-cache',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Referer': referer}
        req = Request(url, encoded_data, default_headers, origin_req_host=referer)

        retries = 0
        response = None
        while True:
            try:
                handle = self._opener.open(req, timeout=30)
                if handle.info().get('Content-Encoding') == 'gzip':
                    data = handle.read()
                    buf = StringIO(data)
                    f = GzipFile(fileobj=buf)
                    response = f.read()
                else:
                    response = handle.read()
                break
            except HTTPError, e:
                retries = retries + 1
                print "%d Tentativas na url: %s, erro: %s" % (retries, url, e.getcode())
                if retries > self.max_retries:
                    break
            except socket.timeout:
                retries = retries + 1
                print "%d Time out: %s, erro: %s" % (retries, url, e.getcode())
                if retries > self.max_retries:
                    break

        if response:
            return response
        else:
            return False
    def listaNewsR7(self):
        content = []
        self.soup = BeautifulSoup(self.getContent(url_direct.get("r7")))
        noticias = self.soup.find_all('title')
        for noticy in noticias:
            tipo = noticy.get('type','zero')
            if(tipo == 'html'):
                content.append(noticy.string)
        return content
    
    
        
