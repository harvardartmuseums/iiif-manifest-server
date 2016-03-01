#!/usr/bin/python

import json, sys
import urllib3

imageHash = {}

imageUriBase = "http://ids.lib.harvard.edu/ids/iiif/"
imageUriSuffix = "/full/full/0/native.jpg"
imageInfoSuffix = "/info.json"
manifestUriBase = ""
serviceBase = imageUriBase
profileLevel = "http://library.stanford.edu/iiif/image-api/1.1/conformance.html#level1"
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

	manifestLabel = huam_json["title"]
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
	images = huam_json["images"]

	#print "Images list", images

	canvasInfo = []
	for (counter, im) in enumerate(images):
		info = {}
		if im["publiccaption"]:
			info['label'] = im["publiccaption"]
		else:
			info['label'] = str(counter+1)
			
		info['image'] = im["idsid"]
		info['baseuri'] = im["iiifbaseuri"]
		canvasInfo.append(info)

	# start building the manifest
	mfjson = {
		"@context":"http://www.shared-canvas.org/ns/context.json",
		"@id": manifest_uri,
		"@type":"sc:Manifest",
		"label":manifestLabel,
		"attribution":attribution,
		"logo":logo,
		"description":huam_json["description"],
		"within": "http://www.harvardartmuseums.org/collections",
		"sequences": [
			{
				"@id": manifest_uri + "/sequence/normal.json",
				"@type": "sc:Sequence",
				"viewingHint":viewingHint,
			}
		]
	}

	# can add metadata key/value pairs
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

	mfjson["metadata"] = metadata


	canvases = []

	for cvs in canvasInfo:
		try: 
			response = http.request('GET', cvs['baseuri'] + imageInfoSuffix)
			huam_image = response.data

			infojson = json.loads(huam_image.decode('utf-8'))
			cvsjson = {
				"@id": manifest_uri + "/canvas/canvas-%s.json" % cvs['image'],
				"@type": "sc:Canvas",
				"label": cvs['label'],
				"height": infojson['height'],
				"width": infojson['width'],
				"images": [
					{
						"@id":manifest_uri+"/annotation/anno-%s.json" % cvs['image'],
						"@type": "oa:Annotation",
						"motivation": "sc:painting",
						"resource": {
							"@id": imageUriBase + cvs['image'] + imageUriSuffix,
							"@type": "dctypes:Image",
							"format":"image/jpeg",
							"height": infojson['height'],
							"width": infojson['width'],
							"service": { 
							  "@id": imageUriBase + cvs['image'],
							  "profile": profileLevel
							},
						},
						"on": manifest_uri + "/canvas/canvas-%s.json" % cvs['image']
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
