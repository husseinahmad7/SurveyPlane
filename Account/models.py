from django.db import models
from authemail.models import EmailUserManager, EmailAbstractUser

class User(EmailAbstractUser):
	# Custom fields
	date_of_birth = models.DateField('Date of birth', null=True, blank=True)

	# Required
	objects = EmailUserManager()