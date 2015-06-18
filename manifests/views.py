from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from manifests import huam
from manifests import models
import json
import urllib3

# Create your views here.

HUAM_API_URL = "http://api.harvardartmuseums.org/object/"
HUAM_API_KEY = "7a519500-933a-11e3-b8ce-c9be9b362aa7"


# Returns a IIIF manifest of a METS, MODS or HUAM JSON object
# Checks if DB has it, otherwise creates it
def manifest(request, document_type, document_id):
    # parts = document_id.split(":")
    host = request.META['HTTP_HOST']
    source = document_type
    id = document_id
    (success, response_doc, real_id, real_source) = get_manifest(id, source, False, host)
    if success:
        response = HttpResponse(response_doc)
        add_headers(response)
        return response
    else:
        return response_doc # 404 HttpResponse
            
# Delete any document from db
def delete(request, document_type, document_id):
    # Check if manifest exists
    source = document_type
    id = document_id
    has_manifest = models.manifest_exists(id, source)

    if has_manifest:
        models.delete_manifest(id, source)
        return HttpResponse("Document ID %s has been deleted" % document_id)
    else:
        return HttpResponse("Document ID %s does not exist in the database" % document_id, status=404)

# Force refresh a single document
# Pull METS, MODS or HUAM JSON, rerun conversion script, and store in db
def refresh(request, document_type, document_id):
    host = request.META['HTTP_HOST']
    source = document_type
    id = document_id
    (success, response_doc, real_id, real_source) = get_manifest(id, source, True, host)

    if success:
        response = HttpResponse(response_doc)
        add_headers(response)
        return response
    else:
        return response_doc # This is actually the 404 HttpResponse, so return and end the function

# Force refresh all records from a single source
# WARNING: this could take a long time
# Pull all METS, MODS or HUAM JSON, rerun conversion script, and store in db
def refresh_by_source(request, document_type):
    document_ids = models.get_all_manifest_ids_with_type(document_type)
    counter = 0
    host = request.META['HTTP_HOST']
    for id in document_ids:
        (success, response_doc, real_id, real_source) = get_manifest(id, document_type, True,  host)
        if success:
            counter = counter + 1

    response = HttpResponse("Refreshed %s out of %s total documents in %s" % (counter, len(document_ids), document_type))
    return response

## HELPER FUNCTIONS ##
# Gets HUAM JSON from HUAM API
def get_huam(document_id, source):
    huam_url = HUAM_API_URL+document_id+"?apikey="+HUAM_API_KEY

    http = urllib3.PoolManager()
    response = http.request('GET', huam_url)

    huam = response.data
    return (True, huam.decode('utf8'))

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
        (success, response) = get_huam(document_id, source)

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
