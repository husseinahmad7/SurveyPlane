from rest_framework import serializers
from ipware import get_client_ip

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect
from django.http import HttpResponse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authemail.models import SignupCode, EmailChangeCode, PasswordResetCode
from authemail.models import send_multi_format_email
from authemail.serializers import LoginSerializer
from authemail.views import SignupVerify as BaseSignupVerify
from authemail.views import PasswordResetVerify as BasePasswordResetVerify
from django.contrib.auth import get_user_model
User = get_user_model()


class RespondentSignup(APIView):
    """
    there is Full or Quick signup types, the full type must include email and confirm it,
    the quick type does not require confirming the email.
    """
    class SignupSerializer(serializers.Serializer):
        """
        Don't require email to be unique so visitor can signup multiple times,
        if misplace verification email.  Handle in view.
        """
        email = serializers.EmailField(max_length=255)
        password = serializers.CharField(max_length=128)
        first_name = serializers.CharField(max_length=30)
        last_name = serializers.CharField(max_length=30)
        date_of_birth = serializers.DateField()
        location = serializers.CharField(max_length=30)
        gender = serializers.ChoiceField(choices=User.Gender.choices)


    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        signup_type = request.data.get('signup_type', 'quick')

        if serializer.is_valid():
            email = serializer.data['email']
            password = serializer.data['password']
            first_name = serializer.data['first_name']
            last_name = serializer.data['last_name']
            date_of_birth = serializer.data['date_of_birth']
            gender = serializer.data['gender']
            location = serializer.data['location']


            must_validate_email = getattr(settings, "AUTH_EMAIL_VERIFICATION", True)

            try:
                user = get_user_model().objects.get(email=email)
                if user.is_verified:
                    content = {'detail': _('Email address already taken.')}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)

                try:
                    # Delete old signup codes
                    signup_code = SignupCode.objects.get(user=user)
                    signup_code.delete()
                except SignupCode.DoesNotExist:
                    pass

            except get_user_model().DoesNotExist:
                user = get_user_model().objects.create_user(email=email)


            # Set user fields provided
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.date_of_birth = date_of_birth
            user.location = location
            user.gender = gender
            if not must_validate_email:
                user.is_verified = True
                send_multi_format_email('welcome_email',
                                        {'email': user.email, },
                                        target_email=user.email)
            user.save()
            # if the signup type is full, send verification email
            if must_validate_email and signup_type == 'full':
                # Create and associate signup code
                client_ip = get_client_ip(request)[0]
                if client_ip is None:
                    client_ip = '0.0.0.0'    # Unable to get the client's IP address
                signup_code = SignupCode.objects.create_signup_code(user, client_ip)
                signup_code.send_signup_email()

            content = {'email': email, 'first_name': first_name,
                       'last_name': last_name, 'date_of_birth': date_of_birth,
                       'location': location, 'gender': gender}
            if signup_type == 'quick':
                token, created = Token.objects.get_or_create(user=user)
                content['token'] = token.key

            return Response(content, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RespondentLogin(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.data['email']
            password = serializer.data['password']
            user = authenticate(email=email, password=password)

            if user:
                # if user.is_verified:
                    if user.is_active:
                        token, created = Token.objects.get_or_create(user=user)
                        return Response({'token': token.key},
                                        status=status.HTTP_200_OK)
                    else:
                        content = {'detail': _('User account not active.')}
                        return Response(content,
                                        status=status.HTTP_401_UNAUTHORIZED)
                # else:
                #     content = {'detail':
                #                _('User account not verified.')}
                #     return Response(content, status=status.HTTP_401_UNAUTHORIZED)
            else:
                content = {'detail':
                           _('Unable to login with provided credentials.')}
                return Response(content, status=status.HTTP_401_UNAUTHORIZED)


class SignupVerify(BaseSignupVerify):
    """
    Custom view to override the default signup verification view
    to provide a user-friendly HTML response instead of JSON.
    """
    def get(self, request):
        code = request.GET.get('code', '')
        output = request.GET.get('output', '')
        try:
            signup_code = SignupCode.objects.get(code=code)
            user = signup_code.user
            user.is_verified = True
            user.save()
            signup_code.delete()
            # Send welcome email
            send_multi_format_email('welcome_email',
                                  {'email': user.email},
                                  target_email=user.email)
            if output == 'json':
                return Response({'detail': 'Email verification successful'}, status=status.HTTP_200_OK)
            # Return HTML response instead of JSON
            return render(request, 'verification_success.html')
        except SignupCode.DoesNotExist:
            if output == 'json':
                return Response({'detail': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
            return HttpResponse("Invalid verification code", status=400)


class PasswordResetVerify(BasePasswordResetVerify):
    """
    Custom view to override the default password reset verification view
    to provide a user-friendly HTML response instead of JSON.
    """
    def get(self, request):
        code = request.GET.get('code', '')
        output = request.GET.get('output', '')
        try:
            # Just check if the code exists
            PasswordResetCode.objects.get(code=code)
            if output == 'json':
                return Response({'detail': 'Password reset code is valid'}, status=status.HTTP_200_OK)
            # Return HTML response instead of JSON
            return render(request, 'password_reset_success.html')
        except PasswordResetCode.DoesNotExist:
            if output == 'json':
                return Response({'detail': 'Invalid password reset code'}, status=status.HTTP_400_BAD_REQUEST)
            return HttpResponse("Invalid password reset code", status=400)