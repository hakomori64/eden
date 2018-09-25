from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Tag, Image
from .forms import AddTagForm, ImageForm
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
import shutil
import os.path
from django.conf import settings


def home(request):
    users = User.objects.all()

    return render(request, 'home.html', {'users': users})

def tags(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    tags = user.user_tags.all().order_by('-created_at')

    return render(request, 'tags.html', {'each': user, 'tags': tags})

@login_required
def add_tag(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    
    if request.method == 'POST':
        form = AddTagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.user = user
            tag.created_by = request.user
            tag.save()

            return redirect('tags', user_pk=user_pk)

    else:
        form = AddTagForm()

    return render(request, 'add_tag.html', {'each': user, 'form': form})  


class UploadFiles(FormView):
    form_class = ImageForm
    template_name = 'upload_images.html'
    success_url = '/profile/'

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('image')

        if form.is_valid():
            directory = settings.MEDIA_ROOT + '/origin/' + request.user.username
            if os.path.exists(directory):
                shutil.rmtree(directory)
                request.user.images.all().delete()

            for f in files:
                instance = Image(user=request.user, image=f)
                instance.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)