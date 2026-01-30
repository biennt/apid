import os
import time
from datetime import datetime
from elasticsearch import Elasticsearch
from dotenv import load_dotenv


########################################
def query_es():
    query = { 
         "range": {"violation_rating": {"gte": min_violation_rating}},
         "range": {"@timestamp": {"gte": "now-" + timerange}}
     }
    client = Elasticsearch(ES_URI, api_key=ES_API_KEY,verify_certs=False, ssl_show_warn=False)
    resp = client.search(index=ES_LOG_INDEX, size=maxrecords, query=query)
    documents = []
    for hit in resp["hits"]["hits"]:
        uri = hit["_source"]["uri"]
        method = hit["_source"]["method"]
        response_code = hit["_source"]["response_code"]
        if (response_code.startswith('1') or response_code.startswith('2')):
            return_string  = method + " " + uri
            documents.append(return_string)
    unique_values_set = set(documents)
    unique_values_list = list(unique_values_set)
    return unique_values_list
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

def put_api_into_es(documents):
    client = Elasticsearch(ES_URI, api_key=ES_API_KEY,verify_certs=False, ssl_show_warn=False)
    for item in documents:
        time_now = datetime.now()
        doc = {
                'timestamp': time_now.strftime('%Y-%m-%dT%H:%M:%S+07:00')
        }
        doc['method'] = item.split(" ")[0]
        doc['uri'] = item.split(" ")[1]
        print(doc)
        try:
            res = client.index(index=ES_APIDISCOVER_INDEX, body=doc)
            print("result: {}".format(res['result']))
        except Exception as e:
            print("Error connecting to Elasticsearch")
            print(e)
        print("--------------------------------------")

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
ES_API_KEY = os.getenv('ES_API_KEY', '_your_key_here_')

if not check_if_es_index_exists(ES_LOG_INDEX):
    print("Elasticsearch index " + ES_LOG_INDEX + " does not exist. Please check again.")
    exit(1)

print("API Discovery starting..")
while True:
    es_response = query_es()
    if len(es_response) > 0:
        print("New logged API requests found in " + ES_LOG_INDEX)
        if not check_if_es_index_exists(ES_APIDISCOVER_INDEX):
            print("Elasticsearch index " + ES_APIDISCOVER_INDEX + " does not exist. Creating new index...")
            current_response = []
        else:
            print("Existing API logged in " +  ES_APIDISCOVER_INDEX)
            current_response = current_list()
        if len(current_response) > 0:
                new_apis = list(set(es_response) - set(current_response))
        else:
                new_apis = es_response
        print("New API requests to be added into " + ES_APIDISCOVER_INDEX + ":")
        print(new_apis)
        put_api_into_es(new_apis)
    else:
        print('!!! There is no recorded API requests !!!')

    print(f"Sleep for {interval} seconds...")
    time.sleep(interval)
    
