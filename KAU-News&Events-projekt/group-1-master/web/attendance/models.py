from django.db import models
from django.conf import settings
from Publication.models import Publication_Event

class EventAttendance(models.Model):
    event = models.ForeignKey(Publication_Event,on_delete=models.CASCADE,related_name='attendees')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    allergies = models.CharField(max_length=200, blank=True, null=True)
    dietary_preferences = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return str(self.event.EventTitle)
