from django.shortcuts import render, redirect, get_object_or_404
from edensystem.forms import SignUpForm
from django.contrib.auth import login
from django.contrib.auth.models import User

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

def profile(request, profile_pk):
    profile = get_object_or_404(User, pk=profile_pk)

    return render(request, 'profile.html', {'profile': profile})