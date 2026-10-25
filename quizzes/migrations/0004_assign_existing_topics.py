from django.db import migrations


def assign_topics(apps, schema_editor):
    Topic = apps.get_model("quizzes", "Topic")
    Quiz = apps.get_model("quizzes", "Quiz")
    for quiz in Quiz.objects.filter(topic__isnull=True).iterator():
        topic_name = (quiz.subject or "").strip() or "Chủ đề chưa phân loại"
        topic, _ = Topic.objects.get_or_create(
            name=topic_name,
            defaults={
                "description": f"Các bộ quiz thuộc chủ đề {topic_name}.",
                "icon": "🌿",
                "color": "tím",
                "is_published": True,
            },
        )
        Quiz.objects.filter(pk=quiz.pk).update(topic_id=topic.pk)


class Migration(migrations.Migration):
    dependencies = [("quizzes", "0003_topic_alter_answer_options_alter_attempt_options_and_more")]
    operations = [migrations.RunPython(assign_topics, migrations.RunPython.noop)]
