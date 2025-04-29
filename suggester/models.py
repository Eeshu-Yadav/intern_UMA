from django.db import models
from django.utils import timezone

class QueryLog(models.Model):
    query = models.TextField()
    tone = models.CharField(max_length=50)
    intent = models.CharField(max_length=50)
    suggested_actions = models.JSONField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.query[:50]} - {self.timestamp}"