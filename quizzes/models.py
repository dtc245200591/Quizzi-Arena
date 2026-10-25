from django.conf import settings
from django.db import models
from django.utils import timezone
import uuid


class Topic(models.Model):
    name = models.CharField(max_length=80, unique=True, verbose_name="Tên chủ đề")
    description = models.CharField(max_length=300, blank=True, verbose_name="Mô tả")
    icon = models.CharField(max_length=8, default="🌱", verbose_name="Biểu tượng")
    color = models.CharField(max_length=20, default="tím", verbose_name="Màu chủ đề")
    is_published = models.BooleanField(default=True, verbose_name="Đang hiển thị")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        ordering = ["name"]
        verbose_name = "Chủ đề"
        verbose_name_plural = "Chủ đề"

    def __str__(self):
        return self.name

class Quiz(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name="quizzes", verbose_name="Chủ đề")
    title = models.CharField(max_length=140, verbose_name="Tên bộ quiz")
    subject = models.CharField(max_length=80, blank=True, verbose_name="Môn học")
    description = models.CharField(max_length=500, blank=True, verbose_name="Mô tả")
    seconds_per_question = models.PositiveSmallIntegerField(default=20, verbose_name="Thời gian mỗi câu (giây)")
    is_published = models.BooleanField(default=True, verbose_name="Công khai")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Bộ quiz"
        verbose_name_plural = "Bộ quiz"

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions", verbose_name="Bộ quiz")
    text = models.CharField(max_length=300, verbose_name="Nội dung câu hỏi")
    explanation = models.TextField(blank=True, verbose_name="Giải thích đáp án")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Thứ tự")
    points = models.PositiveSmallIntegerField(default=100, verbose_name="Điểm")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Câu hỏi"
        verbose_name_plural = "Câu hỏi"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices", verbose_name="Câu hỏi")
    text = models.CharField(max_length=180, verbose_name="Nội dung lựa chọn")
    is_correct = models.BooleanField(default=False, verbose_name="Là đáp án đúng")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Thứ tự")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Lựa chọn"
        verbose_name_plural = "Lựa chọn"

class Attempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts", verbose_name="Bộ quiz")
    nickname = models.CharField(max_length=40, verbose_name="Biệt danh")
    access_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="Mã lượt chơi")
    score = models.PositiveIntegerField(default=0, verbose_name="Điểm số")
    started_at = models.DateTimeField(default=timezone.now, verbose_name="Bắt đầu lúc")
    question_started_at = models.DateTimeField(default=timezone.now, verbose_name="Bắt đầu câu hiện tại")
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name="Hoàn thành lúc")

    class Meta:
        ordering = ["-score", "completed_at"]
        verbose_name = "Lượt chơi"
        verbose_name_plural = "Lượt chơi"

class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers", verbose_name="Lượt chơi")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Câu hỏi")
    choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Lựa chọn")
    is_correct = models.BooleanField(default=False, verbose_name="Trả lời đúng")
    points_earned = models.PositiveIntegerField(default=0, verbose_name="Điểm nhận được")
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name="Trả lời lúc")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["attempt", "question"], name="unique_quiz_answer")]
        verbose_name = "Câu trả lời"
        verbose_name_plural = "Câu trả lời"
