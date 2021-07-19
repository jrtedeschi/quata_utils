"""Main module."""
import requests

import warnings
import xmltodict
import base64
import xml.etree.ElementTree as ET
from collections import defaultdict
import json
from datetime import datetime
import logging
from time import sleep
import random
from fake_useragent import UserAgent


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
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
    URL = "https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=3&s=0&l=200&o%5B0%5D%5BdataEntrega%5D=desc&tipoFundo=1&idCategoriaDocumento=6&idTipoDocumento=40&idEspecieDocumento=0&cnpjFundo={admin}&dataInicial={day1}%2F{month1}%2F{year1}&dataFinal={day}%2F{month}%2F{year}&_=1626271510426"
    warnings.filterwarnings("ignore")
    try:
        r = requests.get(URL.format(admin=cnpj,day1="01",month1="01",year1="2016",day="31",month="12",year="2021"),\
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

    
