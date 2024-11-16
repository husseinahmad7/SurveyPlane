# serializers.py
from rest_framework import serializers
from .models import Survey, Question, Response, Answer
from django.core.files.storage import default_storage
from django.db.models import F
from django.db.models.functions import Cast
from django.db.models import Avg, Max, Min, Count,StdDev, FloatField
from django.conf import settings as project_settings
from .config import ANSWER_FILE_PATH_KEY, QUESTION_ATTACHEMENT_FILE_PATH_KEY
import numpy
# class QuestionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Question
#         fields = ['id', 'question_text', 'question_type', 'required', 'order', 'options']
class QuestionSerializer(serializers.ModelSerializer):
    file_data = serializers.CharField(write_only=True, required=False, allow_null=True)
    url = serializers.URLField(write_only=True, required=False, allow_null=True)
    file = serializers.FileField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'required', 'order', 'settings','file_data', 'url','file']

    def validate(self, data):
        if self.context.get('validated') is True:
            return data
        question_type = data.get('question_type',None)
        if not question_type:
            raise serializers.ValidationError({'question_type':'please specify the `question_type` field.'})
        settings = data.get('settings', {})
        # schema = Question.get_settings_schema()

        if question_type == Question.QUESTION_TYPES.SINGLE:# in ['single_choice', 'multiple_choice']:
            if 'options' not in settings or not settings['options']:
                raise serializers.ValidationError("Choice questions must have options")

        if question_type == Question.QUESTION_TYPES.MULTIPLE:
            if 'options' in settings and 'flexable' not in settings:
                raise serializers.ValidationError("in Multiple choice question you must specify `flexable`== true or false beside specifying options")
            if 'options' not in settings and ('flexable' not in settings or settings['flexable'] == False):
                raise serializers.ValidationError("in Multiple choice question you must specify `flexable` == true if you dont specify options")
            
            min_sel = settings.get('min_selections', 1)
            max_sel = settings.get('max_selections')
            if max_sel and min_sel > max_sel:
                raise serializers.ValidationError(
                    "Minimum selections cannot be greater than maximum selections"
                )
        if data.get('file_data'):
            file_data = data.pop('file_data', None)

            try:
                # Parse file data (format: "data:mimetype;base64,<base64-data>")
                file_format, filestr = file_data.split(';base64,')
                ext = file_format.split('/')[-1]
                
                # Validate file extension
                # allowed_extensions = question.settings.get('allowed_extensions', ['pdf', 'doc', 'docx'])
                # if ext.lower() not in allowed_extensions:
                #     raise serializers.ValidationError(
                #         f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
                #     )

                # Decode file data
                file_data = base64.b64decode(filestr)
                
                file_size = len(file_data) / (1024 * 1024)  # Convert to MB TODO round
                
                # Validate file size
                max_size = getattr(project_settings,'max_file_size', 5 * 1024 * 1024)  # Default 5MB
                if file_size > max_size:
                    raise serializers.ValidationError(
                        f"File size too large. Maximum size: {max_size}MB"
                    )

                # Generate unique filename
                filename = f"{uuid.uuid4().hex}.{ext}"
                
                # Store file information in settings field
                settings.update({'attachment_file_size': file_size})


                data['file'] = ContentFile(file_data, filename)
                # self.context['file'] = ContentFile(file_data, filename)
            except Exception as e:
                raise serializers.ValidationError({'file_data':str(e)})
        # elif question.question_type == 'file' and (file_data is None or file_data == ''):
        #     print(file_data)
        #     raise serializers.ValidationError({"file_data":"File question must have a file"})
        
        return data
    def create(self, validated_data):

        # pop file before creating
        file_data = validated_data.pop('file', None)
        url = validated_data.pop('url', None)
        # print(file_data)
        question = Question(**validated_data)
        question.clean()
                
        if file_data:
            file_path = answer_file_upload_path(question, file_data.name, 'questions')
            default_storage.save(file_path, file_data)
            validated_data.get('settings').update({'attachment_file_path':file_path})

        if url:
            validated_data.get('settings').update({'attachment_url': url})
        question.save()
        # answer = Answer.objects.create(**validated_data) # question, value


        return question
    def update(self, instance, validated_data):
        if validated_data.get('file'):
            file_path = answer_file_upload_path(instance, validated_data.get('file').name, 'questions')
            default_storage.delete(instance.settings.get(QUESTION_ATTACHEMENT_FILE_PATH_KEY))
            default_storage.save(file_path, validated_data.get('file'))
            validated_data.get('settings').update({QUESTION_ATTACHEMENT_FILE_PATH_KEY:file_path})

        url = validated_data.pop('url', None)
        if url:
            validated_data.get('settings').update({'attachment_url': url})

        return super().update(instance, validated_data)


# class AnswerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Answer
#         fields = ['id', 'question', 'answer_text', 'answer_choice']

import base64
import uuid
from django.core.files.base import ContentFile
import os

def answer_file_upload_path(instance, filename, prefix):
    """
    Generate file path: answers/survey_id/response_id/question_id/filename for answers
    else: questions/survey_id/question_{id}.ext for 
    This creates organized file storage structure
    """
    ext = filename.split('.')[-1]
    if isinstance(instance,Question):
        new_filename = f"question_{instance.id}.{ext}" if getattr(instance,'id') is not None else f"question_{filename}"
        return os.path.join(
            prefix,
            str(instance.survey.id),
            new_filename
        )
    new_filename = f"{instance.question.id}_{instance.response.id}.{ext}"
    return os.path.join(
        prefix,
        # 'surveys',
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
                raise serializers.ValidationError({"value":"Muliple choice questions must have `choices` in `value` and have at least one selected option"})
            if not isinstance(value['choices'],list):
                raise serializers.ValidationError({"value":"the `choices` in `value` must be a list"})
            if settings.get('min_selections') and len(value['choices']) < settings.get('min_selections'):
                raise serializers.ValidationError({"value":f"Choice questions must have at least {settings.get('min_selections')} selected options"})
            if settings.get('max_selections') and len(value['choices']) > settings.get('max_selections'):
                raise serializers.ValidationError({"value":f"Choice questions must have at most {settings.get('max_selections')} selected options"})
            # check each answer choice if its in the options
            if settings.get('flexable') == False:
                for choice in value['choices']:
                    if choice not in settings.get('options'):
                        raise serializers.ValidationError({"value":f'the choice `{choice}` is not a valid choice for this question'})
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
            file_path = answer_file_upload_path(answer, file_data.name, 'answers')
            default_storage.save(file_path, file_data)
            validated_data.get('value').update({ANSWER_FILE_PATH_KEY:file_path})
            # answer.value['file_path'] = file_path
            # print(file_path)
            # answer.save()
        answer.save()
        # answer = Answer.objects.create(**validated_data) # question, value


        return answer
    def update(self, instance, validated_data):
        if validated_data.get('file'):
            file_path = answer_file_upload_path(instance, validated_data.get('file').name, 'answers')
            default_storage.delete(instance.value.get(ANSWER_FILE_PATH_KEY))
            default_storage.save(file_path, validated_data.get('file'))
            validated_data.get('value').update({ANSWER_FILE_PATH_KEY:file_path})

        return super().update(instance, validated_data)



class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Response
        fields = ['id', 'survey', 'respondent', 'submitted_at', 'answers']
        read_only_fields = ['submitted_at']
        
    def validate(self, data):
        answers_data = data.get('answers')
        survey_questions = data.get('survey').questions.all()
        required_questions = survey_questions.filter(required=True).values_list('id', flat=True)
        answered_questions = [answer_data.get('question').id for answer_data in answers_data]
        # print(f'required_questions: {required_questions}\nanswered_questions: {answered_questions}')
        required_questions_not_answered = []
        for required_question in required_questions:
            if required_question not in answered_questions:
                required_questions_not_answered.append(required_question)
        if required_questions_not_answered:
            raise serializers.ValidationError({'answers':f'All required questions must be answered','not_answered_required_questions': required_questions_not_answered})

        # if not required_questions.filter(id__in=answered_questions).count() == required_questions.count():
        #     raise serializers.ValidationError(f'All required questions must be answered')

        for answer_data in answers_data:
            if answer_data.get('question').survey.pk is not data.get('survey').pk:
                raise serializers.ValidationError(f'this question ({answer_data.get("question")}) is not for this survey')

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
            # for question_data in data['questions']:
            #     question = Question(**question_data)
                
            #     question.clean()  # do clean() for each question
            return data

        def create(self, validated_data):
            questions_data = validated_data.pop('questions')
            survey = Survey.objects.create(**validated_data)
            for question_data in questions_data:
                question = QuestionSerializer(data=question_data,context={'validated':True})
                 # do clean() for each question
                if question.is_valid(raise_exception=True):
                    question.save(survey=survey) # TODO call clean(), use bulk_create
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

        # Get query parameters for analysis
        correlation_questions = request.query_params.getlist('correlate')
        filter_question = request.query_params.get('filter_question')
        filter_value = request.query_params.get('filter_value')
        group_by = request.query_params.get('group_by')  # e.g., 'date', 'respondent__age_group'

        # Base statistics
        stats = {
            'total_responses': survey.responses.count(),
            'questions': [],
            'correlations': {},
            'patterns': {},
            'filtered_insights': {}
        }

        # Apply filters if specified
        responses = survey.responses.all()
        if filter_question and filter_value:
            try:
                filter_q = Question.objects.get(id=filter_question, survey=survey)
                filtered_answers = Answer.objects.filter(
                    question=filter_q,
                    response__in=responses,
                    value__contains=filter_value
                )
                responses = Response.objects.filter(id__in=filtered_answers.values('response'))
            except Question.DoesNotExist:
                pass

        # Process each question's statistics
        for question in survey.questions.all():
            question_stats = {
                'id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'response_rate': 0,
                'temporal_analysis': {},
            }
            
            answers = Answer.objects.filter(question=question, response__in=responses)
            total_answers = answers.count()
            question_stats['response_rate'] = (total_answers / stats['total_responses']) * 100 if stats['total_responses'] > 0 else 0

            # Time-based analysis TODO
            # temporal_data = answers.extra(
            #     select={'date': "DATE(submitted_at)"}
            # ).values('date').annotate(count=Count('id')).order_by('date')
            # question_stats['temporal_analysis'] = list(temporal_data)

            if question.question_type in [Question.QUESTION_TYPES.SINGLE, Question.QUESTION_TYPES.MULTIPLE]:
                option_counts = {}
                percentage_distribution = {}
                CHOICE_KEY = 'choices' if question.question_type == Question.QUESTION_TYPES.MULTIPLE else 'choice'
                
                for answer in answers:
                    choices = answer.value.get(CHOICE_KEY)
                    if isinstance(choices, list):
                        for choice in choices:
                            option_counts[choice] = option_counts.get(choice, 0) + 1
                    else:
                        option_counts[choices] = option_counts.get(choices, 0) + 1

                # Calculate percentages
                for option, count in option_counts.items():
                    percentage_distribution[option] = (count / total_answers * 100) if total_answers > 0 else 0

                question_stats.update({
                    'option_distribution': option_counts,
                    'percentage_distribution': percentage_distribution,
                    'most_common_answer': max(option_counts.items(), key=lambda x: x[1])[0] if option_counts else None,
                })

            elif question.question_type == Question.QUESTION_TYPES.RATING:
                rating_stats = answers.aggregate(
                    avg_rating=Avg(Cast('value', FloatField())),
                    max_rating=Max(Cast('value', FloatField())),
                    min_rating=Min(Cast('value', FloatField())),
                    count_ratings=Count('id'),
                    stddev_rating=StdDev(Cast('value', FloatField()))
                )
                
                # Calculate rating distribution
                rating_distribution = answers.values('value').annotate(
                    count=Count('id')
                ).order_by('value')

                question_stats.update({
                    'average_rating': float(rating_stats['avg_rating']) if rating_stats['avg_rating'] is not None else None,
                    'max_rating': float(rating_stats['max_rating']) if rating_stats['max_rating'] is not None else None,
                    'min_rating': float(rating_stats['min_rating']) if rating_stats['min_rating'] is not None else None,
                    'total_ratings': rating_stats['count_ratings'],
                    'standard_deviation': float(rating_stats['stddev_rating']) if rating_stats['stddev_rating'] is not None else None,
                    'rating_distribution': list(rating_distribution)
                })

            stats['questions'].append(question_stats)

        # Calculate correlations between specified questions
        if len(correlation_questions) >= 2:
            for i in range(len(correlation_questions)):
                for j in range(i + 1, len(correlation_questions)):
                    q1_id, q2_id = correlation_questions[i], correlation_questions[j]
                    try:
                        q1 = Question.objects.get(id=q1_id, survey=survey)
                        q2 = Question.objects.get(id=q2_id, survey=survey)
                        
                        correlation_key = f"{q1_id}_{q2_id}"
                        correlation_data = self._calculate_correlation(q1, q2, responses)
                        stats['correlations'][correlation_key] = {
                            'questions': [q1.question_text, q2.question_text],
                            'data': correlation_data
                        }
                    except Question.DoesNotExist:
                        continue

        # Pattern recognition
        if group_by:
            patterns = self._recognize_patterns(survey, responses, group_by)
            stats['patterns'] = patterns

        return DRFResponse(stats)

    def _calculate_correlation(self, q1, q2, responses):
        """Calculate correlation between two questions"""
        correlation_data = {
            'joint_distribution': {},
            'correlation_strength': None
        }

        # Get answers for both questions
        answers1 = Answer.objects.filter(question=q1, response__in=responses)
        answers2 = Answer.objects.filter(question=q2, response__in=responses)

        # Create a mapping of response_id to answers
        answers1_map = {a.response_id: a.value for a in answers1}
        answers2_map = {a.response_id: a.value for a in answers2}

        # Calculate joint distribution
        common_responses = set(answers1_map.keys()) & set(answers2_map.keys())
        
        for response_id in common_responses:
            val1 = str(answers1_map[response_id])
            val2 = str(answers2_map[response_id])
            key = f"{val1}_{val2}"
            correlation_data['joint_distribution'][key] = correlation_data['joint_distribution'].get(key, 0) + 1

        # Calculate correlation strength if both questions are numeric
        if q1.question_type == Question.QUESTION_TYPES.RATING and q2.question_type == Question.QUESTION_TYPES.RATING:
            values1 = [float(answers1_map[r]) for r in common_responses]
            values2 = [float(answers2_map[r]) for r in common_responses]
            
            if values1 and values2:
                correlation_data['correlation_strength'] = numpy.corrcoef(values1, values2)[0, 1]

        return correlation_data

    def _recognize_patterns(self, survey, responses, group_by):
        """Recognize patterns in survey responses based on grouping"""
        patterns = {
            'group_analysis': {},
            'trends': {},
            'clusters': {}
        }

        if group_by == 'date':
            # Temporal patterns
            date_groups = responses.extra(
                select={'date': "DATE(submitted_at)"}
            ).values('date').annotate(
                response_count=Count('id'),
                avg_completion_time=Avg(F('submitted_at') - F('created_at'))
            ).order_by('date')
            
            patterns['group_analysis'] = list(date_groups)

        elif group_by.startswith('respondent__'):
            # Demographic patterns
            demographic_field = group_by.split('__')[1]
            demographic_groups = responses.values(
                f'respondent__{demographic_field}'
            ).annotate(
                response_count=Count('id')
            ).order_by(f'respondent__{demographic_field}')
            
            patterns['group_analysis'] = list(demographic_groups)

        # Identify trends
        for question in survey.questions.all():
            if question.question_type in [Question.QUESTION_TYPES.RATING, Question.QUESTION_TYPES.SINGLE]:
                trend_data = Answer.objects.filter(
                    question=question,
                    response__in=responses
                ).extra(
                    select={'date': "DATE(submitted_at)"}
                ).values('date').annotate(
                    avg_value=Avg(Cast('value', FloatField()))
                ).order_by('date')
                
                patterns['trends'][question.id] = list(trend_data)

        return patterns
    # @action(detail=True, methods=['get'])
    # def statistics(self, request, pk=None):
    #     survey = self.get_object()
        
    #     if not survey.is_closed:
    #         return DRFResponse(
    #             {'error': 'Survey is still active'}, 
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     stats = {
    #         'total_responses': survey.responses.count(),
    #         'questions': []
    #     }

    #     for question in survey.questions.all():
    #         question_stats = {
    #             'question_text': question.question_text,
    #             'question_type': question.question_type,
    #         }
    #         # rating_questions = Question.objects.filter(survey=survey, question_type=Question.QUESTION_TYPES.RATING)
    #         answers = Answer.objects.filter(question=question)
            
    #         if question.question_type in [Question.QUESTION_TYPES.SINGLE, Question.QUESTION_TYPES.MULTIPLE]:
    #             option_counts = {}
    #             CHOICE_KEY = 'choices' if question.question_type == Question.QUESTION_TYPES.MULTIPLE else 'choice'
    #             for answer in answers:
    #                 choices = answer.value.get(CHOICE_KEY) # or answer.value.get('choice')
    #                 if isinstance(choices, list):
    #                     for choice in choices:
    #                         option_counts[choice] = option_counts.get(choice, 0) + 1
    #                 else:
    #                     option_counts[choices] = option_counts.get(choices, 0) + 1
    #             question_stats['option_distribution'] = option_counts
                
    #         elif question.question_type == 'rating':
    #             rating_stats = answers.aggregate(
    #                 avg_rating=Avg(Cast('value', FloatField())),
    #                 max_rating=Max(Cast('value', FloatField())),
    #                 min_rating=Min(Cast('value', FloatField())),
    #                 count_ratings=Count('id')
    #             )
    #             question_stats.update({
    #                 'average_rating': float(rating_stats['avg_rating']) if rating_stats['avg_rating'] is not None else None,
    #                 'max_rating': float(rating_stats['max_rating']) if rating_stats['max_rating'] is not None else None,
    #                 'min_rating': float(rating_stats['min_rating']) if rating_stats['min_rating'] is not None else None,
    #                 'total_ratings': rating_stats['count_ratings']
    #             })

    #         stats['questions'].append(question_stats)
    #     return DRFResponse(stats)

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
        ## seems a response is created , use transaction
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