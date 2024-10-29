
from rest_framework import routers
from django.urls import path, include
from .views import SurveyViewSet, QuestionViewSet, ResponseViewSet
router = routers.DefaultRouter()
router.register(r'surveys', SurveyViewSet, basename='survey')

# surveys_router = routers.NestedDefaultRouter(router, r'surveys', lookup='survey')
question_router = routers.DefaultRouter()

question_router.register(r'questions', QuestionViewSet, basename='survey-questions')
response_router = routers.DefaultRouter()
 
response_router.register(r'responses', ResponseViewSet, basename='survey-responses')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(question_router.urls)),
    path('', include(response_router.urls)),
]