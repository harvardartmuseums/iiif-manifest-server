# IIIF Manifest Server

This is a server for creating and delivering IIIF manifests. It sits on top of the Harvard Art Museums API.  

## Requirements

* Python 3.4.3
* Elasticsearch

## Configuration

This application requires the following environment variables.  

```
ELASTICSEARCH_URL = localhost:9200
ELASTICSEARCH_INDEX = manifests
API_KEY = 000000-00000-00000-000000-000000
```