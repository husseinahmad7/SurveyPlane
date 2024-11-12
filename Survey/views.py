# ... (rest of the file remains the same)

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'required', 'order', 'settings']

    def validate(self, data):
        # ... (rest of the method remains the same)

        if data.get('question_type') == Question.QUESTION_TYPES.IMAGE:
            if 'answer_type' not in data['settings'] or not data['settings']['answer_type']:
                raise serializers.ValidationError({'settings': 'answer_type is required for image questions'})
            if data['settings']['answer_type'] not in ['text', 'choice', 'choices']:
                raise serializers.ValidationError({'settings': 'answer_type must be one of text, choice, or choices'})

        # ... (rest of the method remains the same)
