from django.db import models
from django.contrib.auth.models import User

class CallData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='audio/')
    transcript = models.TextField(blank=True, null=True)
    emotion = models.CharField(max_length=50, blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Call Analysis - {self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
