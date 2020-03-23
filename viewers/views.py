from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

def view(request, viewer_type, viewer_version='v2'):
	if (viewer_type == 'mirador'):
		if (viewer_version == 'v2'):
			return render(request, 'viewers/mirador-v2.html')
		elif (viewer_version == 'v3'):
			return render(request, 'viewers/mirador-v3.html')
		else:
			return render(request, 'viewers/mirador-v2.html')

	else:
		return render(request, 'viewers/mirador-v2.html')
