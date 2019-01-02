#!/usr/bin/python

import json, sys
import urllib3
import certifi
from django.conf import settings

imageHash = {}


HAM_API_URL = getattr(settings, 'HAM_API_URL', '')

hamAnnotationUriBase = HAM_API_URL + "annotation/"
imageUriBase = "https://ids.lib.harvard.edu/ids/iiif/"
imageUriSuffix = "/full/full/0/native.jpg"
imageInfoSuffix = "/info.json"
manifestUriBase = ""
serviceBase = imageUriBase
profileLevel = "http://iiif.io/api/image/2/level2.json"
imageServiceContext = "http://iiif.io/api/image/2/context.json"
presentationServiceContext = "http://iiif.io/api/presentation/2/context.json"
listServiceContext = "http://www.shared-canvas.org/ns/context.json"
attributionBase = "Harvard Art Museums"
logoUriBase = "https://ids.lib.harvard.edu/ids/iiif/437958013"

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

def main(data, document_id, source, host):
	global imageHash 
	imageHash = {}
	global manifestUriBase
	manifestUriBase = "https://%s/manifests/" % host

	huam_json = json.loads(data)
	attribution = attributionBase

	if source == "gallery":
		manifestLabel = "%s, Gallery %s, Level %s" % (huam_json["name"], huam_json["gallerynumber"], huam_json["floor"])
		manifestDescription = huam_json["theme"] if huam_json["theme"] else ""
	else:
		manifestLabel = huam_json["title"]
		manifestDescription = huam_json["description"] if huam_json["description"] else ""
	
	#genres = dom.xpath('/mods:mods/mods:genre/text()', namespaces=ALLNS)
	#TODO: determine if there are different viewingHints for HUAM data
	genres = []
	if "handscroll" in genres:
		viewingHint = "continuous"
	else:
		# XXX Put in other mappings here
		viewingHint = "individuals"
	## TODO: add viewingDirection

	manifest_uri = manifestUriBase + "%s/%s" % (source, document_id)

	## List of different image labels
	## @displayLabel = Full Image, @note = Color digital image available, @note = Harvard Map Collection copy image
	images = []
	if source in ["object", "exhibition"]:
		if 'images' in huam_json:
			images = huam_json["images"]
	elif source == "gallery":
		if 'objects' in huam_json:
			images = huam_json["objects"]

	# print("Images list", images)

	# Determine the primary rendering url
	rendering_url = ""
	if source in ["object", "exhibition", "gallery"]:
		if huam_json["url"]:
			rendering_url = huam_json["url"]
	
	thumbnail_uri = ""


	canvasInfo = []
	for (counter, im) in enumerate(images):
		info = {}

		if source == "object":
			if im["publiccaption"]:
				info['label'] = im["publiccaption"]
			else:
				info['label'] = str(counter+1)
		elif source == "exhibition":
			if im["caption"]:
				info['label'] = im["caption"]
			else:
				info['label'] = str(counter+1)
		elif source == "gallery":
			if im["title"]:
				info['label'] = "%s, %s" % (im["title"], im["objectnumber"])
			else:
				info['label'] = str(counter+1)

		info['image'] = ""
		info['baseuri'] = ""
		if source in ["object", "exhibition"]:
			info['image'] = im["idsid"]
			info['baseuri'] = im["iiifbaseuri"]
		elif source == "gallery":
			if len(im["images"]) > 0:
				info['image'] = im["images"][0]["idsid"]
				info['baseuri'] = im["images"][0]["iiifbaseuri"]

		canvasInfo.append(info)

		# Get the URI of the first image to use as the manifest thumbnail
		thumbnail_uri = ""
		if counter == 0:
			if source in ["object", "exhibition"]:
				thumbnail_uri = im["iiifbaseuri"]
			elif source == "gallery":
				if len(im["images"]) > 0:
					thumbnail_uri = im["images"][0]["iiifbaseuri"]

	# start building the manifest
	mfjson = {
		"@context":presentationServiceContext,
		"@id": manifest_uri,
		"@type":"sc:Manifest",
		"label":manifestLabel,
		"attribution":attribution,
		"logo": {
			"@id": logoUriBase + "/full/!800,800/0/native.jpg",
			"service": {
				"@context": imageServiceContext,
				"@id": logoUriBase,
				"profile": profileLevel
			} 
		},
		"description":manifestDescription,
		"within": "https://www.harvardartmuseums.org/collections",
		"sequences": [
			{
				"@id": manifest_uri + "/sequence/normal",
				"@type": "sc:Sequence",
				"viewingHint":viewingHint,
			}
		],
		"thumbnail": {
			"@id": thumbnail_uri + "/full/!170,170/0/native.jpg",
			"service": {
				"@context": imageServiceContext,
				"@id": thumbnail_uri,
				"profile": profileLevel
			} 
		},
		"rendering": {
			"@id": rendering_url,
			"label": "Full record view",
			"format": "text/html"			
		}
	}

	# can add metadata key/value pairs
	if source == "object":
		metadata = [
			{
				"label":"Date",
				"value":huam_json["dated"]
			},
			{
				"label":"Classification",
				"value":huam_json["classification"]
			},
			{
				"label":"Credit Line",
				"value":huam_json["creditline"]
			},
			{
				"label":"Object Number", 
				"value":huam_json["objectnumber"]
			}
		]

		if "people" in huam_json:
			people = []
			for person in huam_json["people"]:
				p = "%s: %s" % (person["role"], person["displayname"])
				if person["culture"]:
					p = p + ", " + person["culture"]
				if person["displaydate"]:
					p = p + ", " + person["displaydate"]

				people.append(p)

			metadata.append({
				"label":"People",
				"value":people
			})

		if huam_json["medium"]:
			metadata.append({
				"label":"Medium",
				"value":huam_json["medium"]
			})

		if huam_json["technique"]:
			metadata.append({
				"label":"Technique",
				"value":huam_json["technique"]
			})

		if huam_json["dimensions"]:
			metadata.append({
				"label":"Dimensions",
				"value":huam_json["dimensions"]
			})

		if huam_json["provenance"]:
			metadata.append({
				"label":"Provenance",
				"value":huam_json["provenance"]
			})


		if huam_json["copyright"]:
			metadata.append({
				"label":"Copyright",
				"value":huam_json["copyright"]
			})
	elif source == "exhibition":
		metadata = [
			{
				"label":"Title",
				"value": huam_json["title"]
			},
			{
				"label":"Begin Date",
				"value": huam_json["begindate"]
			},
			{
				"label":"End Date",
				"value": huam_json["enddate"]
			},
		]
	elif source == "gallery":
		metadata = [
			{
				"label":"Gallery Number",
				"value": huam_json["gallerynumber"]
			},
			{
				"label":"Name",
				"value": huam_json["name"]
			}
		]		

		if huam_json["theme"]:
			metadata.append({
				"label":"Theme",
				"value":huam_json["theme"]
			})

		if huam_json["labeltext"]:
			metadata.append({
				"label":"Description",
				"value":huam_json["labeltext"]
			})

	mfjson["metadata"] = metadata


	canvases = []

	for cvs in canvasInfo:
		try: 
			response = http.request('GET', cvs['baseuri'] + imageInfoSuffix)
			huam_image = response.data

			canvas_uri = manifest_uri + "/canvas/canvas-%s" % cvs['image']
			list_url = manifest_uri + "/list/%s" % cvs['image']

			infojson = json.loads(huam_image.decode('utf-8'))
			cvsjson = {
				"@id": canvas_uri,
				"@type": "sc:Canvas",
				"label": cvs['label'],
				"height": infojson['height'],
				"width": infojson['width'],
				"images": [
					{
						"@id":manifest_uri+"/annotation/anno-%s" % cvs['image'],
						"@type": "oa:Annotation",
						"motivation": "sc:painting",
						"resource": {
							"@id": imageUriBase + str(cvs['image']) + imageUriSuffix,
							"@type": "dctypes:Image",
							"format":"image/jpeg",
							"height": infojson['height'],
							"width": infojson['width'],
							"service": { 
							  "@context": imageServiceContext,
							  "@id": imageUriBase + str(cvs['image']),
							  "profile": profileLevel
							},
						},
						"on": canvas_uri
					}
				],
				"otherContent": [
					{
						"@id": list_url,
						"@type": "sc:AnnotationList"
					}
				]	
			}
			canvases.append(cvsjson)
		except Exception:
			print("Bad IDS URL: " + cvs['baseuri'])

	mfjson['sequences'][0]['canvases'] = canvases
	output = json.dumps(mfjson, indent=4, sort_keys=True)
	return output

def list(data, document_id, canvas_id, source, host, protocol):
	global manifestUriBase
	manifestUriBase = "%s://%s/manifests/" % (protocol, host)
	manifest_uri = manifestUriBase + "%s/%s" % (source, document_id)
	canvas_uri = manifest_uri + "/canvas/canvas-%s" % (canvas_id)

	listUriBase = manifest_uri + "/list/"
	list_uri = listUriBase + "%s" % (canvas_id)

	annotationUriBase = "%s://%s/annotations/" % (protocol, host)
	annotation_uri = annotationUriBase + "%s"

	huam_json = json.loads(data)

	# prepare the members records
	members = []

	for record in huam_json["records"]:
		body = record["body"]
		if record["source"]:
			body  += "<p>Generated by %s</p>" % record["source"] 

		member = {
            "@id": annotation_uri % (record["id"]),
            "@context": "http://iiif.io/api/presentation/2/context.json",
            "@type": "oa:Annotation",
            "motivation": [
                "oa:commenting"
            ],
            "resource": [
                {
                    "@type": "dctypes:Text",
                    "format": "text/html",
                    "chars": body
                }
            ],
            "on": {
                "@type": "oa:SpecificResource",
                "full": canvas_uri,
                "selector": {
                    "@type": "oa:FragmentSelector",
                    "value": record["selectors"][0]["value"]
                },
                "within": {
                    "@id": manifest_uri,
                    "@type": "sc:Manifest"
                }
            }
        }
		members.append(member)

	# start building the list
	mfjson = {		
		"@context": listServiceContext,
		"@id": list_uri,
		"@type":"sc:AnnotationList",
        "resources": members		
	}


	output = json.dumps(mfjson, indent=4, sort_keys=True)
	return output


if __name__ == "__main__":
	if (len(sys.argv) < 5):
		sys.stderr.write('not enough args\n')
		sys.stderr.write('usage: mods.py [input] [manifest_identifier] [source] [host]\n')
		sys.exit(0)

	inputfile = sys.argv[1]
	document_id = sys.argv[2]
	source = sys.argv[3]
	outputfile = source + '-' + document_id +  ".json"
	host = sys.argv[4]

	fh = open(inputfile)
	data = fh.read()
	fh.close()

	output = main(data, document_id, source, host)
	fh = file(outputfile, 'w')
	fh.write(output)
	fh.close()
