from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

def view(request, viewer_type):
	if (viewer_type == "mirador"):
		return render(request, 'viewers/mirador.html')
