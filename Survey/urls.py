
from rest_framework import routers
from django.urls import path, include
from .views import SurveyViewSet, QuestionViewSet, ResponseViewSet, ResponseAnswerViewSet,SurveyResponseManagementView
router = routers.DefaultRouter()
router.register(r'surveys', SurveyViewSet, basename='survey')

# surveys_router = routers.NestedDefaultRouter(router, r'surveys', lookup='survey')
question_router = routers.DefaultRouter()

question_router.register(r'questions', QuestionViewSet, basename='survey-questions')
response_router = routers.DefaultRouter()
 
response_router.register(r'responses', ResponseViewSet, basename='survey-responses')


answers_router = routers.DefaultRouter()
answers_router.register(r'answers', ResponseAnswerViewSet, basename='response-answers')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(question_router.urls)),
    path('', include(response_router.urls)),
    path('', include(answers_router.urls)),
    # Survey Response Management URLs
    path('surveys/<int:survey_id>/responses/', SurveyResponseManagementView.as_view(), name='survey-mng-responses'),
    path('surveys/<int:survey_id>/responses/<int:response_id>/', SurveyResponseManagementView.as_view(), name='survey-response-detail'),
    path('surveys/<int:survey_id>/responses/export/', SurveyResponseManagementView.as_view(export_pdf=True), name='survey-responses-export'),

]