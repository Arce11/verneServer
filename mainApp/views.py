from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError, \
    JsonResponse, Http404
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import io
from .models import Rover, Session
from .serializers import RoverSerializer, SessionSerializer


def index(request):
    return render(request, 'mainApp/index.html')


def monitor(request, rover_id):
    try:
        rover = Rover.objects.get(rover_id=rover_id)  # Only to check if it exists
        session_list = Session.objects.filter(rover_id=rover_id).order_by("-start_time")[:10]
        file_list = [{"filename": s.log_filename, "url": s.log.url} for s in session_list]
        return render(request, 'mainApp/monitor.html', context={'rover_id': rover_id, 'file_list': file_list})
    except Rover.DoesNotExist:
        error_message = "¡No conozco a ningún rover con este identificador!"
        return render(request, 'mainApp/error.html', context={'error_message': error_message})
    except Session.DoesNotExist:
        error_message = "Existe un error en los datos almacenados de este rover..."
        return render(request, 'mainApp/error.html', context={'error_message': error_message})


def monitor_old(request, rover_id):
    try:
        response = "<h1>Monitoring room for Rover ID: <br/><br/>" + rover_id + "</h1>"
        rover = Rover.objects.get(rover_id=rover_id)
        if rover.last_session is None:
            response += "<br/><br/> <h2>NO LAST SESSION DOCUMENTED</h2>"
        else:
            session = Session.objects.get(session_id=rover.last_session)
            date = session.start_time
            response += f"<br/><br/> <h2>Last session start date: {date:%Y-%m-%d %H:%M:%S} (UTC) </h2>"
    except Rover.DoesNotExist:
        error_message = "¡No conozco a ningún rover con este identificador!"
        return render(request, 'mainApp/error.html', context={'error_message': error_message})
    except Session.DoesNotExist:
        error_message = "Existe un error en los datos almacenados de este rover..."
        return render(request, 'mainApp/error.html', context={'error_message': error_message})
    return HttpResponse(response)


class RoverAPI(View):
    """
    List all rovers, or create a new rover.
    """
    def get(self, request):
        rovers = Rover.objects.all()
        serializer = RoverSerializer(rovers, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        data = JSONParser().parse(io.BytesIO(request.body))
        serializer = RoverSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return HttpResponse()
        return HttpResponseBadRequest()


class SessionAPI(View):
    """
    List all sessions, or create a new session.
    """
    def get(self, request):
        sessions = Session.objects.all()
        serializer = SessionSerializer(sessions, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        data = JSONParser().parse(io.BytesIO(request.body))
        serializer = SessionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return HttpResponse()
        return HttpResponseBadRequest()


class SpecificRoverAPI(View):
    def get_object(self, pk):
        try:
            return Rover.objects.get(pk=pk)
        except Rover.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """
        Retrieve rover instance and return a serialized representation (JSON)
        """
        rover = self.get_object(pk)
        serializer = RoverSerializer(rover)
        return JsonResponse(serializer.data)

    def put(self, request, pk):
        """
        Update existing rover instance from JSON request
        """
        data = JSONParser().parse(io.BytesIO(request.body))
        rover = self.get_object(pk)
        serializer = RoverSerializer(rover, data=data)
        if serializer.is_valid():
            serializer.save()
            return HttpResponse()
        else:
            return HttpResponseBadRequest(serializer.errors)

    def delete(self, request, pk):
        """
        Delete an existing rover from the database
        """
        rover = self.get_object(pk)
        rover.delete()
        return HttpResponse()


class SpecificSessionAPI(View):
    def get_object(self, pk):
        try:
            return Session.objects.get(pk=pk)
        except Session.DoesNotExist:
            raise Http404

    def update_log(self, pk, new_data):
        # Inefficient: hitting DB twice, but I couldn't get the updated Session model from the serializer...
        new_s = Session.objects.get(pk=pk)
        newline = ""
        for field in Session.LOG_FIELDS:
            field = Session._meta.get_field(field)
            value = field.value_from_object(new_s)
            value = str(value) if value is not None else ""
            newline = newline + value + ";"
        newline = newline.rstrip(";") + "\n"
        with new_s.log.open("a") as f:
            f.write(newline)
        new_s.save()

    def get(self, request, pk):
        """
        Retrieve session instance and return a serialized representation (JSON)
        """
        s = self.get_object(pk)
        serializer = SessionSerializer(s)
        return JsonResponse(serializer.data)

    def put(self, request, pk):
        """
        Update existing session instance from JSON request
        """
        data = JSONParser().parse(io.BytesIO(request.body))
        s = self.get_object(pk)
        serializer = SessionSerializer(s, data=data)
        if serializer.is_valid():
            serializer.save()
            self.update_log(pk, serializer.validated_data)
            return HttpResponse(serializer.validated_data)
        else:
            return HttpResponseBadRequest(serializer.errors)

    def delete(self, request, pk):
        """
        Delete an existing rover from the database
        """
        rover = self.get_object(pk)
        rover.delete()
        return HttpResponse()
