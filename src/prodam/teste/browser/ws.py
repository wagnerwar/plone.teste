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

    # def showDetails(self):
    #     try:
    #         requested = self.request.form['id']
    #         text = ''
    #         if requested == "ex-clima":
    #             text = self.getWeatherSp()
    #         if requested == "ex-ar":
    #             text = self.getAirQuality()
    #         if requested == "ex-aero":
    #             text = self.getAirportFlights()
    #         if requested == "ex-publico":
    #             text = self.getMeansOfTransportation()
    #         if requested == "ex-transito":
    #             text = self.getTraffic()
    #         if requested == "ex-rodizio":
    #             text = self.getCarRotation()
    #     except:
    #         text = False
    #     return text


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
            print(noticy)
            if(noticy['type'] == 'html'):
                content.append(noticy.string.extract())
            print(content)
        return content
    
    
        
        return content
    def WeatherCapa(self):
        content = ""
        try:
            self.soup = BeautifulSoup(self.getContent(url_direct.get("ex-clima-media")))
            temp_media = self.getTempMedia()
            hour = localtime(time()).tm_hour
            self.soup = BeautifulSoup(self.getContent(url_direct.get("ex-clima")))
            dia = self.soup.findAll('dia')
            potencial = dia[0].parent.find('ct', {'periodo': self.getPeriod(hour)})

            propertyTitle, propertyTexto = self.getPainel(int(1))
            if propertyTitle:
                titulo = propertyTitle
            else:
                titulo = "Tempo"

            if propertyTexto:
                texto = propertyTexto
            else:
                texto = """
                         <div class="tempo-g nb"></div>
                         <div class="t-media"><span>Média</span><span id="CGE-media" class="amarelo bold">%(temp_media)s°</span></div>
                         <div class="tempestade">
                         <span>Potencial <div class="raio"></div></span>
                         <span id="status-temp" class="amarelo">%(potencial)s</span>
                         </div>
                         </div>
                         <div class="ex-hover"><a href="#verMais"></a><div></div>
                        """ % {'temp_media': temp_media, 'potencial': str(potencial['pt'])}

            content += """
                       <li class="ex-clima ver-mais">
                       <div class="dash-border">
                       <strong class="titulo-dash">%(titulo)s</strong>
                       %(texto)s </div>
                       </li>
                       """ % {'titulo': titulo, 'texto': texto}

        except:
            content += self.getContentExcept(class_li='ex-clima', text_div='Tempo')
        return content

    def airQualityCapa(self):
        content = ""
        try:
            self.soup = BeautifulSoup(self.getContent(url_direct.get('qualidade-oxigenio')))
            qualidade_ar = self.getDescQualidade()

            propertyTitle, propertyTexto = self.getPainel(int(2))
            if propertyTitle:
                titulo = propertyTitle
            else:
                titulo = "Qualidade do Ar"

            if propertyTexto:
                texto = propertyTexto
            else:
                texto = """
                        <div class="dash-img o2quali"></div>
                        <b class="bullet-verde em2">%(qualidade_ar)s</b>
                        </div>
                        <div class="ex-hover"><a href="#verMais"></a><div></div>
                        """ % {'qualidade_ar': qualidade_ar}

            content += """
                       <li class="ex-ar ver-mais">
                       <div class="dash-border">
                       <strong class="titulo-dash">%(titulo)s</strong>
                       %(texto)s </div>
                       </li>
                       """ % {'titulo': titulo, 'texto': texto}
        except:
            content += self.getContentExcept(class_li='ex-ar', text_div='Qualidade do Ar')
        return content

    def trafficCapa(self):
        content = ""
        try:
            self.soup = BeautifulSoup(self.getContent(url_direct.get('transito-agora')))

            total_km_lentidao = self.soup.find('div', {"id": 'lentidao'}).string

            result = self.getTrafficCount(total_km_lentidao)

            propertyTitle, propertyTexto = self.getPainel(int(5))
            if propertyTitle:
                titulo = propertyTitle
            else:
                titulo = "Trânsito"

            if propertyTexto:
                texto = propertyTexto
            else:
                texto = """
                        <div class="dash-img semaforo"></div>
                        <div class="tran-total">
                        <div class="ttotal"><span class="amarelo em14 bold">%(total_km_lentidao)skm</span><br>
                        <small class="bold em09">de lentidão</small></div>
                        <span class="kmStatus %(css)s"><i class="ball-status %(css)s"></i>%(status_transito_sp)s</span>
                        </div></div>
                        <div class="ex-hover"><a href="#verMais"></a><div></div>
                        """ % {'total_km_lentidao': total_km_lentidao, 'status_transito_sp': result[1], 'css': result[0]}

            content += """
                       <li class="ex-transito ver-mais">
                       <div class="dash-border">
                       <strong class="titulo-dash">%(titulo)s</strong>
                       %(texto)s </div>
                       </li>
                       """ % {'titulo': titulo, 'texto': texto}
        except:
            content += self.getContentExcept(class_li='ex-transito', text_div='Trânsito')
        return content

    """
    ##########################################################################
                           Página inicial - São Paulo Agora (capa)
    ##########################################################################
    """

    @ram.cache(lambda *args: time() // (60 * 5))
    def getCapa(self):
        content = ""

        content += self.WeatherCapa()

        content += self.airQualityCapa()

        propertyTitle, propertyTexto = self.getPainel(int(3))
        if propertyTitle:
            titulo = propertyTitle
        else:
            titulo = "Aeroportos"

        if propertyTexto:
            texto = propertyTexto
        else:
            texto = """
                    <div class="dash-img"></div>
                    <span id="aero-status">Consulte situação</span>
                    </div>
                    <div class="ex-hover"><a href="#verMais"></a><div></div>
                    """

        content += """
                   <li class="ex-aero ver-mais">
                   <div class="dash-border">
                   <strong class="titulo-dash">%(titulo)s</strong>
                   %(texto)s </div>
                   </li>
                   """ % {'titulo': titulo, 'texto': texto}

        propertyTitle, propertyTexto = self.getPainel(int(4))
        if propertyTitle:
            titulo = propertyTitle
        else:
            titulo = "Transporte Público"

        if propertyTexto:
            texto = propertyTexto
        else:
            texto = """
                    <div class="dash-img"></div>
                    <a href="http://www.sptrans.com.br/itinerarios/" target="_blank" class="azul-pq">Busca de itinerários</a>
                    </div>
                    <div class="ex-hover"><a href="#verMais"></a><div></div>
                    """

        content += """
                   <li class="ex-publico ver-mais">
                   <div class="dash-border">
                   <strong class="titulo-dash">%(titulo)s</strong>
                   %(texto)s </div>
                   </li>
                   """ % {'titulo': titulo, 'texto': texto}

        content += self.trafficCapa()

        try:
            url_rodizio = url_direct.get('dash-rodizio')
            placas_final_url_return = urllib.urlopen(url_rodizio)
            data_result = json.loads(placas_final_url_return.read())
            placa = data_result['Rotation']['desc']

            propertyTitle, propertyTexto = self.getPainel(int(6))
            if propertyTitle:
                titulo = propertyTitle
            else:
                titulo = "Rodízio"

            if propertyTexto:
                texto = propertyTexto
            else:
                texto = """
                       <div class="dash-img"></div>
                       <ul class="rod-3col">
                       <li><span class="em08 bold"><small>Placas final:</small></span><br><span class="azul-pq em15">%(placa)s</span></li>
                       </ul></div>
                       <div class="ex-hover"><a href="#verMais"></a><div></div>
                        """ % {'placa': placa}

            content += """
                       <li class="ex-rodizio ver-mais">
                       <div class="dash-border">
                       <strong class="titulo-dash">%(titulo)s</strong>
                       %(texto)s </div>
                       </li>
                       """ % {'titulo': titulo, 'texto': texto}
        except KeyError, e:
            print e
            content += self.getContentExcept(class_li='ex-rodizio', text_div='Rodizio')
        except:
            content += self.getContentExcept(class_li='ex-rodizio', text_div='Rodizio')
        return content

    """
    ##########################################################################
                           Helpers
    ##########################################################################
    """
    @ram.cache(lambda *args: time() // (60 * 15))
    def getTempMedia(self):
        """
        return temperature median in moment
        """
        temp_media = float(self.soup.media.text)
        temperature = str(int(round(temp_media)))
        return temperature

    def getPeriod(self, hour):
        if int(hour) >= 6 and int(hour) < 13:
            return 'Manhã'
        elif int(hour) >= 13 and int(hour) < 19:
            return 'Tarde'
        elif int(hour) >= 19 and int(hour) <= 23:
            return 'Noite'
        elif int(hour) >= 0 and int(hour) < 6:
            return 'Madrugada'

    def getHour(self, hour):
        if int(hour) >= 6 and int(hour) < 13:
            return self.getPrevManha()
        elif int(hour) >= 13 and int(hour) < 19:
            return self.getPrevTarde()
        elif int(hour) >= 19 and int(hour) <= 23:
            return self.getPrevNoite()
        elif int(hour) >= 0 and int(hour) < 6:
            return self.getPrevMadrugada()

    def getContentExcept(self, class_li, text_div):
        """
        return content to except in case error
        """
        content = """
                   <li class="%(li)s ver-mais">
                   <div class="dash-border" style="display: block;">
                   <strong class="titulo-dash">%(text_div)s</strong>
                   <p class="sp-erro">Não foi possível carregar informações</p>
                   </div>
                   """ % {'text_div': text_div, 'li': class_li}
        return content

    def getContentExceptOculto(self, class_li, text_div):
        """
        return content to except in case error
        """
        content = """
                   <li class="%(li)s ver-mais">
                   <div id="call-aero" style="display: block;">
                   <h3 class="titulo-dash">%(text_div)s</h3>
                   <button class="fechar-dash">X</button>
                   </br>
                   <p class="sp-erro" style="margin-top: 10px;">Não foi possível carregar informações</p>
                   </div>
                   """ % {'text_div': text_div, 'li': class_li}
        return content

    @ram.cache(lambda *args: time() // (60 * 15))
    def getDescQualidade(self, local='Congonhas'):
        """
        return type description qualidaty atmosfera
        """
        quality = int(self.soup.find('td', text=local).parent.find('td', width=50).text)
        if quality >= 0 and quality <= 40:
            descript = 'Boa'
        elif quality >= 41 and quality <= 80:
            descript = 'Moderado'
        elif quality >= 81 and quality <= 120:
            descript = 'Ruim'
        elif quality >= 121 and quality <= 200:
            descript = 'Muito Ruim'
        elif quality >= 200:
            descript = 'Pessimo'
        return descript

    @ram.cache(lambda *args: time() // (60 * 15))
    def getTempMaxima(self):
        """
        return time morning
        """
        self.soup = BeautifulSoup(self.getContent(url_direct.get("ex-clima")))
        dia = self.soup.findAll('dia')
        temp_max = dia[0].parent.find('temp-max')
        return temp_max.string

    @ram.cache(lambda *args: time() // (60 * 15))
    def getTempMinima(self):
        """
        return temperature minimo
        """
        self.soup = BeautifulSoup(self.getContent(url_direct.get("ex-clima")))
        dia = self.soup.findAll('dia')
        temp_min = dia[0].parent.find('temp-min')
        return temp_min.string

    @ram.cache(lambda *args: time() // (60 * 15))
    def getUmidadeArMax(self):
        """
        return unit ar max
        """
        self.soup = BeautifulSoup(self.getContent(url_direct.get("ex-clima")))
        dia = self.soup.findAll('dia')
        umid_max = dia[0].parent.find('umid-max')
        return umid_max.string

    @ram.cache(lambda *args: time() // (60 * 15))
    def getUmidadeArMin(self):
        """
        return unit ar min
        """
        self.soup = BeautifulSoup(self.getContent(url_direct.get("ex-clima")))
        dia = self.soup.findAll('dia')
        umid_min = dia[0].parent.find('umid-min')
        return umid_min.string

    @ram.cache(lambda *args: time() // (60 * 15))
    def getHoraNascerSol(self):
        """
        return hour sunrise
        """
        self.soup = BeautifulSoup(self.getContent(url_direct.get("ex-clima")))
        dia = self.soup.findAll('dia')
        sunrise = dia[0].parent.find('sunrise')
        return sunrise.string

    @ram.cache(lambda *args: time() // (60 * 15))
    def getHoraPorSol(self):
        """
        return sunset time
        """
        self.soup = BeautifulSoup(self.getContent(url_direct.get("ex-clima")))
        dia = self.soup.findAll('dia')
        sunset = dia[0].parent.find('sunset')
        return sunset.string

    """
    ##########################################################################
                           Qualidade do ar
    ##########################################################################
    """
    @ram.cache(lambda *args: time() // (60 * 15))
    def getAirQuality(self):
        try:
            content = """
                      <div id="call-ar" class="dash" style="display: block;">
                      <h3>Qualidade do Ar <em class="fonte">Fonte: CETESB</em></h3>
                      <button class="fechar-dash">X</button>
                      <div class="O2"></div>
                      <div id="o2mapa">
                      <div class="kineticjs-content" role="presentation" style="position: relative; display: inline-block; width: 300px; height: 160px;">
                      <canvas width="300" height="160" style="padding: 0px; margin: 0px; border: 0px; position: absolute; top: 0px; left: 0px; width: 300px; height: 160px; background: transparent;"></canvas>
                      </div>
                      </div>
                      <ol id="dica">
                      <li><i></i> Pessoas com doenças respiratórias podem apresentar sintomas como tosse seca e cansaço</li>
                      <li><i></i>Pessoas com doenças cardíacas ou pulmonares, procurem reduzir esforço pesado ao ar livre.</li>
                      <li><i></i> Reduzir o esforço físico pesado ao ar livre, principalmente pessoas com doenças cardíacas ou pulmonares, idosos e crianças.</li>
                      <li><i></i> População em geral pode apresentar sintomas como ardor nos olhos, nariz e garganta, tosse seca e cansaço.</li>
                      </ol>
                      </div>
                      """
        except:
            content = self.getContentExceptOculto(class_li='ex-ar', text_div='Qualidade do Ar')
        return content

    @ram.cache(lambda *args: time() // (60 * 15))
    def getEfeitoSaude(self):
        """
        return list efect quality life
        """
        list_quality = []
        content_list = self.soup.findAll('td', {'colspan': '4', 'bgcolor': '#e2ecf5'})
        for quality in content_list:
            _quality = quality.text[2:].strip()
            if _quality != '--':
                list_quality.append({'quality': _quality})
        return list_quality

    """
    ##########################################################################
                           Clima
    ##########################################################################
    """
    @ram.cache(lambda *args: time() // (60 * 15))
    def getWeatherSp(self, title=False):
        try:
            self.soup = BeautifulSoup(self.getContent(url_direct.get("ex-clima-media")))
            temp_media = self.getTempMedia()

            self.soup = BeautifulSoup(self.getContent(url_direct.get("ex-clima")))
            dia = self.soup.findAll('dia')

            prev_manha = dia[0].parent.find('ct', {'periodo': 'Manhã'})
            prev_tarde = dia[0].parent.find('ct', {'periodo': 'Tarde'})
            prev_noite = dia[0].parent.find('ct', {'periodo': 'Noite'})
            prev_madrugada = dia[0].parent.find('ct', {'periodo': 'Madrugada'})
            umidade_ar_max = self.getUmidadeArMax()
            umidade_ar_min = self.getUmidadeArMin()
            hora_nascer_sol = self.getHoraNascerSol()
            hora_por_sol = self.getHoraPorSol()
            temp_maxima = self.getTempMaxima()
            temp_minima = self.getTempMinima()
            content = """
                      <div id="call-clima" class="dash" style="display: block;">
                      <h3>Tempo <em class="fonte">Fonte: CGE</em></h3>
                      <button class="fechar-dash">X</button>
                      <div id="temp-bloco">
                      <div id="t-agora" class="tempo-g nb"></div>
                      <div id="t-media"><small class="em08">Temperatura Media</small><br><span id="temp-media" class="amarelo em18">%(media)s°</span></div>
                      <div id="minXmax">
                      <div id="new-max"><span class="tmax"></span>%(max)s</div>
                      <div id="new-min"><span class="tmin"></span>%(min)s</div>
                      </div>
                      </div>
                      <ul id="dia-todo">
                      <li>
                      <strong class="azul-pq em08">Manha</strong>
                      <div class="tempo-p pn-pq"></div>
                      <div class="raio"></div>
                      <span class="em07 bold amarelo">%(manha)s</span>
                      </li>
                      <li>
                      <strong class="azul-pq em08">Tarde</strong>
                      <div class="tempo-p pi-pq"></div>
                      <div class="raio"></div>
                      <span class="em07 bold amarelo">%(tarde)s</span>
                      </li>
                      <li>
                      <strong class="azul-pq em08">Noite</strong>
                      <div class="tempo-p pi-pq-noite"></div>
                      <div class="raio"></div>
                      <span class="em07 bold amarelo">%(noite)s</span>
                      </li>
                      <li>
                      <strong class="azul-pq em08">Madrugada</strong>
                      <div class="tempo-p nb-pq-noite"></div>
                      <div class="raio"></div>
                      <span class="em07 bold amarelo">%(madrugada)s</span>
                      </li>
                      </ul>
                      <div id="tempor-outras">
                      <div class="a-40 bold">
                      <small class="em07"><span id="div" class="gotas"></span>Umidade relativa do ar</small>
                      <div class="a-half em13"><span class="tmax"></span> %(umax)s</div>
                      <div class="a-half em13"><span class="tmin"></span> %(umin)s</div>
                      </div>
                      <div class="sol-box">
                      <div id="sol"></div>
                      <div class="a-half"><small class="amarelo em14">%(hrin)s</small> <small class="em07">Nascer do sol</small></div>
                      <div class="a-half"><small class="amarelo em14">%(hrmax)s</small> <small class="em07">Por do sol</small></div>
                      </div></div></div>
                      """ % {'media': temp_media, 'max': temp_maxima[:-1], 'min': temp_minima[:-1], 'manha': prev_manha['pt'], 'tarde': prev_tarde['pt'], 'noite': prev_noite['pt'], 'madrugada': prev_madrugada['pt'], 'umax': umidade_ar_max, 'umin': umidade_ar_min, 'hrin': hora_nascer_sol[:-1], 'hrmax': hora_por_sol[:-1]}
        except:
            content = self.getContentExceptOculto(class_li='ex-clima', text_div='Tempo')
        return content

    """
    ##########################################################################
                           Situação dos Aeroportos
    ##########################################################################
    """

    list_aeport = {'asbsp': {'codigo': 'CGH',
                             'name': 'Congonhas',
                             'label': 'CGH - Congonhas',
                             'local': 'Sao Paulo - Congonhas-SP',
                             'site': 'http://www.infraero.gov.br/index.php/aeroportos/sao-paulo/aeroporto-de-sao-paulo-congonhas.html'},
                   'bsbgr': {'codigo': 'GRU',
                             'name': 'Guarulhos',
                             'label': 'GRU - Guarulhos',
                             'local': 'Sao Paulo - Guarulhos-SP',
                             'site': 'http://www.gru.com.br/pt-br'},
                   'csbmt': {'codigo': 'MAE',
                             'name': 'Cpo. de Marte',
                             'label': 'MAE - Cpo. de Marte',
                             'local': 'Sao Paulo - Cpo de Marte-SP',
                             'site': 'http://www.infraero.gov.br/index.php/aeroportos/sao-paulo/aeroporto-campo-de-marte.html'},
                   'dsbkp': {'codigo': 'VCP',
                             'name': 'Viracopos',
                             'label': 'VCP- Viracopos',
                             'local': 'Campinas-SP',
                             'site': 'http://www.viracopos.com/passageiros/voos/'}}

    situation_aeport = {'pontoVerde': 'Operando Normalmente',
                        'pontoAmarelo': 'Restrições meteorológicas',
                        'pontoVermelho': 'Fechado operações',
                        'pontoBranco': 'Indisponivel no momento'}

    def getAirportFlights(self):
        referer = None
        default_headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.2.9) Gecko/20100824 Firefox/3.6.9 ( .NET CLR 3.5.30729; .NET4.0E)',
                           'Accept-Language': 'pt-br;q=0.5',
                           'Accept-Charset': 'utf-8;q=0.7,*;q=0.7',
                           'Accept-Encoding': 'gzip',
                           'Connection': 'close',
                           'Cache-Control': 'no-cache',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Referer': referer}
        encoded_data = None
        url = url_direct.get('dash-aero-situacao')
        dt = Request(url, encoded_data, default_headers, origin_req_host=referer)
        try:
            response = urllib2.urlopen(dt, timeout=8).read()
            soup = BeautifulSoup(response)
            retorno = {}

            for aeroporto in sorted(self.list_aeport.keys()):
                aeroporto_congonhas = soup.find(id=aeroporto[1:])
                situacao_aeroporto = self.situation_aeport[aeroporto_congonhas['class'][0]]
                retorno[aeroporto] = {'aeroporto': self.list_aeport[aeroporto]['local'], 'status': situacao_aeroporto, 'label': self.list_aeport[aeroporto]['label']}

            content = """
                      <div id="call-aero" class="dash" style="display: block;">
                      <h3>Aeroportos <em class="em08 fonte">Fonte: Infraero e GRU</em></h3>
                      <button class="fechar-dash">X</button>
                      <ul id="aero-lista">
                      """
            for aeroport in retorno:
                print str(aeroport[1:])
                css_bolinha = "verde"
                if aeroport[1:] in ['sbkp', 'sbgr']:
                    css_bolinha = "vermelho"
                if 'sbsp' == str(aeroport[1:]):
                    statusVooCongonhas = self.AeroportoVooSatus()
                    content += """
                               <li class="cgh"><strong class="aeronome">%(aeroporto)s</strong><small>
                               <span class="%(css_bolinha)s"><b class="ball-status %(css_bolinha)s"></b>%(status)s</span>
                               %(statusVooCongonhas)s
                               </li>
                               """ % {'aeroporto': retorno[aeroport]['label'], 'status': retorno[aeroport]['status'], 'statusVooCongonhas': statusVooCongonhas, 'css_bolinha': css_bolinha}
                else:
                    content += """
                               <li class="cgh"><strong class="aeronome">%(aeroporto)s</strong><small>
                               <span class="%(css_bolinha)s"><b class="ball-status %(css_bolinha)s"></b>%(status)s</span></li>
                               """ % {'aeroporto': retorno[aeroport]['label'], 'status': retorno[aeroport]['status'], 'css_bolinha': css_bolinha}

            content += "</ul></div>"
        except Exception, e:
            content = self.getContentExceptOculto(class_li='ex-aero', text_div='Aeroportos')
            print '1', e.__doc__
            print '2', sys.exc_info()
            print '3', sys.exc_info()[0]
            print '4', sys.exc_info()[1]
            print '5', sys.exc_info()[2], 'Sorry I mean line...', traceback.tb_lineno(sys.exc_info()[2])
            ex_type, ex, tb = sys.exc_info()
            print '6', traceback.print_tb(tb)
        return content

    @ram.cache(lambda *args: time() // (60 * 15))
    def AeroportoVooSatus(self):
        soup = BeautifulSoup(self.getContent(url_direct.get('dash-aero')))
        content = ''
        situacao = soup.find('td', text='Sao Paulo - Congonhas-SP')
        if situacao:
            voos = situacao.parent.findAll('span')
            content += """
                       <br>
                       <span class="txt-right">Vôos atrasados:</span>
                       <span class="txt-left azul-pq">%(atrasado)s</span></small>
                       <small><span class="txt-right">Vôos cancelados:</span>
                       <span class="txt-left azul-pq">%(cancelado)s</span></small>
                       """ % {'atrasado': voos[0].text, 'cancelado': voos[8].text}
        else:
            content += '<p>Consulte situação</p>'
        return content

    """
    ##########################################################################
                           Rodizio SP
    ##########################################################################
    """
    @ram.cache(lambda *args: time() // (60 * 15))
    def getCarRotation(self):
        try:
            url_rodizio = url_direct.get('dash-rodizio')
            placas_final_url_return = urllib.urlopen(url_rodizio)
            data_result = json.loads(placas_final_url_return.read())
            placa = data_result['Rotation']['desc']
            content = """
                      <div id="call-rodizio" class="dash" style="display: block;">
                      <h3>Rodízio</h3>
                      <button class="fechar-dash">X</button>
                      <div id="mapa-rodizio"></div>
                      <ul class="rod-3col">
                      <li><span class="em08 bold">Placas final:</span><br><span class="amarelo em15">%(placa)s</span></li>
                      <li><span class="em08 bold">Horário:</span><br><small class="amarelo em1">7h às 10h</small><br><small class="amarelo em1">17h às 20h</small></li>
                      <li><span class="em08 bold">Penalidade:</span><br><small class="amarelo em10">R$85,13</small><small class="amarelo em08"> e 4pts na carteira</small></li>
                      </ul>
                      </div>
                      """ % {'placa': placa}
        except KeyError:
            print "well, it WASN'T defined after all!"
            content = self.getContentExceptOculto(class_li='ex-rodizio', text_div='Rodízio')
        return content

    """
    ##########################################################################
                           Trânsito SP
    ##########################################################################
    """
    @ram.cache(lambda *args: time() // (60 * 15))
    def getTraffic(self):
        try:
            self.soup = BeautifulSoup(self.getContent(url_direct.get('transito-agora')))
            lista_zonas_sp = ('OesteLentidao', 'NorteLentidao',
                              'LesteLentidao', 'SulLentidao', 'lentidao')
            km_lentidao = []
            for zonas_sp in lista_zonas_sp:
                km_lentidao.append(self.soup.find('div', {"id": zonas_sp}).string)

            result = self.getTrafficCount(km_lentidao[4])
            print type(result)
            content = """
                      <div id="call-trans" class="dash" style="display: block;">
                      <h3>Trânsito</h3>
                      <button class="fechar-dash">X</button>
                      <div class="tran-total">
                      <div class="ttotal"><span class="amarelo em14 bold">%(lentidao)s km</span><br><small class="bold em09">de lentidão</small></div>
                      <div class="ttotal %(css)s"><br><span class="%(css)s bolinha"></span>%(status_transito_sp)s</div>
                      </div>
                      <hr class="pont">
                      <div id="sp-mapa">
                      <ul id="lentidao">
                      <li id="kmOeste" class="amarelo">%(oeste)s</li>
                      <li id="kmNorte" class="amarelo">%(norte)s</li>
                      <li id="kmLeste" class="amarelo">%(leste)s</li>
                      <li id="kmSul" class="amarelo">%(sul)s</li>
                      </ul>
                      </div>
                      <div class="bloco-linha"><a href="http://www.cetsp.com.br/transito-agora/mapa-de-fluidez.aspx" class="azul-pq" target="_blank">Mapa de fluidez</a> <a href="http://www.cetsp.com.br/transito-agora/transito-nas-principais-vias.aspx" target="_blank" class="azul-pq">Lentidão por corredor</a></div></div>
                      """ % {'oeste': km_lentidao[0][:5], 'norte': km_lentidao[1][:5], 'leste': km_lentidao[2][:5], 'sul': km_lentidao[3][:5], 'lentidao': km_lentidao[4], 'css': result[0], 'status_transito_sp': result[1]}
        except:
            content = self.getContentExceptOculto(class_li='ex-transito', text_div='Transito')
        return content

    @ram.cache(lambda *args: time() // (60 * 15))
    def getTrafficCount(self, total_km_lentidao):
        traffic_count = []
        if int(total_km_lentidao) <= 45:
            status_transito_sp = 'livre'
            css = 'verde'
        elif int(total_km_lentidao) >= 45 and int(total_km_lentidao) <= 90:
            status_transito_sp = 'regular'
            css = 'amarelo'
        elif int(total_km_lentidao) > 90:
            css = 'vermelho'
            status_transito_sp = 'ruim'
        traffic_count.append(css)
        traffic_count.append(status_transito_sp)
        return traffic_count

    """
    ##########################################################################
                           Transporte Público
    ##########################################################################
    """
    @ram.cache(lambda *args: time() // (60 * 15))
    def getMeansOfTransportation(self):
        try:
            status_metro_sp = self.getStatusMetro()
            status_trens_sp = self.getStatusCptm()
            content = """
                      <div id="call-publi" class="dash" style="display: block;">
                      <h3>Transporte Público</h3> <button class="fechar-dash">X</button>
                      <ul>
                      <li>
                      <div class="status"><i class="verde"></i></div>
                      <div class="mini Mbus"></div>
                      <span id="spT-twitter">Não saia de casa sem antes consultar qual o melhor trajetos.
                      Acesse: <a href="http://www.sptrans.co" target="_blank">Mais</a></span>
                      </li>
                      <li>
                      <div class="status"><i class="amarelo"></i></div>
                      <div class="mini Mmetro"></div>
                      <span id="t-metro">%(metro)s</span>
                      </li>
                      <li>
                      <div class="status"><i class="vermelho"></i></div>
                      <div class="mini Mcptm"></div>
                      <span id="t-cptm">%(trem)s</span>
                      </li>
                      </ul>
                      <a href="http://www.sptrans.com.br/itinerarios/" target="_blank" class="link-amarelo">Consultar itinerários</a>
                      </div>
                       """ % {'metro': status_metro_sp, 'trem': status_trens_sp}
        except:
            content = self.getContentExceptOculto(class_li='ex-publico', text_div='Transporte público')
        return content

    @ram.cache(lambda *args: time() // (60 * 15))
    def getStatusCptm(self):
        """
        return Informações CPTM da cidade de São Paulo
        """
        retorno = BeautifulSoup(self.getContent(url_direct.get('transp-cptm')))
        transp_metro = retorno.findAll('span', {'class': 'nome_linha'})
        linhas_cptm = []
        linhas_com_problemas = {}
        for x in transp_metro:
            linhas_cptm.append(x.string.lower())

        content = ''
        for key, x in enumerate(linhas_cptm):
            for div in retorno.find_all(class_=x):
                contador = 0
                for childdiv in div.find_all('span'):
                    if contador % 2:
                        if childdiv.string.lower().find('normal') == int(-1):
                            linhas_com_problemas[key] = {'situacao': childdiv.string, 'linha': x}
                    contador = contador + 1

        content = ''
        if len(linhas_com_problemas) > 0:
            for x in linhas_com_problemas.values():
                content += '<p>Linha: %s - %s </p>' % (x['linha'], x['situacao'])
        else:
            content += 'Circulação normal'
        return content

    @ram.cache(lambda *args: time() // (60 * 15))
    def getStatusMetro(self):
        """
        return Informações Metro da cidade de São Paulo
        """
        retorno = BeautifulSoup(self.getContent(url_direct.get('transp-metro')))
        transp_metro = retorno.find('ul', {'id': 'statusLinhaMetro'}).findAll('div')

        linhas_com_problemas = {}
        nome_da_linha = ''
        for key, value in enumerate(transp_metro):
            if key % 2:
                situacao = value.find('span').string
                if situacao is None:
                    linhas_com_problemas[key] = {'situacao': (nome_da_linha + ' apresenta problemas')}
            else:
                nome_da_linha = value.find('span').string
        content = ''
        if len(linhas_com_problemas) > 0:
            for x in linhas_com_problemas.values():
                content += '%s' % x['situacao']
        else:
            content += 'Circulação normal'

        return content

    """
    ##########################################################################
                           Tweets
    ##########################################################################
    """

    @ram.cache(lambda *args: time() // (60 * 15))
    def getTweets(self, consumer_key='OOXF8haUGyWq2YNoSciDTLGXd', consumer_secret='sZfagT290goGqJG94H0Nng2gsEStqvpEbz3wEw0UTHgboxrUmh', access_token_secret='A0DEgOpSCTu44NZcyMHCtXdNBFq8vsFwMKSv7Neenl7AY', access_token='3397165841-g80Y2QqVEEjhzqMsQTDBpyWiz1Mcm0pwv519GfN', screen_name='saopaulo_agora', count=5):
        api = Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token, access_token_secret=access_token_secret)
        try:
            api.VerifyCredentials()
            statuses = api.GetUserTimeline(screen_name=screen_name)[:int(count)]
            ocorrencias = []
            ocorrencias.append('<div>')
            y = 0
            for i in statuses:
                text = ""
                if y == int(0):
                    text = '<a href="https://twitter.com/' + screen_name + '/statuses/' + str(i.id) + '" class="selecionado" target="_blank">' + str(i.text) + '<time>' + str(i.relative_created_at) + '</time></a>'
                    # ocorrencias.append(status)
                else:
                    text = '<a href="https://twitter.com/' + screen_name + '/statuses/' + str(i.id) + '" target="_blank">' + str(i.text) + '<time>' + str(i.relative_created_at) + '</time></a>'
                ocorrencias.append(text)
                y = y + 1
            ocorrencias.append('</div>')
            return ocorrencias
        except:
            return False
