import requests
import os
import urllib3
from datetime import datetime
import pandas as pd
import time

OUTPUT_FOLDER="./data/cie11/"
os.mkdir(OUTPUT_FOLDER, exist_ok=True)

# Suppress only the InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

master_child = [
    'http://id.who.int/icd/release/11/2024-01/mms/1435254666',
  'http://id.who.int/icd/release/11/2024-01/mms/1630407678',
  'http://id.who.int/icd/release/11/2024-01/mms/1766440644',
  'http://id.who.int/icd/release/11/2024-01/mms/1954798891',
  'http://id.who.int/icd/release/11/2024-01/mms/21500692',
  'http://id.who.int/icd/release/11/2024-01/mms/334423054',
  'http://id.who.int/icd/release/11/2024-01/mms/274880002',
  'http://id.who.int/icd/release/11/2024-01/mms/1296093776',
  'http://id.who.int/icd/release/11/2024-01/mms/868865918',
  'http://id.who.int/icd/release/11/2024-01/mms/1218729044',
  'http://id.who.int/icd/release/11/2024-01/mms/426429380',
  'http://id.who.int/icd/release/11/2024-01/mms/197934298',
  'http://id.who.int/icd/release/11/2024-01/mms/1256772020',
  'http://id.who.int/icd/release/11/2024-01/mms/1639304259',
  'http://id.who.int/icd/release/11/2024-01/mms/1473673350',
  'http://id.who.int/icd/release/11/2024-01/mms/30659757',
  'http://id.who.int/icd/release/11/2024-01/mms/577470983',
  'http://id.who.int/icd/release/11/2024-01/mms/714000734',
  'http://id.who.int/icd/release/11/2024-01/mms/1306203631',
  'http://id.who.int/icd/release/11/2024-01/mms/223744320',
  'http://id.who.int/icd/release/11/2024-01/mms/1843895818',
  'http://id.who.int/icd/release/11/2024-01/mms/435227771',
  'http://id.who.int/icd/release/11/2024-01/mms/850137482',
  'http://id.who.int/icd/release/11/2024-01/mms/1249056269',
  'http://id.who.int/icd/release/11/2024-01/mms/1596590595',
  'http://id.who.int/icd/release/11/2024-01/mms/718687701',
  'http://id.who.int/icd/release/11/2024-01/mms/231358748',
  'http://id.who.int/icd/release/11/2024-01/mms/979408586']



def get_token():
  token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
  client_id = os.getenv("ICS_CLIENT_ID")
  client_secret = os.getenv("ICS_CLIENT_SECRET")
  scope = 'icdapi_access'
  grant_type = 'client_credentials'


  # get the OAUTH2 token

  # set data to post
  payload = {'client_id': client_id,
          'client_secret': client_secret,
            'scope': scope,
            'grant_type': grant_type}


  # make request
  r = requests.post(token_endpoint, data=payload, verify=False).json()
  token = r['access_token']

  return token

def get_json(id, token, apitype="mms"):
  #uri = 'https://id.who.int/icd/entity/1435254666'
  if apitype =="mms":
    url = "https://id.who.int/icd/release/11/2024-01/mms/" + id
  else:
    url = "https://id.who.int/icd/entity/" + id
  # HTTP header fields to set
  headers = {'Authorization':  'Bearer '+token,
            'Accept': 'application/json',
            #'Accept': 'application/ld+json',
            'Accept-Language': 'es',
      'API-Version': 'v2'}

  # make request
  r = requests.get(url, headers=headers, verify=False)

  print(r)
  if r.status_code == 200:
    return r.json()
  elif r.status_code == 401:
    time.sleep(10)
    return get_json(id, token)
  else:
    return 'skip'



for id_prob in master_child:
  token = get_token()
  id_prob = id_prob.split("/")[-1]

  def explore_childs(node):
      id = node.split("/")[-1]
      data = get_json(id, token)
      data_entity = get_json(id, token, apitype="entity") #Needed for synonims


      if data == 'skip':
        return

      # Procesar el nodo actual (por ejemplo, imprimir su información)
      print(f"ID: {id} {data['title']['@value']}")

      output["datetime"].append(datetime.now())
      output["id"].append(id)
      output["api-browser"].append(data['browserUrl'])
      output["api-url"].append(node)
      output["parents"].append([c.split("/")[-1] for c in data.get("parent", [])])
      output["children"].append([c.split("/")[-1] for c in data.get("child", [])] )
      output["cie-code"].append(data.get("code", ""))
      output["title"].append(data['title']['@value'])
      output["entity_title"].append(data_entity["title"]["@value"])
      output["synonyms"].append([s["label"]["@value"] for s in data_entity.get("synonym", [{"label":{"@value": ""}}])])
      output["definition"].append(data.get("definition", {"@value": ""})["@value"])
      output["entity_definition"].append(data_entity.get("definition", {"@value": ""})["@value"])
      output["exclusions"].append([e["label"]["@value"] for e in data.get("exclusion", [{"label":{"@value": ""}}])])

      # I need for each child : [[CODE, Title, URL]]
      children_detailed = []

      # Recorrer los childs del nodo actual
      for child in data.get("child", []):
          child_output = explore_childs(child)
          if child_output:
            child_info = [child_output.get("code", ""), child_output.get("title", {"@value": ""})["@value"], child_output.get("browserUrl", "")]
            children_detailed.append(child_info)

      output["children_human"].append(children_detailed)

      return data

  ###############
  output = {"datetime": [],
            "id": [],
          "api-browser": [],
          "api-url":[],
          "parents": [],
          "children": [],
          "children_human": [],
          "cie-code": [],
          "title": [],
          "entity_title": [],
          "synonyms": [],
          "definition": [],
          "entity_definition": [],
          "exclusions": []}

  # Llamada inicial con el nodo raíz
  _ = explore_childs(f"http://id.who.int/icd/release/11/2024-01/mms/{id_prob}")



  df = pd.DataFrame(output)

  # Fixing the children mess
  # Convert the 'children' column from string to list
 #  df['children'] = df['children'].apply(lambda x: eval(x))

  # Function to retrieve the titles for children
  def get_child_info(row, df):
      child_ids = row['children']
      child_titles = []
      for child_id in child_ids:
          child_row = df[df['id'] == str(child_id)]
          if not child_row.empty:
              child_titles.append([child_row.iloc[0]['cie-code'], child_row.iloc[0]['title'], child_row.iloc[0]['api-browser']])
      return child_titles

  # Function to retrieve the titles for parentd
  # Change
  def get_parents_info(row, df):
      child_ids = row['parents']
      child_titles = []
      for child_id in child_ids:
          child_row = df[df['id'] == str(child_id)]
          if not child_row.empty:
              child_titles.append([child_row.iloc[0]['cie-code'], child_row.iloc[0]['title'], child_row.iloc[0]['api-browser']])
      return child_titles

  # Apply the function to each row to populate the 'children_human' column
  df['children_human'] = df.apply(lambda row: get_child_info(row, df), axis=1)
  df['parents_human'] = df.apply(lambda row: get_parents_info(row, df), axis=1)


  #df["datetime"] = df["datetime"].astype(str)
  df = df.astype(str)
  df.to_json(f'{OUTPUT_FOLDER}/{id_prob}.json', orient='records', lines=True)