from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, Sprint
from .forms import TaskForm
from .forms import SprintForm
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# tasks/views.py

def task_board(request):
    # 1. ดึงรายชื่อ Sprint ทั้งหมดมาเพื่อเอาไปใส่ Dropdown (เรียงจากใหม่ไปเก่า)
    all_sprints = Sprint.objects.all().order_by('-id')
    
    # 2. เช็คว่า User เลือก Sprint มาไหม? (จาก URL ?sprint=...)
    sprint_id = request.GET.get('sprint')
    
    active_sprint = None
    
    if sprint_id:
        # ถ้าเลือกมา -> ดึง Sprint นั้นมาโชว์ (แม้ว่าจะไม่ Active ก็ตาม)
        active_sprint = get_object_or_404(Sprint, pk=sprint_id)
    else:
        # ถ้าไม่ได้เลือก -> ดึงตัวที่เป็น Active ปัจจุบันมาโชว์ (Default)
        active_sprint = Sprint.objects.filter(is_active=True).first()

    # 3. เตรียมข้อมูล Task (เหมือนเดิม แต่ใช้ active_sprint ที่เราเลือกข้างบน)
    tasks_todo = []
    tasks_in_progress = []
    tasks_done = []

    if active_sprint:
        tasks = active_sprint.tasks.all()
        tasks_todo = tasks.filter(status='TODO')
        tasks_in_progress = tasks.filter(status='IN_PROGRESS')
        tasks_done = tasks.filter(status='DONE')

    # 4. หางานดอง (Backlog)
    backlog_tasks = Task.objects.filter(sprint__isnull=True)

    context = {
        'active_sprint': active_sprint,
        'all_sprints': all_sprints,  # 👈 ส่งรายชื่อทั้งหมดไปให้ HTML
        'tasks_todo': tasks_todo,
        'tasks_in_progress': tasks_in_progress,
        'tasks_done': tasks_done,
        'backlog_tasks': backlog_tasks,
    }
    return render(request, 'tasks/list.html', context)
def update_task_status(request, task_id, new_status):
    # 1. หางานตาม ID
    task = get_object_or_404(Task, pk=task_id)
    
    # 2. เช็คว่า Status ที่ส่งมาถูกต้องไหม (ป้องกันคนมั่ว)
    valid_statuses = ['TODO', 'IN_PROGRESS', 'DONE']
    if new_status in valid_statuses:
        task.status = new_status
        task.save()
    
    # 3. เสร็จแล้วดีดกลับไปหน้าบอร์ด
    return redirect('tasks:board')

def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            
            # 🤖 Auto-assign: หาสปรินท์ที่ Active อยู่ แล้วยัดงานนี้ใส่เข้าไปเลย
            active_sprint = Sprint.objects.filter(is_active=True).first()
            if active_sprint:
                task.sprint = active_sprint
            
            task.save()
            return redirect('tasks:board') # บันทึกเสร็จ กลับไปหน้าบอร์ด
    else:
        form = TaskForm()

    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Add New Task'})

def add_sprint(request):
    if request.method == 'POST':
        form = SprintForm(request.POST)
        if form.is_valid():
            new_sprint = form.save(commit=False)
            
            # ✅ เช็คว่า User ติ๊กช่อง "Start Immediately" (is_active) หรือไม่?
            if new_sprint.is_active:
                # 1. หา Sprint เก่าที่กำลังรันอยู่ (ถ้ามี)
                old_sprint = Sprint.objects.filter(is_active=True).first()
                
                # 2. ปิด Sprint เก่าซะ
                if old_sprint:
                    old_sprint.is_active = False
                    old_sprint.save()
                
                # 3. บันทึก Sprint ใหม่ลงฐานข้อมูล (เพื่อให้มี ID ก่อน)
                new_sprint.save()
                
                # 4. 🔥 จุดสำคัญ: ย้ายงานค้าง! 🔥
                if old_sprint:
                    # เลือกงานที่ยัง "ไม่เสร็จ" (exclude DONE)
                    unfinished_tasks = old_sprint.tasks.exclude(status='DONE')
                    
                    # สั่งย้ายงานพวกนั้น มาใส่ Sprint ใหม่ทันที
                    unfinished_tasks.update(sprint=new_sprint, source=old_sprint.name)
                    
            else:
                # ถ้าไม่ได้ติ๊ก Active ก็บันทึกเฉยๆ (สร้างล่วงหน้า)
                new_sprint.save()
                
            return redirect('tasks:board')
    else:
        form = SprintForm()

    return render(request, 'tasks/sprint_form.html', {
        'form': form, 
        'title': '🚀 Start New Sprint',
        'button_text': 'Start Sprint'
    })

def edit_task(request, task_id):
    # 1. หางานที่จะแก้
    task = get_object_or_404(Task, pk=task_id)
    
    if request.method == 'POST':
        # 2. รับข้อมูลใหม่มาใส่ในงานเดิม (instance=task)
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks:board')
    else:
        # 3. ถ้าเพิ่งเปิดหน้า ให้เอาข้อมูลเก่ามาแสดงในฟอร์ม
        form = TaskForm(instance=task)

    # ใช้ template เดิม (task_form.html) ได้เลย ประหยัดเวลา!
    return render(request, 'tasks/task_form.html', {
        'form': form, 
        'title': '✏️ Edit Task', 
        'button_text': 'Save Changes'
    })

def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    task.delete()
    return redirect('tasks:board')


@csrf_exempt
def move_task_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            new_status = data.get('status')
            
           
            sprint_id = data.get('sprint_id')

            task = Task.objects.get(id=task_id)
            task.status = new_status


            if sprint_id:
                task.sprint_id = sprint_id 
            else:
                task.sprint = None  

            task.save()
            
            return JsonResponse({'success': True, 'message': 'Moved successfully!'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False}, status=400)