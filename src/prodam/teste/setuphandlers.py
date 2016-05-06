# -*- coding: utf-8 -*-
from plone.app.textfield.value import RichTextValue

def post_install(context):
    """Post install script"""
    if context.readDataFile('prodamteste_default.txt') is None:
        return
    # Do something during the installation of this package
    site = context.getSite()
    prepareDb(site)

def prepareDb(portal):
    """
    Criacao de pastas para o rodape personalizado
    """
    if('wagner-rodape' not in portal.objectIds()):
        portal.invokeFactory('Folder','wagner-rodape', title='Rodape do Wagner', exclude_from_nav=True)


    pasta = portal['wagner-rodape']    
    if('governo-municipal' not in pasta.objectIds()):
        pasta.invokeFactory('Folder','governo-municipal', title='Governo municipal', exclude_from_nav=True)

    if('acontece-na-cidade' not in pasta.objectIds()):
        pasta.invokeFactory('Folder','acontece-na-cidade', title='Acontece na cidade', exclude_from_nav=True)

    if('sao-paulo-para' not in pasta.objectIds()):
        pasta.invokeFactory('Folder','sao-paulo-para', title='Parando sao paulo', exclude_from_nav=True)

    if('atendimento' not in pasta.objectIds()):
        pasta.invokeFactory('Folder','atendimento', title='Atendimento', exclude_from_nav=True)


    if('canais-oficiais' not in pasta.objectIds()):
        pasta.invokeFactory('Folder','canais-oficiais', title='Canais oficiais', exclude_from_nav=True)

    if('consultas' not in pasta.objectIds()):
        pasta.invokeFactory('Folder','consultas', title='Consultas', exclude_from_nav=True)


    pasta_governo = pasta['governo-municipal']
    if('governo-municipal' not in pasta_governo.objectIds()):
        text='<ul><li><span>Prefeito</span><strong>Fernando Haddad</strong></li><li><a href="http://www.prefeitura.sp.gov.br/guiadeservicos/content/equipe-de-governo" target="_blank"><strong>Equipe de Governo</strong></a></li></ul><ul class="lista"><li><a href="../../agenda/prefeito">Agenda do prefeito</a></li></ul>'
        pasta_governo.invokeFactory('Document','governo-municipal',title="Governo municipal",text=RichTextValue(text, 'text/html', 'text/x-html-safe', encoding='utf-8'))


    pasta_acontece = pasta['acontece-na-cidade']
    if('ultimas-noticias' not in pasta_acontece.objectIds()):
        pasta_acontece.invokeFactory('Link','ultimas-noticias',title='Ultimas noticias',remoteUrl='/Prefeitura/noticia')

    if('itinerario-de-onibus' not in pasta_acontece.objectIds()):
        pasta_acontece.invokeFactory('Link','itinerario-de-onibus',title='Itinerarios',remoteUrl='http://www.sptrans.com.br/itinerarios/')

    if('mapa-de-servicos' not in pasta_acontece.objectIds()):
        pasta_acontece.invokeFactory('Link','mapa-de-servicos',title='Mapa de servicos',remoteUrl='/Prefeitura/mapa')

    pasta_para = pasta['sao-paulo-para']
    if('empresa' not in pasta_para.objectIds()):
        pasta_para.invokeFactory('Link','empresa',title='Empresa',remoteUrl='/Prefeitura/empresa')

    if('cidadao' not in pasta_para.objectIds()):
        pasta_para.invokeFactory('Link','cidadao',title='Cidadao',remoteUrl='/Prefeitura/cidadao')

    if('turismo' not in pasta_para.objectIds()):
        pasta_para.invokeFactory('Link','turismo',title='Turista',remoteUrl='/Prefeitura/turista')

    if('servidor' not in pasta_para.objectIds()):
        pasta_para.invokeFactory('Link','servidor',title='Servidor',remoteUrl='/Prefeitura/servidor')

    pasta_atendimento = pasta['atendimento']
    if('solicitacao' not in pasta_atendimento.objectIds()):
        text='<ul class="box_content"><li><a target="_blank" aria-label="Faça sua Solicitação" href="http://sac.prefeitura.sp.gov.br Faça sua Solicitação</a></li></ul>'
        pasta_atendimento.invokeFactory('Document','solicitacao',title="Solicitacao",text=RichTextValue(text, 'text/html', 'text/x-html-safe', encoding='utf-8'))

    pasta_canais = pasta['canais-oficiais']
    if('canais' not in pasta_canais.objectIds()):
        text='<ul class="social_footer" id="social_footer"><li><a target="_blank" href="https://www.facebook.com/PrefSP"><span id="facebook">Facebook</span></a></li><li><a target="_blank" href="http://www.twitter.com/prefsp"><span id="twitter">Twitter</span></a></li><li><a target="_blank" href="http://www.youtube.com/prefeiturasaopaulo"><span id="youtube">Youtube</span></a></li><li style="clear: both;padding-top: 14px;"><a target="_blank" href="http://www.docidadesp.imprensaoficial.com.br"><span id="diario"></span>Diário Oficial</a></li></ul>'
        pasta_canais.invokeFactory('Document','canais',title="Canais oficiais",text=RichTextValue(text, 'text/html', 'text/x-html-safe', encoding='utf-8'))

    pasta_consultas = pasta['consultas']
    if('leis-municipais' not in pasta_consultas.objectIds()):
        pasta_consultas.invokeFactory('Link','leis-municipais',title='Leis municipais',remoteUrl='http://www.prefeitura.sp.gov.br/cidade/secretarias/negocios_juridicos/cadastro_de_leis/index.php?p=325')

    if('pesquisa-de-processos' not in pasta_consultas.objectIds()):
        pasta_consultas.invokeFactory('Link','pesquisa-de-processos',title='Pesquisa de processos',remoteUrl='http://www3.prodam.sp.gov.br/simproc/simproc.asp')

    if('licitacoes' not in pasta_consultas.objectIds()):
        pasta_consultas.invokeFactory('Link','licitacoes',title='Licitacoes',remoteUrl='http://e-negocioscidadesp.prefeitura.sp.gov.br/')

    if('ata-registro-precos' not in pasta_consultas.objectIds()):
        pasta_consultas.invokeFactory('Link','ata-registro-precos',title='Ata de registro de precos',remoteUrl='http://www.prefeitura.sp.gov.br/cidade/secretarias/planejamento/links/index.php?p=24208')
