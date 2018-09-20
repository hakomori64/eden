from django.shortcuts import render, get_object_or_404
from .models import Profile


def home(request):
    users = Profile.objects.all()

    return render(request, 'home.html', {'users': users})