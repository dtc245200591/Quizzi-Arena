from django.db import migrations

QUESTIONS = [
    ("Rừng là nơi sinh sống của điều gì?", ["Chỉ có cây thông", "Nhiều loài động, thực vật", "Chỉ có côn trùng", "Không có sinh vật"], 1),
    ("Quá trình nào giúp cây xanh tạo ra thức ăn và giải phóng oxy?", ["Bay hơi", "Đóng băng", "Quang hợp", "Lên men"], 2),
    ("Loài động vật nào thường sống trên cây ở rừng nhiệt đới?", ["Đười ươi", "Cá heo", "Chim cánh cụt", "Cá mập"], 0),
    ("Lá cây rụng phân hủy giúp ích gì cho đất rừng?", ["Làm đất biến mất", "Tạo ra nhựa", "Làm cây ngừng lớn", "Bổ sung chất dinh dưỡng"], 3),
    ("Nhóm động vật nào thường giúp phát tán hạt khi ăn quả?", ["Cá mập", "Chim", "Bạch tuộc", "Sứa"], 1),
    ("Rừng ngập mặn giúp bảo vệ bờ biển bằng cách nào?", ["Làm nước biển biến mất", "Tạo ra núi lửa", "Giảm tác động của sóng và xói mòn", "Ngăn mọi cơn mưa"], 2),
    ("Rừng mưa nhiệt đới thường nổi tiếng vì điều gì?", ["Có nhiều loài sinh vật", "Luôn phủ đầy tuyết", "Không có cây cao", "Chỉ có một loài cây"], 0),
    ("Loài nào thường hoạt động về đêm?", ["Bướm ngày", "Gà trống", "Sóc bay ban ngày", "Cú mèo"], 3),
    ("Gấu trúc lớn chủ yếu ăn gì?", ["Quả mọng", "Tre", "Cá", "Côn trùng"], 1),
    ("Khi tham quan rừng, hành động nào có ích nhất?", ["Cho thú hoang ăn bánh", "Bẻ cành cây làm quà", "Không xả rác và không làm phiền động vật", "Mang động vật về nhà"], 2),
]


def add_starter_quiz(apps, schema_editor):
    Quiz = apps.get_model("quizzes", "Quiz")
    Question = apps.get_model("quizzes", "Question")
    Choice = apps.get_model("quizzes", "Choice")
    if Quiz.objects.filter(title="Khám phá rừng xanh và muôn loài").exists():
        return
    quiz = Quiz.objects.create(
        title="Khám phá rừng xanh và muôn loài",
        subject="Rừng & động vật",
        description="Mười câu hỏi vui khám phá hệ sinh thái rừng và cách bảo vệ muôn loài.",
        seconds_per_question=20,
        is_published=True,
    )
    for order, (prompt, choices, correct) in enumerate(QUESTIONS):
        question = Question.objects.create(quiz=quiz, text=prompt, order=order)
        Choice.objects.bulk_create([
            Choice(question=question, text=text, is_correct=(index == correct), order=index)
            for index, text in enumerate(choices)
        ])


class Migration(migrations.Migration):
    dependencies = [("quizzes", "0001_initial")]
    operations = [migrations.RunPython(add_starter_quiz, migrations.RunPython.noop)]
