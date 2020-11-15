from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'mainApp/index.html')


def monitor(request, rover_id):
    return HttpResponse("<h1>Monitoring room for Rover ID: <br/><br/>" + rover_id + "</h1>")
