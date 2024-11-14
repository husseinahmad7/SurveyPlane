from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
from .models import Question, Answer
from .config import QUESTION_ATTACHEMENT_FILE_PATH_KEY, ANSWER_FILE_PATH_KEY
@receiver(pre_delete, sender=Question)
def delete_question_file(sender, instance, **kwargs):
    """Delete the attached file when a question is deleted if it exists"""
    if instance.settings and instance.settings.get(QUESTION_ATTACHEMENT_FILE_PATH_KEY):
        file_path = instance.settings.get(QUESTION_ATTACHEMENT_FILE_PATH_KEY)
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

@receiver(pre_delete, sender=Answer)
def delete_answer_file(sender, instance, **kwargs):
    """Delete the file when an answer to a file question is deleted"""
    if instance.question.question_type == Question.QUESTION_TYPES.FILE and instance.value and instance.value.get(ANSWER_FILE_PATH_KEY):
        file_path = instance.value.get(ANSWER_FILE_PATH_KEY)
        if default_storage.exists(file_path):
            default_storage.delete(file_path)