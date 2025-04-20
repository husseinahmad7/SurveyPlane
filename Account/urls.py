from django.urls import path
from . import views

urlpatterns = [
    path('respondent_signup/', views.RespondentSignup.as_view(), name='respondent_signup'),
    path('respondent_signin/', views.RespondentLogin.as_view(), name='respondent_signin')
]