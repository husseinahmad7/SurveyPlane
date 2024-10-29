from django.db import models

# Create your models here.
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import json
User = get_user_model()

class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    closes_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def is_closed(self):
        from django.utils import timezone
        return timezone.now() >= self.closes_at or not self.is_active

class Question(models.Model):
    QUESTION_TYPES = (
        ('text', 'Text Response'),
        ('single_choice', 'Single Choice'),
        ('multiple_choice', 'Multiple Choice'),
        ('rating', 'Rating Scale'),
    )

    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    required = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    options = models.JSONField(null=True, blank=True)  # For choice-based questions

    class Meta:
        ordering = ['order']

    def clean(self):
        if self.question_type in ['single_choice', 'multiple_choice'] and not self.options:
            raise ValidationError("Choice-based questions must have options defined")

class Response(models.Model):
    survey = models.ForeignKey(Survey, related_name='responses', on_delete=models.CASCADE)
    respondent = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
class Answer(models.Model):
    response = models.ForeignKey(Response, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(null=True, blank=True)
    answer_choice = models.JSONField(null=True, blank=True)  # For storing single/multiple choice answers
