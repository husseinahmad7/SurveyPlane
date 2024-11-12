# ... (rest of the file remains the same)

class Question(models.Model):
    # ... (rest of the class remains the same)

    class QUESTION_TYPES(models.TextChoices):
        # ... (rest of the choices remain the same)
        IMAGE = ('image', 'Image')

    # ... (rest of the class remains the same)

    def get_settings_schema(self):
        """Return the expected settings schema for each question type"""
        schemas = {
            # ... (rest of the schemas remain the same)
            'image': {
                'answer_type': {'type': str, 'required': True, 'choices': ['text', 'choice', 'choices']},
                'choices': {'type': list, 'required': False, 'default': None},
                'min_selections': {'type': int, 'required': False, 'default': None},
                'max_selections': {'type': int, 'required': False, 'default': None},
            },
        }
        return schemas.get(self.question_type, {})
