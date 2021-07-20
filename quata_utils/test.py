import quata_utils as qu
import requests
from fake_useragent import UserAgent
from google.oauth2 import service_account
from google.cloud import storage
credentials = service_account.Credentials.from_service_account_file("/mnt/c/Users/joaor/documents/projetos/quata_utils/qscraper/deployment/heroic-goal-319113-c71736c4d4b0.json")

client = storage.Client(credentials=credentials)


# https://console.cloud.google.com/storage/browser/[bucket-id]/
bucket = client.get_bucket('teste-rw')



def get_ids(request):
  lista_fundos  = qu.get_fundos_fnet()
  ids = []
  for fundo in lista_fundos[0:4]:
    result = qu.get_informes_id(fundo["id"])
    id_list = [item['id'] for item in result]


    for i in id_list:
      ids.append(i)

  blob = bucket.blob("teste")
  blob.upload_from_string("Conseguimos! Os requests retornaram {} ids".format(len(ids)))

  return "Conseguimos! Os requests retornaram {} ids".format(len(ids))
    
if __name__ == "__main__":
    print("teste")
    mensage = get_ids(request="tcharam")
    print(mensage)
