# ... (rest of the file remains the same)

class AnswerSerializer(serializers.ModelSerializer):
    # ... (rest of the class remains the same)

    def validate(self, data):
        # ... (rest of the method remains the same)

        question_type = data.get('question_type', None)
        if question_type == Question.QUESTION_TYPES.IMAGE:
            answer_type = data.get('value', {}).get('answer_type')
            if answer_type not in ['text', 'choice', 'choices']:
                raise serializers.ValidationError({'value': 'answer_type must be one of text, choice, or choices'})

            if answer_type == 'choice' or answer_type == 'choices':
                if 'choices' not in data.get('value', {}):
                    raise serializers.ValidationError({'value': 'choices are required for choice or choices answer type'})

            if answer_type == 'choice' and len(data.get('value', {}).get('choices', [])) > 1:
                raise serializers.ValidationError({'value': 'only one choice is allowed for choice answer type'})

        # ... (rest of the method remains the same)
