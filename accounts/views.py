from django.shortcuts import render, redirect
from edensystem.forms import SignUpForm
from django.contrib.auth import login

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