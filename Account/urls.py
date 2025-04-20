from django.urls import path
from . import views

urlpatterns = [
    path('respondent_signup/', views.RespondentSignup.as_view(), name='respondent_signup'),
    path('respondent_signin/', views.RespondentLogin.as_view(), name='respondent_signin'),

    # Override the default authemail verification views
    path('signup/verify/', views.SignupVerify.as_view(), name='signup_verify'),
    path('password/reset/verify/', views.PasswordResetVerify.as_view(), name='password_reset_verify'),
]