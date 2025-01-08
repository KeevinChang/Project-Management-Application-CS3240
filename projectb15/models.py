from django.db import models
from django.urls import reverse
from users.models import User
    
class Event(models.Model):
    title = models.CharField(max_length=50)
    date = models.DateField("date of event")
    description = models.CharField(max_length=200)
    start_time = models.TimeField("beginning of event")
    end_time = models.TimeField("end of event")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owners")
    members = models.ManyToManyField(User, related_name="members", blank=True)
    pending_invites = models.ManyToManyField(User, related_name="pending", blank=True)
    invited = models.ManyToManyField(User, related_name="invited", blank=True)
   
    header_image = models.FileField(upload_to='uploads/', blank=True, null=True)  # Allow blank and null
    visibility = models.IntegerField()

    def get_absolute_url(self):
        return reverse('event-detail', args=[str(self.id)])
    
class Message(models.Model):
    posted_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=False, null=False)
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.poster}: {self.content}"

class Upload(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='uploads/')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    keywords = models.CharField(max_length=200, blank=True, null=True, help_text="Comma-separated keywords (ex. Event, Topic, etc.)")
    