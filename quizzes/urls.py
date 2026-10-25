from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "quizzes"
urlpatterns = [
    path("", views.quiz_list, name="list"),
    path("quiz/<int:quiz_id>/", views.quiz_detail, name="detail"),
    path("quiz/<int:quiz_id>/start/", views.start_quiz, name="start"),
    path("quiz/<int:quiz_id>/play/", views.quiz_play, name="play"),
    path("result/<uuid:token>/", views.quiz_result, name="result"),
]
