from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm, UploadThumbnailForm
from django.contrib.auth import login
from django.contrib.auth.models import User
import shutil
from django.conf import settings
import os.path

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.sex = form.cleaned_data['sex']
            login(request, user)
            return redirect('home')
    
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

def profile(request):
    return render(request, 'profile.html')

def upload(request):
    user = request.user

    if request.method == 'POST':
        form = UploadThumbnailForm(request.POST, request.FILES)

        if form.is_valid():
            path = settings.MEDIA_ROOT + '/profile/' + request.user.username
            if os.path.exists(path):
                shutil.rmtree(path)
            user.profile.thumbnail = form.cleaned_data['thumbnail']
            user.save()

            return redirect('profile')
    
    else:
        form = UploadThumbnailForm()

    return render(request, 'upload.html', {'form': form})