import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Answer, Attempt, Choice, Question, Quiz, Topic


def quiz_list(request):
    topics = Topic.objects.filter(is_published=True).annotate(
        quiz_total=Count("quizzes", filter=Q(quizzes__is_published=True), distinct=True),
        question_total=Count("quizzes__questions", filter=Q(quizzes__is_published=True), distinct=True),
    )
    quizzes = Quiz.objects.filter(is_published=True).select_related("topic").annotate(question_total=Count("questions"))
    query = request.GET.get("q", "").strip()
    if query:
        quizzes = quizzes.filter(Q(title__icontains=query) | Q(subject__icontains=query) | Q(topic__name__icontains=query))
    selected_topic = request.GET.get("topic", "")
    active_topic = None
    if selected_topic.isdigit():
        quizzes = quizzes.filter(topic_id=int(selected_topic))
        active_topic = topics.filter(pk=int(selected_topic)).first()
    return render(request, "quiz/list.html", {
        "quizzes": quizzes,
        "topics": topics,
        "query": query,
        "selected_topic": selected_topic,
        "active_topic": active_topic,
    })


def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(
        Quiz.objects.select_related("topic").annotate(
            question_total=Count("questions"), max_score=Sum("questions__points")
        ),
        pk=quiz_id,
    )
    if not quiz.is_published and not request.user.is_staff:
        return redirect("quizzes:list")
    leaderboard = quiz.attempts.filter(completed_at__isnull=False).order_by("-score", "completed_at")[:8]
    return render(request, "quiz/detail.html", {"quiz": quiz, "leaderboard": leaderboard})


@require_POST
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, is_published=True)
    nickname = " ".join(request.POST.get("nickname", "").split())[:40]
    if not nickname:
        messages.error(request, "Nhập biệt danh trước khi bắt đầu nhé!")
        return redirect("quizzes:detail", quiz_id=quiz.id)
    if not quiz.questions.exists():
        messages.error(request, "Quiz này chưa có câu hỏi.")
        return redirect("quizzes:detail", quiz_id=quiz.id)
    attempt = Attempt.objects.create(quiz=quiz, nickname=nickname)
    active = request.session.get("quiz_attempts", {})
    active[str(quiz.id)] = str(attempt.access_token)
    request.session["quiz_attempts"] = active
    return redirect("quizzes:play", quiz_id=quiz.id)


def _active_attempt(request, quiz):
    token = request.session.get("quiz_attempts", {}).get(str(quiz.id))
    if not token:
        return None
    return Attempt.objects.filter(quiz=quiz, access_token=token, completed_at__isnull=True).first()


def _record_answer(attempt, question, choice=None):
    correct = bool(choice and choice.is_correct)
    points = question.points if correct else 0
    Answer.objects.create(
        attempt=attempt,
        question=question,
        choice=choice,
        is_correct=correct,
        points_earned=points,
    )
    attempt.score += points
    attempt.question_started_at = timezone.now()
    attempt.save(update_fields=["score", "question_started_at"])


def quiz_play(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, is_published=True)
    attempt = _active_attempt(request, quiz)
    if attempt is None:
        return redirect("quizzes:detail", quiz_id=quiz.id)
    questions = list(quiz.questions.prefetch_related("choices").all())
    index = attempt.answers.count()
    if index >= len(questions):
        attempt.completed_at = timezone.now()
        attempt.save(update_fields=["completed_at"])
        return redirect("quizzes:result", token=attempt.access_token)

    question = questions[index]
    elapsed = (timezone.now() - attempt.question_started_at).total_seconds()
    if request.method == "POST":
        if str(request.POST.get("question_id", "")) != str(question.id):
            return redirect("quizzes:play", quiz_id=quiz.id)
        choice = None
        if elapsed <= quiz.seconds_per_question and request.POST.get("choice"):
            choice = get_object_or_404(Choice, pk=request.POST["choice"], question=question)
        _record_answer(attempt, question, choice)
        if index + 1 == len(questions):
            attempt.completed_at = timezone.now()
            attempt.save(update_fields=["completed_at"])
            return redirect("quizzes:result", token=attempt.access_token)
        return redirect("quizzes:play", quiz_id=quiz.id)

    if elapsed >= quiz.seconds_per_question:
        _record_answer(attempt, question)
        return redirect("quizzes:play", quiz_id=quiz.id)

    return render(request, "quiz/play.html", {
        "quiz": quiz,
        "question": question,
        "index": index,
        "total": len(questions),
        "remaining": max(1, quiz.seconds_per_question - int(elapsed)),
        "progress": round((index + 1) * 100 / len(questions)),
    })


def quiz_result(request, token):
    attempt = get_object_or_404(Attempt.objects.select_related("quiz").prefetch_related("answers__question", "answers__choice"), access_token=token)
    active_token = request.session.get("quiz_attempts", {}).get(str(attempt.quiz_id))
    if str(attempt.access_token) != active_token:
        return redirect("quizzes:detail", quiz_id=attempt.quiz_id)
    total = attempt.quiz.questions.count()
    correct_count = attempt.answers.filter(is_correct=True).count()
    percent = round(correct_count * 100 / total) if total else 0
    max_score = sum(attempt.quiz.questions.values_list("points", flat=True))
    return render(request, "quiz/result.html", {
        "attempt": attempt,
        "total": total,
        "max_score": max_score,
        "correct_count": correct_count,
        "percent": percent,
    })


@login_required
@require_POST
def create_quiz(request):
    if not request.user.is_staff:
        return redirect("quizzes:list")
    title = request.POST.get("title", "").strip()[:140]
    description = request.POST.get("description", "").strip()[:500]
    try:
        topic_id = int(request.POST.get("topic_id", ""))
        seconds = int(request.POST.get("seconds_per_question", 20))
        items = json.loads(request.POST.get("questions_json", "[]"))
    except (ValueError, TypeError, json.JSONDecodeError):
        messages.error(request, "Dữ liệu quiz chưa hợp lệ.")
        return redirect("staff")
    cleaned = []
    topic = Topic.objects.filter(pk=topic_id).first()
    if not topic or not title or not isinstance(items, list) or not 1 <= len(items) <= 50 or not 5 <= seconds <= 180:
        messages.error(request, "Chọn chủ đề, nhập tên quiz, đặt thời gian và thêm từ 1 đến 50 câu.")
        return redirect("staff")
    for item in items:
        if not isinstance(item, dict):
            messages.error(request, "Có câu hỏi chưa hợp lệ.")
            return redirect("staff")
        prompt = str(item.get("text", "")).strip()[:300]
        choices = item.get("choices", [])
        try:
            correct = int(item.get("correct", -1))
            points = int(item.get("points", 100))
        except (TypeError, ValueError):
            correct = -1
            points = 100
        explanation = str(item.get("explanation", "")).strip()[:2000]
        if not prompt or not isinstance(choices, list) or len(choices) != 4 or correct not in range(4) or not 0 <= points <= 1000:
            messages.error(request, "Mỗi câu cần nội dung, 4 đáp án và một đáp án đúng.")
            return redirect("staff")
        cleaned_choices = [str(value).strip()[:180] for value in choices]
        if any(not value for value in cleaned_choices):
            messages.error(request, "Hãy điền đủ bốn lựa chọn cho mỗi câu.")
            return redirect("staff")
        cleaned.append((prompt, cleaned_choices, correct, points, explanation))

    with transaction.atomic():
        quiz = Quiz.objects.create(
            topic=topic,
            title=title,
            subject=topic.name,
            description=description,
            seconds_per_question=seconds,
            is_published=request.POST.get("is_published") == "on",
        )
        for order, (prompt, choices, correct, points, explanation) in enumerate(cleaned):
            question = Question.objects.create(quiz=quiz, text=prompt, explanation=explanation, points=points, order=order)
            Choice.objects.bulk_create([
                Choice(question=question, text=text, is_correct=(index == correct), order=index)
                for index, text in enumerate(choices)
            ])
    messages.success(request, f"Đã tạo quiz ‘{quiz.title}’ thành công.")
    return redirect("staff")


@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect("quizzes:list")
    quizzes = Quiz.objects.select_related("topic").annotate(question_total=Count("questions"))
    topics = Topic.objects.annotate(quiz_total=Count("quizzes", distinct=True), question_total=Count("quizzes__questions", distinct=True))
    return render(request, "quiz/staff.html", {"quizzes": quizzes, "topics": topics})


@login_required
@require_POST
def create_topic(request):
    if not request.user.is_staff:
        return redirect("quizzes:list")
    name = " ".join(request.POST.get("name", "").split())[:80]
    description = request.POST.get("description", "").strip()[:300]
    icon = request.POST.get("icon", "🌱").strip()[:8] or "🌱"
    color = request.POST.get("color", "tím").strip()[:20]
    if not name:
        messages.error(request, "Nhập tên chủ đề trước khi lưu.")
    elif Topic.objects.filter(name__iexact=name).exists():
        messages.error(request, "Chủ đề này đã có rồi.")
    else:
        Topic.objects.create(name=name, description=description, icon=icon, color=color)
        messages.success(request, f"Đã tạo chủ đề “{name}”. Bạn có thể thêm nhiều bộ quiz vào chủ đề này.")
    return redirect("staff")


@login_required
@require_POST
def delete_topic(request, topic_id):
    if not request.user.is_staff:
        return redirect("quizzes:list")
    topic = get_object_or_404(Topic, pk=topic_id)
    quiz_count = topic.quizzes.count()
    Quiz.objects.filter(topic=topic).update(topic=None, subject="Chưa phân loại")
    topic.delete()
    if quiz_count:
        messages.success(request, f"Đã xóa chủ đề. {quiz_count} bộ quiz vẫn được giữ lại trong mục Chưa phân loại.")
    else:
        messages.success(request, "Đã xóa chủ đề.")
    return redirect("staff")


@login_required
@require_POST
def delete_quiz(request, quiz_id):
    if not request.user.is_staff:
        return redirect("quizzes:list")
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    quiz.delete()
    messages.success(request, "Đã xóa quiz.")
    return redirect("staff")
