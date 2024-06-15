from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def sample_view(request):
    data = {
        "message": "Hello from Django!"
    }
    return JsonResponse(data)