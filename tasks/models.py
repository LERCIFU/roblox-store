from django.db import models
from django.utils import timezone

# 1. สร้างกล่อง Sprint (เช่น "Sprint #1: Setup System")
class Sprint(models.Model):
    name = models.CharField(max_length=200, verbose_name="Sprint Name")
    goal = models.TextField(blank=True, null=True, verbose_name="Sprint Goal")
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    is_active = models.BooleanField(default=False, verbose_name="Is Current Sprint?")
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# 2. อัปเกรด Task ให้รองรับระบบ Kanban
class Task(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),          # งานที่จะทำ
        ('IN_PROGRESS', 'Doing'),   # กำลังทำ
        ('DONE', 'Done'),           # เสร็จแล้ว
    ]
    
    PRIORITY_CHOICES = [
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 👇 พระเอกของเรา: ผูกงานกับ Sprint (ถ้าเป็น Null แปลว่าเป็น Backlog)
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M')
    
    # Story Points (ความยากง่ายของงาน 1, 2, 3, 5, 8) - เอาไว้ฝึกประเมินงาน
    story_points = models.IntegerField(default=1)

    source = models.CharField(max_length=200, blank=True, null=True, verbose_name="From Sprint")

    def __str__(self):
        return self.title