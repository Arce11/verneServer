from django.db import models
from django.core.files.base import ContentFile
import datetime
import os

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.db import models


class Rover(models.Model):
    rover_id = models.CharField(max_length=60, primary_key=True, unique=True)
    # IP Address, though it should be compatible with IP:Port format
    address = models.CharField(max_length=32, blank=False, null=False)
    last_session = models.ForeignKey("mainApp.Session", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.rover_id


class Session(models.Model):
    session_id = models.CharField(max_length=30, primary_key=True, unique=True)
    rover_id = models.ForeignKey("mainApp.Rover", on_delete=models.CASCADE)
    temperature = models.FloatField(blank=True, null=True)
    timestamp = models.FloatField(blank=True, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    log = models.FileField(upload_to='logs/', null=True, blank=True)

    LOG_FIELDS = ["timestamp", "temperature"]

    def __str__(self):
        return self.session_id

    def log_filename(self):
        return os.path.basename(self.log.name)

    def save(self, *args, **kwargs):
        if self._state.adding:
            save_date = datetime.datetime.now()
            filename = f"{self.rover_id}_{save_date:%Y-%m-%d_%H-%M-%S}.csv"
            log_headers = [self._meta.get_field(field).verbose_name for field in self.LOG_FIELDS]
            self.log.save(filename, ContentFile(";".join(log_headers) + "\n"), save=False)
        super(Session, self).save(*args, **kwargs)


# -------------------------------------- METHODS TO HANDLE FILE DELETION -------------------------
# -------------------------------------- (quite inefficient) -------------------------------------
@receiver(post_delete)
def delete_files_when_row_deleted_from_db(sender, instance, **kwargs):
    """ Whenever ANY model is deleted, if it has a file field on it, delete the associated file too"""
    for field in sender._meta.concrete_fields:
        if isinstance(field, models.FileField):
            instance_file_field = getattr(instance, field.name)
            delete_file_if_unused(sender, instance, field, instance_file_field)


@receiver(pre_save)
def delete_files_when_file_changed(sender, instance, **kwargs):
    """ Delete the file if something else get uploaded in its place"""
    # Don't run on initial save
    if not instance.pk:
        return
    for field in sender._meta.concrete_fields:
        if isinstance(field, models.FileField):
            # its got a file field. Let's see if it changed
            try:
                instance_in_db = sender.objects.get(pk=instance.pk)
            except sender.DoesNotExist:
                # We are probably in a transaction and the PK is just temporary
                # Don't worry about deleting attachments if they aren't actually saved yet.
                return
            instance_in_db_file_field = getattr(instance_in_db, field.name)
            instance_file_field = getattr(instance, field.name)
            if instance_in_db_file_field.name != instance_file_field.name:
                delete_file_if_unused(sender, instance, field, instance_in_db_file_field)


def delete_file_if_unused(model, instance, field, instance_file_field):
    """ Only delete the file if no other instances of that model are using it"""
    dynamic_field = {}
    dynamic_field[field.name] = instance_file_field.name
    other_refs_exist = model.objects.filter(**dynamic_field).exclude(pk=instance.pk).exists()
    if not other_refs_exist:
        instance_file_field.delete(False)