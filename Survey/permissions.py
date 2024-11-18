from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Survey, Response
class IsVerified(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_verified)
    
class SurveyAccessPermission(BasePermission):
    """
    Custom permission for Survey access:
    - Unauthenticated users can see active surveys
    - Authenticated but unverified users can see active surveys
    - Authenticated and verified users can see their own surveys
    """
    
    def has_permission(self, request, view):
        # Allow all users to access list and retrieve actions
        if view.action in ['list', 'retrieve']:
            return True
        # For other actions, require authentication and verified
        return request.user and request.user.is_authenticated and request.user.is_verified
    
    def has_object_permission(self, request, view, obj):
        # For retrieve action
        if view.action == 'retrieve':
            # If user is authenticated and verified, check if they own the survey
            if request.user.is_authenticated and request.user.is_verified:
                return obj.creator == request.user
            # For other users, only allow access to active surveys
            return obj.is_active
        
        # For other actions (update, delete, etc.)
        return request.user.is_authenticated and request.user.is_verified and obj.creator == request.user



class QuestionAccessPermission(BasePermission):
    """
    Custom permission for Question access:
    - Unauthenticated users can see questions of active surveys
    - Authenticated but unverified users can see questions of active surveys
    - Only survey creators can create/update/delete questions
    """
    
    def has_permission(self, request, view):
        # Allow all users to access list and retrieve actions
        if view.action in ['list', 'retrieve','survey_questions']:
            return True
            
        # For create/update/delete, require authentication
        return request.user and request.user.is_authenticated and request.user.is_verified
    
    def has_object_permission(self, request, view, obj):
        # For retrieve action
        if view.action == 'retrieve':
            # If user is authenticated and verified, check if they own the survey
            if request.user.is_authenticated and request.user.is_verified:
                return obj.survey.creator == request.user
            # For other users, only allow access to questions of active surveys
            return obj.survey.is_active
        
        # For other actions (update, delete, etc.)
        return request.user.is_authenticated and request.user.is_verified and obj.survey.creator == request.user



class ResponseAccessPermission(BasePermission):
    """
    Custom permission for Response access based on survey's auth requirement:
    - NONE: Any user can respond
    - QUICK: Must be authenticated (verified or not)
    - FULL: Must be authenticated and verified
    """
    
    def has_permission(self, request, view):
        # Always allow GET requests for list/retrieve
        if request.method in SAFE_METHODS:
            return True
            
        # For POST/PUT/PATCH/DELETE, check survey auth requirement
        if view.action == 'create':
            survey_id = request.data.get('survey')
            try:
                survey = Survey.objects.get(pk=survey_id)
            except Survey.DoesNotExist:
                return False
                
            # Check auth requirements
            if survey.respondent_auth_requirement == Survey.AuthRequirement.NONE:
                return True
            elif survey.respondent_auth_requirement == Survey.AuthRequirement.QUICK:
                return request.user and request.user.is_authenticated
            elif survey.respondent_auth_requirement == Survey.AuthRequirement.FULL:
                return request.user and request.user.is_authenticated and request.user.is_verified
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # For GET requests
        if request.method in SAFE_METHODS:
            # Allow survey creator to view responses
            if request.user and request.user.is_authenticated:
                if obj.survey.creator == request.user:
                    return True
            # Allow respondent to view their own responses
            if request.user and request.user.is_authenticated and obj.respondent == request.user:
                return True
            return False
        
        # For modification requests
        # Only allow respondent to modify their own responses if survey is still active
        return (request.user and request.user.is_authenticated and 
                obj.respondent == request.user and not obj.survey.is_closed)



class ResponseAnswerAccessPermission(BasePermission):
    """
    Custom permission for ResponseAnswer access:
    - Only authenticated users can access
    - Users can only access their own response answers
    - Survey creators can view answers to their surveys
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # For bulk create, check if response belongs to user
        if view.action == 'bulk_create':
            response_id = request.data[0].get('response') if request.data else None
            if not response_id:
                return False
                
            try:
                response = Response.objects.get(pk=response_id)
                return response.respondent == request.user
            except Response.DoesNotExist:
                return False
                
        # For create, check if response belongs to user
        if view.action == 'create':
            response_id = request.data.get('response')
            if not response_id:
                return False
                
            try:
                response = Response.objects.get(pk=response_id)
                return response.respondent == request.user
            except Response.DoesNotExist:
                return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        # Allow survey creator to view answers
        if obj.response.survey.creator == request.user:
            return True
            
        # Allow respondent to view/modify their own answers
        if obj.response.respondent == request.user:
            # For modification requests, check if survey is still active
            if request.method not in SAFE_METHODS:
                return not obj.response.survey.is_closed
            return True
            
        return False
