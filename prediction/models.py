from django.db import models
from django.contrib.auth.models import User
from speech_analytics.models import CallData

class Prediction(models.Model):
    BEHAVIOR_CHOICES = [
        ('Positive', 'Positive'),
        ('Neutral', 'Neutral'),
        ('Negative', 'Negative'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    call = models.ForeignKey(CallData, on_delete=models.CASCADE)
    behavior = models.CharField(max_length=20, choices=BEHAVIOR_CHOICES)
    confidence_score = models.FloatField()
    recommendation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction for Call #{self.call.id} - {self.behavior}"
