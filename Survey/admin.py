from django.contrib import admin
from django.utils.html import format_html
from .models import Survey, Question, Response, Answer
from django.conf import settings
from .config import ANSWER_FILE_PATH_KEY

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('question_text', 'question_type', 'required', 'order')
    ordering = ('order',)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('get_question_text', 'formatted_value')
    fields = ('get_question_text', 'formatted_value')
    can_delete = True
    max_num = 0  # Prevents adding new answers through admin

    def get_question_text(self, obj):
        return obj.question.question_text if obj.question else ''
    get_question_text.short_description = 'Question'

    def formatted_value(self, obj):
        if obj.question.question_type == 'file' and obj.value and obj.value.get(ANSWER_FILE_PATH_KEY):
        #     return format_html('<a href="{}" target="_blank">View File</a>', obj.value['file_path'])
            file_path = obj.value[ANSWER_FILE_PATH_KEY]
            if not file_path.startswith('/') and not settings.MEDIA_URL.endswith('/'):
                file_path = '/' + file_path
            return format_html('<a href="{}" target="_blank">View File</a>', settings.MEDIA_URL + file_path)
  
        return str(obj.value)
    formatted_value.short_description = 'Answer'

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'closes_at', 'is_active', 'response_count')
    list_filter = ('is_active', 'created_at', 'closes_at')
    search_fields = ('title', 'description', 'creator__username')
    readonly_fields = ('created_at',)
    inlines = [QuestionInline]
    date_hierarchy = 'created_at'

    def response_count(self, obj):
        return obj.responses.count()
    response_count.short_description = 'Responses'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'survey', 'question_type', 'required', 'order')
    list_filter = ('survey', 'question_type', 'required')
    search_fields = ('question_text', 'survey__title')
    ordering = ('survey', 'order')
    # raw_id_fields = ('survey',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('question_type',) + self.readonly_fields
        return self.readonly_fields

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'respondent', 'submitted_at', 'answer_count')
    list_filter = ('survey', 'submitted_at')
    search_fields = ('survey__title', 'respondent__username')
    readonly_fields = ('submitted_at',)
    inlines = [AnswerInline]
    date_hierarchy = 'submitted_at'

    def answer_count(self, obj):
        return obj.answers.count()
    answer_count.short_description = 'Number of Answers'

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_question_text', 'get_response_info', 'formatted_value')
    list_filter = ('question__question_type', 'response__survey')
    search_fields = ('question__question_text', 'response__survey__title')
    readonly_fields = ('formatted_value',)

    def get_question_text(self, obj):
        return obj.question.question_text
    get_question_text.short_description = 'Question'

    def get_response_info(self, obj):
        return f"Response #{obj.response.id} - {obj.response.survey.title}"
    get_response_info.short_description = 'Response'

    def formatted_value(self, obj):
        if obj.question.question_type == 'file' and obj.value and obj.value.get(ANSWER_FILE_PATH_KEY):
            # return format_html('<a href="{}" target="_blank">View File</a>', obj.value['file_path'])
            file_path = obj.value[ANSWER_FILE_PATH_KEY]
            if not file_path.startswith('/') and not settings.MEDIA_URL.endswith('/'):
                file_path = '/' + file_path
            return format_html('<a href="{}" target="_blank">View File</a>', settings.MEDIA_URL + file_path)

        return str(obj.value)
    formatted_value.short_description = 'Answer'
