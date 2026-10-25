from django.contrib import admin
from .models import Answer, Attempt, Choice, Question, Quiz, Topic

admin.site.site_header = "Quizzi Arena · Quản trị"
admin.site.site_title = "Quản trị Quizzi Arena"
admin.site.index_title = "Quản lý chủ đề và câu hỏi"
admin.site.site_url = "/"

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "is_published", "created_at")
    list_filter = ("topic", "is_published")
    search_fields = ("title", "subject", "topic__name")
    inlines = (QuestionInline,)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published", "created_at")
    search_fields = ("name", "description")

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "order")
    list_filter = ("quiz__topic", "quiz")
    search_fields = ("text", "quiz__title")
    inlines = (ChoiceInline,)

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("nickname", "quiz", "score", "started_at", "completed_at")
    list_filter = ("quiz__topic", "quiz", "completed_at")
    search_fields = ("nickname", "quiz__title")

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "is_correct", "points_earned", "answered_at")
    list_filter = ("is_correct", "question__quiz__topic")
