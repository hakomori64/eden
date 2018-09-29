from __future__ import absolute_import, unicode_literals
import time
from django.contrib.auth.models import User
from django.conf import settings
import glob
import os
import cv2
import random
import shutil
from celery import shared_task
import numpy as np
import matplotlib.pyplot as plt
from keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array, array_to_img


@shared_task
def add(x, y):
    return x + y

@shared_task
def learning(user_id):
    print("learning function is called")
    modify(user_id)
    scratch_image(user_id)
    return


@shared_task
def modify(user_id):
    user = User.objects.get(pk=user_id)
    in_dir = settings.MEDIA_ROOT + '/origin/' + user.username + '/*'
    out_dir = settings.MEDIA_ROOT + '\\face_image\\' + user.username
    in_jpg=glob.glob(in_dir)
    in_filename=os.listdir(settings.MEDIA_ROOT + '/origin/' + user.username)
    
    for num in range(len(in_jpg)):
        image = cv2.imread(str(in_jpg[num]))
        if image is None:
            print("Not open:", num)
            continue
        
        image_gs = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(settings.MEDIA_ROOT + '/cascade/haarcascade_frontalface_alt.xml')
        face_list = cascade.detectMultiScale(image_gs, scaleFactor=1.1, minNeighbors=2, minSize=(64,64))

        if len(face_list) > 0:
            for rect in face_list:
                x, y, width, height = rect
                image = image[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
                if image.shape[0] < 64:
                    continue
                image = cv2.resize(image, (64, 64))
        
        else:
            print("no face")
            continue
        print(image.shape)

        filename=os.path.join(out_dir, str(in_filename[num]))
        cv2.imwrite(str(filename), image)
    
    in_dir = settings.MEDIA_ROOT + '\\face_image\\' + user.username + '\\*'
    in_jpg = glob.glob(in_dir)
    img_file_name_list = os.listdir(settings.MEDIA_ROOT + '\\face_image\\' + user.username)

    print("in_jpg ", len(in_jpg))
    print("img_file_name_list ", len(img_file_name_list))
    for i in img_file_name_list:
        print(i)

    random.shuffle(in_jpg)
    for i in range(len(in_jpg)//5):
        shutil.copyfile(str(in_jpg[i]), settings.MEDIA_ROOT + '\\test_image\\' + user.username + '\\' + img_file_name_list[i])


@shared_task
def draw_images(generator, x, dir_name, index):
    # 出力ファイルの設定
    save_name = 'extened-' + str(index)
    print('save_name: ', save_name)
    g = generator.flow(x, batch_size=1, save_to_dir=dir_name, save_prefix=save_name, save_format='jpg')

    # 1つの入力画像から何枚拡張するかを指定
    # g.next()の回数分拡張される
    for i in range(30):
        bach = g.next()


@shared_task
def scratch_image(user_id):
    user = User.objects.get(pk=user_id)
    output_dir = settings.MEDIA_ROOT + '\\extended\\' + user.username

    images = glob.glob(os.path.join(settings.MEDIA_ROOT, 'face_image', user.username, '*'))
    
    for i in images:
        print(i)

    generator = ImageDataGenerator(
        rotation_range=90,
        width_shift_range=0.1,
        height_shift_range=0.1,
        channel_shift_range=50.0,
        shear_range=0.39,
        horizontal_flip=True,
        vertical_flip=True
    )

    for i in range(len(images)):
        img = load_img(images[i])
        x = img_to_array(img)
        x = x.reshape((1,) + x.shape)

        draw_images(generator, x, output_dir, i)