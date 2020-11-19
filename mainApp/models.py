from django.db import models


class Rover(models.Model):
    rover_id = models.CharField(max_length=60, primary_key=True, unique=True)
    address = models.CharField(max_length=32)  # IP Address, though it should be compatible with IP:Port format
    last_session = models.ForeignKey("mainApp.Session", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.rover_id


class Session(models.Model):
    session_id = models.CharField(max_length=30, primary_key=True, unique=True)
    rover_id = models.ForeignKey("mainApp.Rover", on_delete=models.CASCADE)
    last_temperature = models.FloatField(blank=True, null=True)
    last_timestamp = models.FloatField()
    start_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.session_id

