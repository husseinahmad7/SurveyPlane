# serializers.py
from rest_framework import serializers
from .models import Survey, Question, Response, Answer
from django.core.files.storage import default_storage
from django.db.models import F
from django.db.models.functions import Cast
from django.db.models import Avg, Max, Min, Count, FloatField
from django.db.models.expressions import RawSQL

# class QuestionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Question
#         fields = ['id', 'question_text', 'question_type', 'required', 'order', 'options']
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'required', 'order', 'settings']

    def validate(self, data):
        question_type = data.get('question_type',None)
        if not question_type:
            raise serializers.ValidationError({'question_type':'please specify the `question_type` field.'})
        settings = data.get('settings', {})
        # schema = Question.get_settings_schema()

        if question_type in ['single_choice', 'multiple_choice']:
            if 'options' not in settings or not settings['options']:
                raise serializers.ValidationError("Choice questions must have options")

        if question_type == 'multiple_choice':
            min_sel = settings.get('min_selections', 1)
            max_sel = settings.get('max_selections')
            if max_sel and min_sel > max_sel:
                raise serializers.ValidationError(
                    "Minimum selections cannot be greater than maximum selections"
                )

        return data



# class AnswerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Answer
#         fields = ['id', 'question', 'answer_text', 'answer_choice']

import base64
import uuid
from django.core.files.base import ContentFile
import os

def answer_file_upload_path(instance, filename):
    """
    Generate file path: surveys/survey_id/response_id/question_id/filename
    This creates organized file storage structure
    """
    ext = filename.split('.')[-1]
    new_filename = f"{instance.question.id}_{instance.response.id}.{ext}"
    return os.path.join(
        'surveys',
        str(instance.question.survey.id),
        str(instance.response.id),
        str(instance.question.id),
        new_filename
    )
class AnswerSerializer(serializers.ModelSerializer):
    # question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    id = serializers.IntegerField(read_only=True)
    file_data = serializers.CharField(write_only=True, required=False)
    file = serializers.FileField(write_only=True, required=False)
    
    class Meta:
        model = Answer
        fields = ['id','question', 'value', 'file_data', 'file']
        # extra_kwargs = {
        #     'value': {'required': False}
        # }

    def validate(self, data):
        """
        validate the client answer is valid for the question schema.
        """
        if self.context.get('validated') is True:
            return data
         
        question = data['question']
        # print(question)
        value = data.get('value')
        # print(value)
        file_data = data.pop('file_data', None)
        # print('5') if file_data else print('0')
        settings = question.settings
 # Validate based on question type
        if question.question_type == Question.QUESTION_TYPES.MULTIPLE:
            if 'choices' not in value or not value['choices']:
                raise serializers.ValidationError({"value":"Choice questions must have at least one selected option"})
            for choice in value['choices']:
                if choice not in question.settings.get('options'):
                    raise serializers.ValidationError({"value":f'the choice {choice} is not a valid choice for this question'})
        elif question.question_type == Question.QUESTION_TYPES.SINGLE:
            if 'choice' not in value or not value['choice'] or not isinstance(value['choice'],str):
                raise serializers.ValidationError({"value":"Single choice question can only have one selected option"})
            if value['choice'] not in question.settings.get('options'):
                raise serializers.ValidationError({"value":f'the choice ({value["choice"]}) is not a valid choice for this question'})
        elif question.question_type == Question.QUESTION_TYPES.RATING:
            if not isinstance(value,float):
                raise serializers.ValidationError({"value":"Rating question must have an float value"})
            if not (settings.get('min_value') <= value <= settings.get('max_value')):
                raise serializers.ValidationError({"value":"Rating question must have an float value between min value and max value"})
            if not (value - settings.get('min_value')) % settings.get('step') == 0:
                raise serializers.ValidationError({"value":f"Rating question must have an float value with the correct step {settings.get('step')}"})
        elif question.question_type == Question.QUESTION_TYPES.TEXT and not isinstance(value, str) or value == '': #('answer_text' not in value or not value['answer_text']):
            raise serializers.ValidationError({"value":"Text question must have a value"})
        # Handle file upload
        if question.question_type == 'file' and file_data:#(file_data is not None or file_data != ''):
            try:
                # Parse file data (format: "data:mimetype;base64,<base64-data>")
                file_format, filestr = file_data.split(';base64,')
                ext = file_format.split('/')[-1]
                
                # Validate file extension
                allowed_extensions = question.settings.get('allowed_extensions', ['pdf', 'doc', 'docx'])
                if ext.lower() not in allowed_extensions:
                    raise serializers.ValidationError(
                        f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
                    )

                # Decode file data
                file_data = base64.b64decode(filestr)
                
                file_size = len(file_data) / (1024 * 1024)  # Convert to MB TODO round
                
                # Validate file size
                max_size = question.settings.get('max_file_size', 5)  # Default 5MB
                if file_size > max_size:
                    raise serializers.ValidationError(
                        f"File size too large. Maximum size: {max_size}MB"
                    )

                # Generate unique filename
                filename = f"{value if value else 'file'}-{uuid.uuid4().hex}.{ext}"
                
                # Store file information in value field
                data['value'] = {
                    # 'filename': filename,
                    'size': file_size,
                    'type': ext
                }

                data['file'] = ContentFile(file_data, filename)
                # self.context['file'] = ContentFile(file_data, filename)
            except Exception as e:
                raise serializers.ValidationError({'file_data':str(e)})
        elif question.question_type == 'file' and (file_data is None or file_data == ''):
            print(file_data)
            raise serializers.ValidationError({"file_data":"File question must have a file"})
        
            # print(f'data: {data}\n**validated**')
        # self.context['validate'] = True
        return data

    def create(self, validated_data):
        # Create answer instance

        # pop file_data before creating
        file_data = validated_data.pop('file', None)
        # print(file_data)
        answer = Answer(**validated_data)
                
        if file_data:
            file_path = answer_file_upload_path(answer, file_data.name)
            default_storage.save(file_path, file_data)
            validated_data.get('value').update({'file_path':file_path})
            # answer.value['file_path'] = file_path
            # print(file_path)
            # answer.save()
        answer.save()
        # answer = Answer.objects.create(**validated_data) # question, value


        return answer
    def update(self, instance, validated_data):
        if validated_data.get('file'):
            file_path = answer_file_upload_path(instance, validated_data.get('file').name)
            default_storage.delete(instance.value.get('file_path'))
            default_storage.save(file_path, validated_data.get('file'))
            validated_data.get('value').update({'file_path':file_path})

        return super().update(instance, validated_data)



class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Response
        fields = ['id', 'survey', 'respondent', 'submitted_at', 'answers']
        read_only_fields = ['submitted_at']
        
    def validate(self, data):
        answers_data = data.get('answers')
        # print(data)
        # {'survey': <Survey: discussion>, 
        # 'answers': [{'question': <Question: Question object (9)>, 'value': 'hussana'},
        #  {'question': <Question: Question object (10)>, 'value': {'choices': ['Option A']}},
        # {'question': <Question: Question object (12)>, 'value': {'choices': ['Option A']}}]}
        for answer_data in answers_data:
            if answer_data.get('question').survey.pk is not data.get('survey').pk:
                print(f"{answer_data.get('question').survey.pk} --- {data.get('survey').pk}")
                raise serializers.ValidationError(f'this question ({answer_data.get('question')}) is not for this survey')

        return data

    def create(self, validated_data):
        # print(f'validated data: {validated_data}')
        answers_data = validated_data.pop('answers')
        response = Response.objects.create(**validated_data)
        # self.answers
        # print(f'response: {response}')
        for answer_data in answers_data:
            # Update answer data with question id replacing Question object
            answer_data.update({'question': answer_data.get('question').pk})
            # print(answer_data)
            # Pass response instance in context for file path generation
            answer_serializer = AnswerSerializer(
                data=answer_data,
                context={'response': response,'validated':True} # to avoid validating the data again and loss `file` key
            )
            # print(f'answer serializer: {answer_serializer}')
            if answer_serializer.is_valid(raise_exception=True):
                answer_serializer.save(response=response) # calls the answer serializer.create
        
        return response

        # for answer_data in answers_data:
        #     Answer.objects.create(response=response, **answer_data)
        # return response

# views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse
from django.db.models import Count, Avg
from django.utils import timezone

class SurveyViewSet(viewsets.ModelViewSet):

    class CreateSerializer(serializers.ModelSerializer):
        questions = QuestionSerializer(many=True)

        class Meta:
            model = Survey
            fields = ['id', 'title', 'description', 'creator', 'created_at', 
                    'closes_at', 'is_active', 'questions']
            read_only_fields = ['creator', 'created_at']

        def validate(self, data):
            if 'questions' not in data or not data['questions']:
                raise serializers.ValidationError({'questions': 'Questions is required and must not be empty'})
            for question_data in data['questions']:
                question = Question(**question_data)
                question.clean()  # validate each question
            return data

        def create(self, validated_data):
            questions_data = validated_data.pop('questions')
            survey = Survey.objects.create(**validated_data)
            for question_data in questions_data:
                Question.objects.create(survey=survey, **question_data) # TODO call clean(), use bulk_create
            return survey

    class OutputSerializer(serializers.ModelSerializer):
        questions = QuestionSerializer(many=True, read_only=True)
        is_closed = serializers.BooleanField(read_only=True)

        class Meta:
            model = Survey
            fields = ['id', 'title', 'description', 'creator', 'created_at', 
                    'closes_at', 'is_active', 'is_closed', 'questions']
            read_only_fields = ['creator', 'created_at']

    serializer_class = OutputSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            # For list action, show all active surveys
            return Survey.objects.filter(is_active=True)
        # For other actions, show all surveys created by the user
        return Survey.objects.filter(creator=self.request.user)
    

    def get_serializer_class(self):
        if self.action == 'create':
            return self.CreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        survey = self.get_object()
        
        if not survey.is_closed:
            return DRFResponse(
                {'error': 'Survey is still active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        stats = {
            'total_responses': survey.responses.count(),
            'questions': []
        }

        for question in survey.questions.all():
            question_stats = {
                'question_text': question.question_text,
                'question_type': question.question_type,
            }
            # rating_questions = Question.objects.filter(survey=survey, question_type=Question.QUESTION_TYPES.RATING)
            answers = Answer.objects.filter(question=question)
            
            if question.question_type in ['single_choice', 'multiple_choice']:
                option_counts = {}
                for answer in answers:
                    choices = answer.value.get('choices') or answer.value.get('choice')
                    if isinstance(choices, list):
                        for choice in choices:
                            option_counts[choice] = option_counts.get(choice, 0) + 1
                    else:
                        option_counts[choices] = option_counts.get(choices, 0) + 1
                question_stats['option_distribution'] = option_counts
                
            elif question.question_type == 'rating':
                rating_stats = answers.aggregate(
                    avg_rating=Avg(Cast('value', FloatField())),
                    max_rating=Max(Cast('value', FloatField())),
                    min_rating=Min(Cast('value', FloatField())),
                    count_ratings=Count('id')
                )
                question_stats.update({
                    'average_rating': float(rating_stats['avg_rating']) if rating_stats['avg_rating'] is not None else None,
                    'max_rating': float(rating_stats['max_rating']) if rating_stats['max_rating'] is not None else None,
                    'min_rating': float(rating_stats['min_rating']) if rating_stats['min_rating'] is not None else None,
                    'total_ratings': rating_stats['count_ratings']
                })

            stats['questions'].append(question_stats)

                # avg_rating = answers.aggregate(Avg(F('value'))) # TODO decide how to store rating answer
#                 TypeError(f'the JSON object must be str, bytes or bytearray, '
# TypeError: the JSON object must be str, bytes or bytearray, not float
                # question_stats['average_rating'] = avg_rating['value__avg']

#list(survey.responses.annotate(date=TruncDate('created_at'))
                #    .values('date')
                #    .annotate(count=Count('id'))
                #    .order_by('date'))
# user = answer.response.user

#                     # Assuming you have age, gender, and location fields in your User model
#                     if hasattr(user, 'age'):  # Example - adapt as needed
#                         age_group = self.get_age_group(user.age)
#                         age_groups[age_group] = age_groups.get(age_group, 0) + 1
#                     # ... similarly collect gender and location counts

#                     if hasattr(user, 'gender'):
#                         gender = user.gender
#                         gender_counts[gender] = gender_counts.get(gender, 0) + 1

#                     if hasattr(user, 'location'):
#                         location = user.location
#                         locations[location] = locations.get(location, 0) + 1


#                 demographics.update({"age_groups":age_groups})
#                 demographics.update({"gender_counts":gender_counts})
#                 demographics.update({"locations":locations})

#         return demographics
#     def get_age_group(self, age):
#         # Example age grouping - customize as per your needs

#         if age < 18:
#             return "Under 18"
#         elif age < 30:
#             return "18-29"
#         elif age < 45:
#             return "30-44"

#         # ... more age groups
#         else:
#             return "65+"  # Example
        return DRFResponse(stats)

class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Question.objects.filter(survey__creator=self.request.user)

    def perform_create(self, serializer):
        survey = Survey.objects.get(pk=self.kwargs['survey_pk'])
        if survey.creator != self.request.user:
            raise permissions.PermissionDenied()
        serializer.save(survey=survey)
    
    @action(detail=False, methods=['get'], url_path='survey-questions/(?P<survey_pk>[0-9]+)')
    def survey_questions(self, request, survey_pk=None):
        survey = Survey.objects.get(pk=survey_pk)
        # if not survey.is_closed:
        #     return DRFResponse(
        #         {'error': 'Survey is still active'}, 
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        # print(survey)
        questions = Question.objects.filter(survey=survey)
        # print(questions)
        serializer = QuestionSerializer(questions, many=True)
        return DRFResponse(serializer.data)

class ResponseViewSet(viewsets.ModelViewSet):
    serializer_class = ResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):    
        if self.request.user.is_staff:
            # Staff can see all responses
            return Response.objects.all()
        # Regular users can only see their own responses
        return Response.objects.filter(respondent=self.request.user).prefetch_related('survey__questions')

    def perform_create(self, serializer):
        print('perform create in response view')
        survey = Survey.objects.get(pk=self.request.data['survey'])
        
        if survey.is_closed:
            raise serializers.ValidationError("Survey is closed")
            
        serializer.save(
            survey=survey,
            respondent=self.request.user if self.request.user.is_authenticated else None
        )

from django.shortcuts import get_object_or_404

class ResponseAnswerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing answers within a response.
    Allows updating, creating, and deleting individual answers.
    """
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    # http_method_names = ['PUT', 'PATCH', 'POST']


    def get_queryset(self):
        return Answer.objects.filter(
            response__respondent=self.request.user,
            response_id=self.kwargs.get('response_pk')
        )
    
    
    # def perform_create(self, serializer):
    #     response = get_object_or_404(
    #         Response, 
    #         id=self.kwargs.get('response_pk'),
    #         respondent=self.request.user
    #     )
    #     if response.survey.is_closed:
    #         raise serializers.ValidationError("Cannot modify answers - survey is closed")
    #     serializer.save(response=response)
    
    # def perform_update(self, serializer):
    #     answer = self.get_object()
    #     if answer.response.survey.is_closed:
    #         raise serializers.ValidationError("Cannot modify answers - survey is closed")
    #     serializer.save()
    
    # def perform_destroy(self, instance):
    #     if instance.response.survey.is_closed:
    #         raise serializers.ValidationError("Cannot delete answers - survey is closed")
    #     instance.delete()
    
    ####### check kwargs
    @action(detail=False, methods=['put', 'patch'],url_path='bulk_update/(?P<response_pk>[0-9]+)')
    def bulk_update(self, request, response_pk=None):
        """
        Bulk update answers for a response.
        Expects data in format:
        {
            "answers": [
                {
                    "id": 1,
                    "value": "new value"
                },
                {
                    "id": 2,
                    "value": {"choices": ["Option A", "Option B"]}
                }
            ]
        }
        """
        response = get_object_or_404(
            Response, 
            id=response_pk,
            respondent=self.request.user
        )
        
        if response.survey.is_closed:
            return Response(
                {"detail": "Cannot modify answers - survey is closed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        answers_data = request.data.get('answers', [])
        updated_answers = []
        errors = []
        
        for answer_data in answers_data:
            answer_id = answer_data.get('id')
            try:
                answer = Answer.objects.get(
                    id=answer_id,
                    response=response
                )
                serializer = self.get_serializer(
                    answer,
                    data=answer_data,#{'question': answer.question.id, 'value': answer_data.get('value')},
                    partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    updated_answers.append(serializer.data)
                else:
                    errors.append({
                        'id': answer_id,
                        'errors': serializer.errors
                    })
            except Answer.DoesNotExist:
                errors.append({
                    'id': answer_id,
                    'errors': 'Answer not found'
                })
        
        # Answer.objects.bulk_update(updated_answers, ['value'])
        return DRFResponse({
            'updated': updated_answers,
            'errors': errors
        })

    @action(detail=False, methods=['post'])
    def add_answers(self, request, response_pk=None):
        """
        Add new answers to an existing response.
        Expects data in format:
        {
            "answers": [
                {
                    "question": 1,
                    "value": "new answer"
                },
                {
                    "question": 2,
                    "value": {"choices": ["Option A", "Option B"]}
                }
            ]
        }
        """
        response = get_object_or_404(
            Response, 
            id=response_pk,
            respondent=self.request.user
        )
        
        if response.survey.is_closed:
            return Response(
                {"detail": "Cannot add answers - survey is closed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        answers_data = request.data.get('answers', [])
        created_answers = []
        errors = []
        
        for answer_data in answers_data:
            # Check if answer already exists for this question
            existing_answer = Answer.objects.filter(
                response=response,
                question_id=answer_data.get('question')
            ).first()
            
            if existing_answer:
                errors.append({
                    'question': answer_data.get('question'),
                    'errors': 'Answer already exists for this question'
                })
                continue
            
            serializer = self.get_serializer(data=answer_data)
            if serializer.is_valid():
                serializer.save(response=response)
                created_answers.append(serializer.data)
            else:
                errors.append({
                    'question': answer_data.get('question'),
                    'errors': serializer.errors
                })
        
        return DRFResponse({
            'created': created_answers,
            'errors': errors
        })