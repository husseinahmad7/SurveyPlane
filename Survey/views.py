# serializers.py
from rest_framework import serializers
from .models import Survey, Question, Response, Answer

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'required', 'order', 'options']

class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    is_closed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'creator', 'created_at', 
                 'closes_at', 'is_active', 'is_closed', 'questions']
        read_only_fields = ['creator', 'created_at']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'answer_text', 'answer_choice']

class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Response
        fields = ['id', 'survey', 'respondent', 'submitted_at', 'answers']
        read_only_fields = ['submitted_at']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        response = Response.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(response=response, **answer_data)
        return response

# views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse
from django.db.models import Count, Avg
from django.utils import timezone

class SurveyViewSet(viewsets.ModelViewSet):
    serializer_class = SurveySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            # For list action, show all active surveys
            return Survey.objects.filter(is_active=True)
        # For other actions, show all surveys created by the user
        return Survey.objects.filter(creator=self.request.user)

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

            answers = Answer.objects.filter(question=question)
            
            if question.question_type in ['single_choice', 'multiple_choice']:
                option_counts = {}
                for answer in answers:
                    choices = answer.answer_choice
                    if isinstance(choices, list):
                        for choice in choices:
                            option_counts[choice] = option_counts.get(choice, 0) + 1
                    else:
                        option_counts[choices] = option_counts.get(choices, 0) + 1
                question_stats['option_distribution'] = option_counts
                
            elif question.question_type == 'rating':
                avg_rating = answers.aggregate(Avg('answer_text'))
                question_stats['average_rating'] = avg_rating['answer_text__avg']

            stats['questions'].append(question_stats)

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

class ResponseViewSet(viewsets.ModelViewSet):
    serializer_class = ResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            # Staff can see all responses
            return Response.objects.all()
        # Regular users can only see their own responses
        return Response.objects.filter(respondent=self.request.user)

    def perform_create(self, serializer):
        survey = Survey.objects.get(pk=self.kwargs['survey_pk'])
        
        if survey.is_closed:
            raise serializers.ValidationError("Survey is closed")
            
        serializer.save(
            survey=survey,
            respondent=self.request.user if self.request.user.is_authenticated else None
        )