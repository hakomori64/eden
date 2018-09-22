from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Tag
from .forms import AddTagForm


def home(request):
    users = User.objects.all()

    return render(request, 'home.html', {'users': users})

def tags(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    tags = user.user_tags.all().order_by('-created_at')

    return render(request, 'tags.html', {'each': user, 'tags': tags})


def add_tag(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    
    if request.method == 'POST':
        form = AddTagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.user = user
            tag.created_by = user
            tag.save()

            return redirect('tags', user_pk=user_pk)

    else:
        form = AddTagForm()

    return render(request, 'add_tag.html', {'each': user, 'form': form})  