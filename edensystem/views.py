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
from background_task import background
from .tasks import learning


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
            origin_path = settings.MEDIA_ROOT + '\\origin\\' + request.user.username
            face_image_path = settings.MEDIA_ROOT + '\\face_image\\' + request.user.username
            test_image_path = settings.MEDIA_ROOT + '\\test_image\\' + request.user.username
            scratch_image_path = settings.MEDIA_ROOT + '\\extended\\' + request.user.username
            if len(request.user.images.all()) >= 10:
                if os.path.exists(origin_path):
                    shutil.rmtree(origin_path)
                if os.path.exists(face_image_path):
                    shutil.rmtree(face_image_path)
                if os.path.exists(test_image_path):
                    shutil.rmtree(test_image_path)
                if os.path.exists(scratch_image_path):
                    shutil.rmtree(scratch_image_path)
                                
                request.user.images.all().delete()
            
            if not os.path.exists(origin_path):
                os.makedirs(origin_path)
            if not os.path.exists(face_image_path):
                os.makedirs(face_image_path)
            if not os.path.exists(test_image_path):
                os.makedirs(test_image_path)
            if not os.path.exists(scratch_image_path):
                os.makedirs(scratch_image_path)

            for f in files:
                instance = Image(user=request.user, image=f)
                instance.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


def train(request):
    learning.delay(request.user.id)
    title = 'Now learning your face...'
    content = 'Your face can be recognized after a few minutes.'

    return render(request, 'train.html', {'title': title, 'content': content})

