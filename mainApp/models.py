from django.db import models
from django.core.files.base import ContentFile
import datetime
import os


class Rover(models.Model):
    rover_id = models.CharField(max_length=60, primary_key=True, unique=True)
    address = models.CharField(max_length=32)  # IP Address, though it should be compatible with IP:Port format
    last_session = models.ForeignKey("mainApp.Session", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.rover_id


class Session(models.Model):
    FILE_HEADERS = "Timestamp;Temperature\n"

    session_id = models.CharField(max_length=30, primary_key=True, unique=True)
    rover_id = models.ForeignKey("mainApp.Rover", on_delete=models.CASCADE)
    last_temperature = models.FloatField(blank=True, null=True)
    last_timestamp = models.FloatField()
    start_time = models.DateTimeField(auto_now_add=True)
    log = models.FileField(upload_to='logs/', null=True, blank=True)

    def __str__(self):
        return self.session_id

    def log_filename(self):
        return os.path.basename(self.log.name)

    def save(self, *args, **kwargs):
        if self._state.adding:
            save_date = datetime.datetime.now()
            filename = f"{self.rover_id}_{save_date:%Y-%m-%d_%H-%M-%S}.csv"
            self.log.save(filename, ContentFile(self.FILE_HEADERS), save=False)
        super(Session, self).save(*args, **kwargs)
