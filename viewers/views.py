from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import json
import urllib3
import certifi

def view(request, viewer_type, viewer_version='v2'):
	viewerTemplate = ''
	manifestList = {}

	if request.GET.get('collection'):
		manifestList = loadCollection(request.GET.get('collection'))

	if (viewer_type == 'mirador'):
		if (viewer_version == 'v2'):
			viewerTemplate = 'viewers/mirador-v2.html'
		elif (viewer_version == 'v3'):
			viewerTemplate = 'viewers/mirador-v3.html'
		else:
			viewerTemplate = 'viewers/mirador-v2.html'

	else:
		viewerTemplate = 'viewers/mirador-v2.html'
	
	return render(request, viewerTemplate, {'manifestList': manifestList})

def loadCollection(collection_url):
	manifestList = {}
	
	try:
		http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
		response = http.request('GET', collection_url)
		data = response.data
		collection = json.loads(data.decode('utf8'))
		
		
		for manifest in collection["manifests"]:
			manifestList.update({manifest['@id']: {'provider': ''}})

		return json.dumps(manifestList)

	except Exception:
		print('Bad collection URL: ' + collection_url)
		
		return json.dumps(manifestList)