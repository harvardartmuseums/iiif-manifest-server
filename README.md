# IIIF Manifest Server

This is a server for creating and delivering IIIF manifests that conform to the specification for Presentation API v2. It sits on top of the Harvard Art Museums API.  

The server is configured to run over HTTPS in staging and production environments.  

## Requirements

* Python 3.4.3
* Elasticsearch

## Configuration

This application requires the following environment variables.  

```
ELASTICSEARCH_URL = localhost:9200
ELASTICSEARCH_INDEX = manifests
API_KEY = 000000-00000-00000-000000-000000
PYTHON_DJANGO_SECRET_KEY = SOME_LONG_SET_OF_RANDOM_CHARACTERS
DJANGO_DEBUG = False
```

### Create a virtual environment
```
cd YOUR_PROJECT_FOLDER
virtualenv venv
```

### Activate the virtual environment
```
venv\Scripts\activate.bat
```

### Install dependencies  
```
pip install -r requirements.txt
```

### Start the server
```
py manage.py runserver 0.0.0.0:5000
```