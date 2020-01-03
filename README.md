# IIIF Manifest Server

This is a server for creating and delivering IIIF manifests that conform to the specification for [Presentation API 2.1](http://iiif.io/api/presentation/2.1/). It sits on top of the Harvard Art Museums API.  

The server is configured to run over HTTPS in staging and production environments.  

## Requirements

* Python 3.*
* Elasticsearch

## Configuration

This application requires the following environment variables.  

```
ELASTICSEARCH_URL = http://localhost:9200
ELASTICSEARCH_URL_STAGING = http://...
ELASTICSEARCH_URL_DEV  = http://...
ELASTICSEARCH_INDEX = manifests
HAM_API_KEY = 000000-00000-00000-000000-000000
HAM_API_URL = https://api.harvardartmuseums.org
PYTHON_DJANGO_SECRET_KEY = SOME_LONG_SET_OF_RANDOM_CHARACTERS
DJANGO_DEBUG = False
```

Get a HAM API key at [https://www.harvardartmuseums.org/collections/api](https://www.harvardartmuseums.org/collections/api) and set the `HAM_API_KEY` variable with your new key.

### Clone the repository
```
> git clone https://github.com/harvardartmuseums/iiif-manifest-server.git
```

### Create a virtual environment
We recommend creating a virtual environment with [Virtualenv](https://pypi.org/project/virtualenv/) and running everything within it.

```
> cd iiif-manifest-server
> virtualenv venv
```

### Activate the virtual environment
```
> venv\Scripts\activate.bat
```

### Install dependencies  
```
> pip install -r requirements.txt
```

## Usage

### Start the server
```
> python manage.py runserver 0.0.0.0:5000
```

Open a web browser and point it to http://localhost:5000/collections/top.