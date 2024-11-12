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

# class Question(models.Model):
#     QUESTION_TYPES = (
#         ('text', 'Text Response'),
#         ('single_choice', 'Single Choice'),
#         ('multiple_choice', 'Multiple Choice'),
#         ('rating', 'Rating Scale'),
#     )

#     survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)
#     question_text = models.TextField()
#     question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
#     required = models.BooleanField(default=False)
#     order = models.IntegerField(default=0)
#     options = models.JSONField(null=True, blank=True)  # For choice-based questions

#     class Meta:
#         ordering = ['order']
#         unique_together = ('survey', 'order')

#     def clean(self):
#         if self.question_type in ['single_choice', 'multiple_choice'] and not self.options:
#             raise ValidationError("Choice-based questions must have options defined")

class Question(models.Model):
    class  QUESTION_TYPES(models.TextChoices):
        TEXT = ('text', 'Text Response')
        SINGLE = ('single_choice', 'Single Choice')
        MULTIPLE = ('multiple_choice', 'Multiple Choice')
        RATING = ('rating', 'Rating Scale')
        FILE = ('file', 'File Upload')
    

    survey = models.ForeignKey('Survey',related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES.choices)
    required = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    settings = models.JSONField(default=dict)  # For type-specific settings

    class Meta:
        ordering = ['order']

    def get_settings_schema(self):
        """Return the expected settings schema for each question type"""
        schemas = {
            'text': {
                'min_length': {'type': int, 'required': False, 'default': None},
                'max_length': {'type': int, 'required': False, 'default': None}
            },
            'single_choice': {
                'options': {'type': list, 'required': True}
            },
            'multiple_choice': {
                'options': {'type': list, 'required': True},
                'min_selections': {'type': int, 'required': False, 'default': 1},
                'max_selections': {'type': int, 'required': False, 'default': None}
            },
            'rating': {
                'min_value': {'type': int, 'required': False, 'default': 1},
                'max_value': {'type': int, 'required': False, 'default': 5},
                'step': {'type': float, 'required': False, 'default': 1.0}
            },
            'file': {
                'allowed_extensions': {'type': list, 'required': False, 'default': ['pdf', 'doc', 'docx']},
                'max_file_size': {'type': int, 'required': False, 'default': 5}
            }
        }
        return schemas.get(self.question_type, {})

    def clean(self):
        schema = self.get_settings_schema()
        for field, rules in schema.items():
            if rules['required'] and field not in self.settings:
                raise ValidationError(f"{field} is required for {self.question_type} questions")
            if field not in self.settings and 'default' in rules:
                self.settings[field] = rules['default']
    
    # @classmethod
    # def get_schema_for_question_type(cls, question_type):
    #     return cls.get_settings_schema()


class Response(models.Model):
    survey = models.ForeignKey(Survey, related_name='responses', on_delete=models.CASCADE)
    respondent = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Response to {self.survey.title} at {self.submitted_at}"


class Answer(models.Model):
    response = models.ForeignKey(Response, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    # answer_text = models.TextField(null=True, blank=True)
    # answer_choice = models.JSONField(null=True, blank=True)  # For storing single/multiple choice answers
    value = models.JSONField(null=True, blank=True)
    
    class Meta:
        unique_together = ['response', 'question']

    def __str__(self) -> str:
        return f"Answer to question {self.question.id} in response {self.response.id} to survey {self.response.survey.pk}"

    def clean(self):
        """Validate answer based on question type"""
        # if not self.question_id:
        #     return
        print('model clean method')
        if self.question.required and not self.value:
            raise ValidationError("This question is required")

        try:
            self.validate_answer_format()
        except Exception as e:
            raise ValidationError(str(e))

    def validate_answer_format(self):
        """Validate answer format based on question type"""
        question_type = self.question.question_type
        settings = self.question.settings

        if not self.value and not self.question.required:
            return

        if question_type == 'text':
            if not isinstance(self.value, str):
                raise ValidationError("Text answer must be a string")
            min_length = settings.get('min_length')
            max_length = settings.get('max_length')
            if min_length and len(self.value) < min_length:
                raise ValidationError(f"Answer must be at least {min_length} characters")
            if max_length and len(self.value) > max_length:
                raise ValidationError(f"Answer cannot exceed {max_length} characters")

        elif question_type == 'single_choice':
            if self.value not in settings.get('options', []):
                raise ValidationError("Invalid choice selected")

        elif question_type == 'multiple_choice':
            if not isinstance(self.value, list):
                raise ValidationError("Multiple choice answer must be a list")
            options = settings.get('options', [])
            if not all(choice in options for choice in self.value):
                raise ValidationError("Invalid choices selected")
            min_selections = settings.get('min_selections', 1)
            max_selections = settings.get('max_selections')
            if len(self.value) < min_selections:
                raise ValidationError(f"Must select at least {min_selections} options")
            if max_selections and len(self.value) > max_selections:
                raise ValidationError(f"Cannot select more than {max_selections} options")

        elif question_type == 'rating':
            try:
                rating = float(self.value)
                min_value = float(settings.get('min_value', 1))
                max_value = float(settings.get('max_value', 5))
                if not (min_value <= rating <= max_value):
                    raise ValidationError(f"Rating must be between {min_value} and {max_value}")
            except (TypeError, ValueError):
                raise ValidationError("Rating must be a number")

        elif question_type == 'file':
            if not isinstance(self.value, dict) or 'filename' not in self.value:
                raise ValidationError("Invalid file answer format")
