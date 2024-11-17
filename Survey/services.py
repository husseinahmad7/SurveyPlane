from .models import Answer,Question
import numpy as np
from collections import defaultdict

ACCEPTED_Q_TYPES = [Question.QUESTION_TYPES.RATING, Question.QUESTION_TYPES.SINGLE, Question.QUESTION_TYPES.MULTIPLE]

def _calculate_general_correlation(survey, responses):
        """Calculate correlations between different questions in the survey"""
        correlations = {}
        questions = survey.questions.all()
        
        for i, q1 in enumerate(questions):
            for j, q2 in enumerate(questions):
                if j <= i:  # Avoid duplicate pairs and self-correlation
                    continue
                
                # Get answers for both questions
                answers1 = Answer.objects.filter(question=q1, response__in=responses)
                answers2 = Answer.objects.filter(question=q2, response__in=responses)
                
                # Skip if either question has no answers
                if not answers1.exists() or not answers2.exists():
                    continue
                
                # Create a mapping of response_id to answer for each question
                answers1_map = {a.response_id: a for a in answers1}
                answers2_map = {a.response_id: a for a in answers2}
                
                # Find common responses
                common_responses = set(answers1_map.keys()) & set(answers2_map.keys())
                
                if not common_responses:
                    continue
                
                joint_distribution = {}
                correlation_strength = None
                
                # Handle different question type combinations
                if q1.question_type not in ACCEPTED_Q_TYPES or q2.question_type not in ACCEPTED_Q_TYPES:
                    continue
                if q1.question_type == Question.QUESTION_TYPES.RATING and q2.question_type == Question.QUESTION_TYPES.RATING:
                    # Rating-Rating correlation
                    values1 = []
                    values2 = []
                    for response_id in common_responses:
                        val1 = float(answers1_map[response_id].value)
                        val2 = float(answers2_map[response_id].value)
                        values1.append(val1)
                        values2.append(val2)
                        key = f"{val1}_{val2}"
                        joint_distribution[key] = joint_distribution.get(key, 0) + 1
                    
                    if len(values1) > 1:  # Need at least 2 points for correlation
                        correlation_strength = float(np.corrcoef(values1, values2)[0, 1])
                
                elif q1.question_type in [Question.QUESTION_TYPES.SINGLE, Question.QUESTION_TYPES.MULTIPLE] and \
                     q2.question_type == Question.QUESTION_TYPES.RATING:
                    # Choice-Rating correlation
                    choice_ratings = defaultdict(list)
                    for response_id in common_responses:
                        choices = answers1_map[response_id].value.get('choices', [answers1_map[response_id].value.get('choice')])
                        rating = float(answers2_map[response_id].value)
                        
                        for choice in choices:
                            key = f"{choice}_{rating}"
                            joint_distribution[key] = joint_distribution.get(key, 0) + 1
                            choice_ratings[choice].append(rating)
                    
                    # Calculate average rating for each choice
                    avg_ratings = {
                        choice: {
                            'mean': float(np.mean(ratings)),
                            'std': float(np.std(ratings)) if len(ratings) > 1 else 0
                        }
                        for choice, ratings in choice_ratings.items()
                    }
                    correlation_strength = avg_ratings
                
                elif q2.question_type in [Question.QUESTION_TYPES.SINGLE, Question.QUESTION_TYPES.MULTIPLE] and \
                     q1.question_type == Question.QUESTION_TYPES.RATING:
                    # Rating-Choice correlation (swap order)
                    choice_ratings = defaultdict(list)
                    for response_id in common_responses:
                        choices = answers2_map[response_id].value.get('choices', [answers2_map[response_id].value.get('choice')])
                        rating = float(answers1_map[response_id].value)
                        
                        for choice in choices:
                            key = f"{rating}_{choice}"
                            joint_distribution[key] = joint_distribution.get(key, 0) + 1
                            choice_ratings[choice].append(rating)
                    
                    # Calculate average rating for each choice
                    avg_ratings = {
                        choice: {
                            'mean': float(np.mean(ratings)),
                            'std': float(np.std(ratings)) if len(ratings) > 1 else 0
                        }
                        for choice, ratings in choice_ratings.items()
                    }
                    correlation_strength = avg_ratings
                
                else:
                    # Choice-Choice correlation
                    for response_id in common_responses:
                        choices1 = answers1_map[response_id].value.get('choices', [answers1_map[response_id].value.get('choice')])
                        choices2 = answers2_map[response_id].value.get('choices', [answers2_map[response_id].value.get('choice')])
                        
                        for c1 in choices1:
                            for c2 in choices2:
                                key = f"{c1}_{c2}"
                                joint_distribution[key] = joint_distribution.get(key, 0) + 1
                
                pair_key = f"{q1.id}_{q2.id}"
                correlations[pair_key] = {
                    "questions": [q1.question_text, q2.question_text],
                    "question_types": [q1.question_type, q2.question_type],
                    "data": {
                        "joint_distribution": joint_distribution,
                        "correlation_strength": correlation_strength
                    }
                }
        
        return {"correlations": correlations}