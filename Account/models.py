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
	# is_quick_user = models.BooleanField(
    #     'Quick registration user',
    #     default=False,
    #     help_text='Designates whether this user was created through quick registration'
    # )
	# Required
	objects = EmailUserManager()

	# def save(self, *args, **kwargs):
	# 	if self.is_quick_user:
	# 		   self.is_verified = True  # Auto-verify quick registration users
	# 		   super().save(*args, **kwargs)