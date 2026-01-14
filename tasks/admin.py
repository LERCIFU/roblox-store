from django.contrib import admin
from .models import Task, Sprint

@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active', 'is_completed')
    list_filter = ('is_active', 'is_completed')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'sprint', 'status', 'priority', 'story_points')
    list_filter = ('sprint', 'status', 'priority')
    search_fields = ('title',)