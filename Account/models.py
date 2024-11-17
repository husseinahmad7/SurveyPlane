from django.db import models
from authemail.models import EmailUserManager, EmailAbstractUser

class User(EmailAbstractUser):
    
	class Gender(models.TextChoices):
		MALE = 'M', 'Male'
		FEMALE = 'F', 'Female'

	# Custom fields
	date_of_birth = models.DateField('Date of birth', null=True, blank=True)
	location = models.CharField('Location', max_length=30, null=True, blank=True)
	gender = models.CharField('Gender', max_length=1, null=True, blank=True, choices=Gender.choices)
	# Required
	objects = EmailUserManager()