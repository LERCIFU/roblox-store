from django.shortcuts import render, redirect
from .models import Task
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required(login_url='/accounts/login/')
def index(request):
    # 1. รับค่าที่ส่งมาจากปุ่ม (ถ้าไม่มีให้เป็นค่าว่าง)
    filter_type = request.GET.get('filter') 
    
    # 2. เริ่มต้นด้วยการดึง "งานทั้งหมด" มาก่อน
    tasks = Task.objects.all().order_by('-created_at')

    # 3. เข้าเครื่องกรอง ตามรหัสที่ส่งมา
    if filter_type == 'mine':
        # กรองเฉพาะงานของ "ฉัน" (คนที่ Login อยู่)
        tasks = tasks.filter(assignee=request.user)
        
    elif filter_type == 'high':
        # กรองเฉพาะงานด่วนไฟลุก 🔥
        tasks = tasks.filter(priority='HIGH')
        
    elif filter_type == 'completed':
        # กรองเฉพาะงานที่เสร็จแล้ว ✅
        tasks = tasks.filter(completed=True)
        
    else:
        # (Default) ถ้าเลือก All Tasks ให้โชว์เฉพาะงานที่ "ยังไม่เสร็จ" 
        # (เพื่อให้หน้าแรกสะอาดๆ ไม่งั้นงานรกเต็มไปหมด)
        tasks = tasks.filter(completed=False)

    # 4. จัดการเรื่องเพิ่มงานใหม่ (POST) เหมือนเดิม
    if request.method == 'POST':
        title = request.POST.get('title')
        priority = request.POST.get('priority')
        Task.objects.create(title=title, priority=priority, assignee=request.user)
        return redirect('task') # กลับไปหน้าหลัก

    return render(request, 'tasks/list.html', {'tasks': tasks})

def delete_task(request, pk):
    task = Task.objects.get(id=pk) # ไปหาของในโกดังที่รหัส (ID) ตรงกับที่เรากด
    task.delete() # สั่งทำลายทิ้งทันที!
    return redirect('task') # ลบเสร็จแล้วเด้งกลับหน้าแรก

def complete_task(request, pk):
    task = get_object_or_404(Task, id=pk)
    task.completed = not task.completed # สลับค่า True/False (เสร็จ/ไม่เสร็จ)
    task.save() # บันทึกลง Database
    return redirect('task')