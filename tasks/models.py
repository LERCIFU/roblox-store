from django.db import migrations, models
from django.contrib.auth.models import User
class Task(models.Model):
    title = models.CharField(max_length=200) # ชื่อหัวข้อ
    completed = models.BooleanField(default=False) # ทำเสร็จหรือยัง?

    PRIORITY_CHOICES = [
        ('HIGH', 'High Priority 🔥'),    # เก็บค่า HIGH, โชว์คำว่า High Priority 🔥
        ('MEDIUM', 'Medium Priority ⚠️'),
        ('LOW', 'Low Priority ☕'),
    ]
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM', # ถ้าไม่เลือก ให้ถือว่ากลางๆ ไว้ก่อน
    )

    created_at = models.DateTimeField(auto_now_add=True)

    assignee = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title