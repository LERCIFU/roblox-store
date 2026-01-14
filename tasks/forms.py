from django import forms
from .models import Task, Sprint

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'story_points', 'sprint']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่องาน...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'รายละเอียด...'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'story_points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class SprintForm(forms.ModelForm):
    class Meta:
        model = Sprint
        # 👇 จุดสำคัญ: ต้องมี 'is_active' ในนี้ครับ (ลำดับมีผลต่อการเรียงหน้าเว็บ)
        fields = ['name', 'goal', 'start_date', 'end_date', 'is_active'] 
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เช่น Sprint #2: Bug Fixes'}),
            'goal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'เป้าหมายในรอบนี้...'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            # 👇 ตัว Checkbox
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'width: 20px; height: 20px;'}), 
        }
        
        labels = {
            'name': 'Sprint Name',
            'goal': 'Sprint Goal',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'is_active': 'Set as Current Sprint immediately? (เริ่มทันทีเลยไหม?)',
        }