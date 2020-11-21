from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView
from .models import Rover, Session


def index(request):
    return render(request, 'mainApp/index.html')


def monitor(request, rover_id):
    try:
        rover = Rover.objects.get(rover_id=rover_id)
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


class RoverAPI(TemplateView):
    pass

# To update a saved file:
# s = Session.objects.get(pk="34534534543")
# with s.log.open("a") as f:
#     f.writelines(["Error! xd"])
# s.save()
