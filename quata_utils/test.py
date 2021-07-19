import quata_utils as qu
import requests
from fake_useragent import UserAgent


def get_ids(request):
  lista_fundos  = qu.get_fundos_fnet()
  ids = []
  for fundo in lista_fundos:
    result = qu.get_informes_id(fundo["id"])
    id_list = [item['id'] for item in result]
    print(fundo["id"])
    print(id_list)

    for i in id_list:
      ids.append(i)

  return "Conseguimos! Os requests retornaram {} ids".format(len(ids))
    
if __name__ == "__main__":
    print("teste")
    mensage = get_ids(request="tcharam")
    print(mensage)
