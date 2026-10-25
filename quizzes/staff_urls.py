from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="quiz/staff_login.html", redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("quizzes/", views.staff_dashboard, name="staff"),
    path("quizzes/create/", views.create_quiz, name="create"),
    path("topics/create/", views.create_topic, name="create_topic"),
    path("topics/<int:topic_id>/delete/", views.delete_topic, name="delete_topic"),
    path("quizzes/<int:quiz_id>/delete/", views.delete_quiz, name="delete"),
]
