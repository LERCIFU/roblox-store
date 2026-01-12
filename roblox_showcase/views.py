from django.shortcuts import render

def index(request):
    return render(request, 'roblox_showcase/index.html')