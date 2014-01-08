from django.db import models
from django.conf import settings
from elasticsearch import Elasticsearch

# Create your models here.

ELASTICSEARCH_URL = getattr(settings, 'ELASTICSEARCH_URL', 'localhost:9200')
ELASTICSEARCH_INDEX = getattr(settings, 'ELASTICSEARCH_INDEX', 'manifests')

# Connect to elasticsearch db
def get_connection():
    return Elasticsearch(ELASTICSEARCH_URL)

# Gets the content of a manifest, returns JSON
def get_manifest(manifest_id):
    es = get_connection()
    return es.get(index=ELASTICSEARCH_INDEX, doc_type="manifest", id=manifest_id)["_source"]

# Inserts JSON document into elasticsearch with the given manifest_id
# Either adds new document or replaces existing document
def add_or_update_manifest(manifest_id, document):
    es = get_connection()
    es.index(index=ELASTICSEARCH_INDEX, doc_type="manifest", id=manifest_id, body=document)

# Deletes manifest from elasticsearch (need to refresh index?)
def delete_manifest(manifest_id):
    es = get_connection()
    es.delete(index=ELASTICSEARCH_INDEX, doc_type="manifest", id=manifest_id)

# Checks if manifest exists in elasticsearch, returns boolean
def manifest_exists(manifest_id):
    es = get_connection()
    return es.exists(index=ELASTICSEARCH_INDEX, doc_type="manifest", id=manifest_id)
