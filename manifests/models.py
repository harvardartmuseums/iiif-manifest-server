from django.db import models
from django.conf import settings
from urllib.parse import urlparse
from elasticsearch import Elasticsearch

# Create your models here.

ELASTICSEARCH_URL = getattr(settings, 'ELASTICSEARCH_URL', 'localhost:9200')
ELASTICSEARCH_INDEX = getattr(settings, 'ELASTICSEARCH_INDEX', 'manifests')
ELASTIC_CLOUD_ID = getattr(settings, 'ELASTIC_CLOUD_ID', '')
ELASTIC_CLOUD_USERNAME = getattr(settings, 'ELASTIC_CLOUD_USERNAME', '')
ELASTIC_CLOUD_PASSWORD = getattr(settings, 'ELASTIC_CLOUD_PASSWORD', '')


# Connect to elasticsearch db
def get_connection():
    if ELASTIC_CLOUD_ID is not None: 
        return Elasticsearch(cloud_id=ELASTIC_CLOUD_ID, http_auth=(ELASTIC_CLOUD_USERNAME, ELASTIC_CLOUD_PASSWORD))

    else:
        server_options = urlparse(ELASTICSEARCH_URL)

        if server_options.username is not None:
            return Elasticsearch(host=server_options.hostname, use_ssl=True, http_auth=(server_options.username, server_options.password), port=server_options.port)
        else:
            return Elasticsearch(host=server_options.hostname, port=server_options.port)

def make_doc_id(id, entity_type):
    return f"manifest:{entity_type}:{id}"

# Gets the content of a manifest, returns JSON
def get_manifest(manifest_id, source):
    es = get_connection()
    return es.get(index=ELASTICSEARCH_INDEX, id=make_doc_id(manifest_id, source))["_source"]

# Inserts JSON document into elasticsearch with the given manifest_id
# Either adds new document or replaces existing document
def add_or_update_manifest(manifest_id, document, source):
    es = get_connection()
    es.index(index=ELASTICSEARCH_INDEX, id=make_doc_id(manifest_id, source), body=document)

# Deletes manifest from elasticsearch (need to refresh index?)
def delete_manifest(manifest_id, source):
    es = get_connection()
    es.delete(index=ELASTICSEARCH_INDEX, id=make_doc_id(manifest_id, source))

# Checks if manifest exists in elasticsearch, returns boolean
def manifest_exists(manifest_id, source):
    es = get_connection()
    return es.exists(index=ELASTICSEARCH_INDEX, id=make_doc_id(manifest_id, source))

def get_all_manifest_ids_with_type(source):
    es = get_connection()
    results = es.search(index="manifests", fields="[]")
    ids = []
    for r in results["hits"]["hits"]:
        ids.append(str(r["_id"]))
    return ids

def get_all_manifest_ids():
    es = get_connection()
    results = es.search(index="manifests", fields="[]")
    ids = []
    for r in results["hits"]["hits"]:
        ids.append(str(r["_id"]))
    return ids

def get_manifest_title(manifest_id, source):
    es = get_connection()
    return es.get(index=ELASTICSEARCH_INDEX, id=make_doc_id(manifest_id, source))["_source"]["label"]
