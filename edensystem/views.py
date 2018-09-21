from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Tag


def home(request):
    users = User.objects.all()

    return render(request, 'home.html', {'users': users})

def tags(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    tags = user.user_tags.all().order_by('-created_at')

    return render(request, 'tags.html', {'user': user, 'tags': tags})