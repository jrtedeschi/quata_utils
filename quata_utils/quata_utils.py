"""Main module."""
import requests
import warnings
import xmltodict
import pandas as pd
import base64
import xml.etree.ElementTree as ET
from collections import defaultdict
import json
from datetime import datetime
import logging
from time import sleep
import random
import tqdm
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def chunks(l, n):
    """ Divide uma lista em n sublistas """
    d, r = divmod(len(l), n)
    for i in range(n):
        si = (d+1)*(i if i < r else r) + d*(0 if i < r else i - r)
        yield l[si:si+(d+1 if i < r else d)]

def get_fundos_fnet():
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
    URL = "https://fnet.bmfbovespa.com.br/fnet/publico/listarFundos?&term=&page={}&idTipoFundo=1&idAdm=0&paraCerts=false&_=1626443273261"
    warnings.filterwarnings("ignore")
    data_list = []
    condition = True
    i = 0
    while condition == True:
        i += 1
        try:
            # sleep(random.randint(2,2))
            r = requests.get(URL.format(i),\
                verify=False,\
                headers={'User-Agent': ua})
            if r.status_code == 200:
                data_list.append(r.json()['results'])
                condition = r.json()['more']
            else:
                print("Erro: ",r.status_code,' ' , r.text)
        except:
            print("Erro no request")
            pass
    fundos = [item for sublista in data_list for item in sublista]
    return fundos

def get_informes_id(cnpj):
    date = datetime.today()
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
    URL = "https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=3&s=0&l=200&o%5B0%5D%5BdataEntrega%5D=desc&tipoFundo=1&idCategoriaDocumento=6&idTipoDocumento=40&idEspecieDocumento=0&cnpjFundo={admin}&dataInicial={day1}%2F{month1}%2F{year1}&dataFinal={day}%2F{month}%2F{year}&_=1626271510426"
    warnings.filterwarnings("ignore")
    try:
        r = requests.get(URL.format(admin=cnpj,day1="01",month1="01",year1="2016",day=str(date.day()),month=str(date.month()),year=str(date.year())),\
            verify=False,\
            headers={'User-Agent': ua})

        if r.status_code == 200:
            data = r.json()['data']
            return data
        else:
            return "Erro: Status Code: {} - {} ".format(r.status_code , r.text)
    except:
        raise
        pass


def get_rendimentos_id(cnpj):
    date = datetime.today()
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
    URL = "https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=2&s=0&l=200&o%5B0%5D%5BdataEntrega%5D=desc&tipoFundo=1&cnpjFundo={cnpj}&idCategoriaDocumento=14&idTipoDocumento=41&idEspecieDocumento=0&situacao=A&_=1626801789397"
    warnings.filterwarnings("ignore")
    try:
        r = requests.get(URL.format(cnpj=cnpj),\
            verify=False,\
            headers={'User-Agent': ua})

        if r.status_code == 200:
            data = r.json()['data']
            return data
        else:
            return "Erro: Status Code: {} - {} ".format(r.status_code , r.text)
    except:
        raise
        pass
    
def get_rendimentos(ids):
    """Pega os dividendos de um dado cnpj, tendo como fonte de dados o site do fundosnet"""
    
    warnings.filterwarnings("ignore")
    dd = defaultdict(list)

    lista_campos = ["id","CodNegociacaoCota","NomeFundo","CNPJFundo","ValorProventoCota","DataPagamento","DataAprovacao","DataBase","PeriodoReferencia",\
    "Ano","CodISINCota","ResponsavelInformacao","NomeAdministrador","CNPJAdministrador"]

    lista_dados = []
    url = "https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id={}"

    for id in tqdm.tqdm(ids): 
    #make request
        try:
            r = requests.get(url.format(id),verify=False)
            decoded_text = base64.b64decode(r.text)
            root = ET.fromstring(decoded_text)
            rendimento = {child.tag:child.text for child in root.find("InformeRendimentos").find("Rendimento")}
            dadosgerais = {child.tag:child.text for child in root.find("DadosGerais")}
            id_data = {"id":id}

            predata = dict(**id_data, **rendimento, **dadosgerais)
            data = {i: predata[i] for i in lista_campos}
            lista_dados.append(data)
        except:
            print("id {} não foi baixado, tentando mais uma vez".format(id))
            try:
                r = requests.get(url.format(id),verify=False)
                decoded_text = base64.b64decode(r.text)
                root = ET.fromstring(decoded_text)
                rendimento = {child.tag:child.text for child in root.find("InformeRendimentos").find("Rendimento")}
                dadosgerais = {child.tag:child.text for child in root.find("DadosGerais")}
                id_data = {"id":id}

                predata = dict(**id_data, **rendimento, **dadosgerais)
                data = {i: predata[i] for i in lista_campos}
                lista_dados.append(data)
            except:
                print("id {} não foi baixado, triste".format(id))
                pass

    for d in lista_dados: # you can list as many input dicts as you want here
        for key, value in d.items():
            dd[key].append(value)

    return pd.DataFrame.from_dict(dd)


def xml_downloader(lista_ids, filename = "filename"):
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
    warnings.filterwarnings("ignore")
    logging.basicConfig(filename=BASE_DIR+filename+".log",level=logging.INFO)
    logging.info("processo iniciado")

    url = "https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id={}"
    lista = []

    for id in tqdm.tqdm(lista_ids): 
        logging.info("tentativa de request para o id {}".format(id))
        try:
            r = requests.get(url.format(id),verify=False, headers = {'User-Agent': ua.random})
            decoded_text = base64.b64decode(r.text)
            data = pd.json_normalize(xmltodict.parse(decoded_text),max_level=3,sep="_")
            data['id'] = id
            lista.append(data)
            logging.info("request id {} feito com sucesso".format(id))
        except:
            logging.info("request id {} deu erro".format(id))
            pass
    if len(lista) == 0:
        print("erro no tamanho da lista")
    df = pd.concat(lista)       
    return df