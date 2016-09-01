#!/usr/bin/python

import json, sys
import urllib3

imageHash = {}

imageUriBase = "https://ids.lib.harvard.edu/ids/iiif/"
imageUriSuffix = "/full/full/0/native.jpg"
imageInfoSuffix = "/info.json"
manifestUriBase = ""
serviceBase = imageUriBase
profileLevel = "http://library.stanford.edu/iiif/image-api/1.1/conformance.html#level1"
imageServiceContext = "http://iiif.io/api/image/1/context.json"
attributionBase = "Harvard Art Museums"
logo = "http://www.harvardartmuseums.org/assets/images/logo.png"

http = urllib3.PoolManager()

def main(data, document_id, source, host):
	global imageHash 
	imageHash = {}
	global manifestUriBase
	manifestUriBase = "http://%s/manifests/" % host

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
	print(manifest_uri)

	## List of different image labels
	## @displayLabel = Full Image, @note = Color digital image available, @note = Harvard Map Collection copy image
	if source in ["object", "exhibition"]:
		images = huam_json["images"]
	elif source == "gallery":
		images = huam_json["objects"]

	# print("Images list", images)

	# Determine the primary rendering url
	if source in ["object", "exhibition"]:
		if huam_json["url"]:
			rendering_url = huam_json["url"]
	elif source == "gallery":
		rendering_url = "http://www.harvardartmuseums.org/visit/floor-plan/%s/%s" % (huam_json["floor"], huam_json["gallerynumber"])

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

		if source in ["object", "exhibition"]:
			info['image'] = im["idsid"]
			info['baseuri'] = im["iiifbaseuri"]
		elif source == "gallery":
			info['image'] = im["images"][0]["idsid"]
			info['baseuri'] = im["images"][0]["iiifbaseuri"]

		canvasInfo.append(info)

	# start building the manifest
	mfjson = {
		"@context":"http://iiif.io/api/presentation/2/context.json",
		"@id": manifest_uri,
		"@type":"sc:Manifest",
		"label":manifestLabel,
		"attribution":attribution,
		"logo":logo,
		"description":manifestDescription,
		"within": "http://www.harvardartmuseums.org/collections",
		"sequences": [
			{
				"@id": manifest_uri + "/sequence/normal",
				"@type": "sc:Sequence",
				"viewingHint":viewingHint,
			}
		],
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

			infojson = json.loads(huam_image.decode('utf-8'))
			cvsjson = {
				"@id": manifest_uri + "/canvas/canvas-%s" % cvs['image'],
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
							"@id": imageUriBase + cvs['image'] + imageUriSuffix,
							"@type": "dctypes:Image",
							"format":"image/jpeg",
							"height": infojson['height'],
							"width": infojson['width'],
							"service": { 
							  "@context": imageServiceContext,
							  "@id": imageUriBase + cvs['image'],
							  "profile": profileLevel
							},
						},
						"on": manifest_uri + "/canvas/canvas-%s" % cvs['image']
					}
				]
			}
			canvases.append(cvsjson)
		except Exception:
			print("Bad IDS URL: " + cvs['baseuri'])

	mfjson['sequences'][0]['canvases'] = canvases
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
