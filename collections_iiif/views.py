from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from collections_iiif import huam
# from collections import models
import json
import urllib3
import certifi

# Create your views here.

HUAM_API_URL = getattr(settings, 'HAM_API_URL', '')
HUAM_API_KEY = getattr(settings, 'HAM_API_KEY', '')


# Returns a IIIF collection of HAM manifests
def collection(request, document_type):
    host = request.META['HTTP_HOST']
    protocol = "https" if request.is_secure() else "http"
    source = document_type

    if 'page' in request.GET:
        page = int(request.GET['page'])
    else: 
        page = 0

    (success, response_doc, real_id, real_source) = get_collection(source, page, False, host, protocol)
    if success:
        response = HttpResponse(response_doc)
        add_headers(response)
        return response
    else:
        return response_doc # 404 HttpResponse
            
## HELPER FUNCTIONS ##
# Gets HUAM JSON from HUAM API
def get_huam(source, page):
    huam_url = HUAM_API_URL + "%s?apikey=%s&hasimage=1&fields=objectid,title&size=100&page=%s" % (source, HUAM_API_KEY, page)

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    response = http.request('GET', huam_url)
    huam = response.data

    if (huam.decode('utf8')==''):
        return (False, HttpResponse("The document ID %s does not exist" % document_id, status=404))

    return (True, huam.decode('utf8'))

def get_huam_gallery(document_id, source):
    huam_url = HUAM_API_URL + "%s/%s?apikey=%s" % (source, document_id, HUAM_API_KEY)

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    response = http.request('GET', huam_url)
    huam = response.data

    # Get the objects in the gallery
    huam_url = HUAM_API_URL + "object?apikey=%s&size=100&hasimage=1&fields=objectid,objectnumber,title,images&gallery=%s" % (HUAM_API_KEY, document_id)
    response = http.request('GET', huam_url)
    objects = response.data
    o = json.loads(objects.decode('utf8'))

    # Append the objects to the gallery
    j = json.loads(huam.decode('utf8'))
    j["objects"] = o["records"]

    if (huam.decode('utf8')==''):
        return (False, HttpResponse("The document ID %s does not exist" % document_id, status=404))

    return (True, json.dumps(j))

# Adds headers to Response for returning JSON that other Mirador instances can access
def add_headers(response):
    response["Access-Control-Allow-Origin"] = "*"
    response["Content-Type"] = "application/ld+json"
    return response

# Uses other helper methods to create JSON
def get_manifest(document_id, source, force_refresh, host):
    # Check if manifest exists
    has_manifest = models.manifest_exists(document_id, source)

    ## TODO: add last modified check

    if not has_manifest or force_refresh:
        if source == "object":
            (success, response) = get_huam(document_id, source)
        elif source == "gallery":
            (success, response) = get_huam_gallery(document_id, source)

        if not success:
            return (success, response, document_id, source) # This is actually the 404 HttpResponse, so return and end the function
 
        # Convert to shared canvas model if successful
        converted_json = huam.main(response, document_id, source, host)

        # Store to elasticsearch
        models.add_or_update_manifest(document_id, converted_json, source)

        return (success, converted_json, document_id, source)
    else:
        # return JSON from db
        json_doc = models.get_manifest(document_id, source)
        return (True, json.dumps(json_doc), document_id, source)

# Uses other helper methods to create JSON
def get_collection(source, page, force_refresh, host, protocol):

    if source == "object":
        (success, response) = get_huam(source, page)
    elif source == "gallery":
        (success, response) = get_huam_gallery(source, page)

    if not success:
        return (success, response, page, source) # This is actually the 404 HttpResponse, so return and end the function

    # Convert to shared canvas model if successful
    converted_json = huam.collection(response, source, host, protocol, page)

    return (success, converted_json, page, source)
