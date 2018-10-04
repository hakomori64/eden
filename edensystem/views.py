from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Tag, Image, ImageForDetecting
from .forms import AddTagForm, ImageForm, ImageForDetectingForm
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
import shutil
import os.path
from django.conf import settings
from background_task import background
from .tasks import learning, detect_face
import glob
import matplotlib.pyplot as plt
import cv2
import json


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


def upload_photo(request):
    save_directory1 = settings.MEDIA_ROOT + '\\detecting\\'
    save_directory2 = settings.MEDIA_ROOT + '\\detected\\'

    if request.method == 'POST':
        form = ImageForDetectingForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('image')

            for f in files:
                instance = ImageForDetecting(image=f)
                instance.save()
            
            files = glob.glob(save_directory1 + '*')
            
            if os.path.exists(save_directory2):
                shutil.rmtree(save_directory2)
            
            os.makedirs(save_directory2)
                
            for index, file in enumerate(files):
                image = cv2.imread(file)
                b, g, r = cv2.split(image)
                image = cv2.merge([r, g, b])
                whoImage, name = detect_face(image)

                r, g, b = cv2.split(whoImage)
                whoImage = cv2.merge([b, g, r])

                cv2.imwrite(save_directory2 + str(index) + name + '.png', whoImage)

            ImageForDetecting.objects.all().delete()
            shutil.rmtree(save_directory1)

            return redirect('result')
        
    else:
        form = ImageForDetectingForm()
        
    return render(request, 'upload_photo.html', {'form': form})
        

def result(request):
    save_directory2 = settings.MEDIA_ROOT + '\\detected\\'
    _files = glob.glob(save_directory2 + '*')
    file_list = os.listdir(save_directory2)
    names = []
    files = []

    for file in file_list:
        files.append('/media/detected/' + file)

    for file in file_list:
        name = file[1:-4]
        names.append(name)
    
    # for name in names:
    #     print(name)

    pk = []

    for name in names:
        print(name)
        user = User.objects.get(username=name)
        pk.append(user.pk)

    dictionary = dict(zip(files, pk))

    return render(request, 'result.html', {'dictionary': dictionary})

                
def result_demo():
    save_directory2 = settings.MEDIA_ROOT + '\\detected\\'
    files = glob.glob(save_directory2 + '*')
    # print('files: ', files)
    file_list = os.listdir(save_directory2)
    # print('file_list: ', file_list)
    names = []

    for file in file_list:
        name = file[1:-4]
        names.append(name)
    
    # for name in names:
    #     print('name: ', name)

    pk = []

    for name in names:
        user = User.object.get(username=name)
        pk.append(user.pk)

    return            
                 

