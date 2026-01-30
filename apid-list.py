import os
import time
from datetime import datetime
from elasticsearch import Elasticsearch
from dotenv import load_dotenv


########################################
def current_list():
    query = { 
        "match_all" : {}
     }
    client = Elasticsearch(ES_URI, api_key=ES_API_KEY,verify_certs=False, ssl_show_warn=False)
    resp = client.search(index=ES_APIDISCOVER_INDEX, size=maxrecords, query=query)
    documents = []
    for hit in resp["hits"]["hits"]:
        uri = hit["_source"]["uri"]
        method = hit["_source"]["method"]
        return_string  = method + " " + uri
        documents.append(return_string)
    unique_values_set = set(documents)
    unique_values_list = list(unique_values_set)
    return unique_values_list
########################################

def check_if_es_index_exists(index_name):
    client = Elasticsearch(ES_URI, api_key=ES_API_KEY,verify_certs=False, ssl_show_warn=False)
    return client.indices.exists(index=index_name)
########################################
# Main
load_dotenv()
interval = int(os.getenv('INTERVAL', 20))
timerange = os.getenv('TIMERANGE', '500s')
maxrecords = int(os.getenv('MAXRECORDS', 500))
min_violation_rating = int(os.getenv('MIN_VIOLATION_RATING', 0))
ES_URI = os.getenv('ES_URI', 'https://127.0.0.1:9200/')
ES_LOG_INDEX = os.getenv('ES_LOG_INDEX', 'f5waf-*')
ES_APIDISCOVER_INDEX = os.getenv('ES_APIDISCOVER_INDEX', 'apidiscover-app1')
ES_API_KEY = os.getenv('ES_API_KEY', 'eVdCQjJwc0JMMVJOS3lDbEtRcHk6SDNNT3Y0TWlRSWVTU1BTbEJEN0xPQQ==')

if not check_if_es_index_exists(ES_APIDISCOVER_INDEX):
    print("Elasticsearch index " + ES_APIDISCOVER_INDEX + " does not exist. Please check again.")
    exit(1)

print("Existing API logged in " +  ES_APIDISCOVER_INDEX)
current_response = current_list()

if len(current_response) > 0:
    for item in current_response:
        print(item)
else:
    print("No recorded APIs")
