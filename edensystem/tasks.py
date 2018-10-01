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
from celery.task import task
from keras.utils.np_utils import to_categorical
import json
from keras.layers import Activation, Conv2D, Dense, Flatten, MaxPooling2D
from keras.models import Sequential, load_model


@shared_task
def add(x, y):
    return x + y

@shared_task
def learning(user_id):
    print("learning function is called")
    modify(user_id)
    scratch_image(user_id)
    X_train, y_train = face_answer_into_list()
    define_model(X_train, y_train)

    return


@shared_task
def modify(user_id):
    print("modify function is called")
    user = User.objects.get(pk=user_id)
    in_dir = settings.MEDIA_ROOT + '\\origin\\' + user.username + '\\*'
    out_dir = settings.MEDIA_ROOT + '\\face_image\\' + user.username
    in_jpg=glob.glob(in_dir)
    in_filename=os.listdir(settings.MEDIA_ROOT + '\\origin\\' + user.username)
    
    for num in range(len(in_jpg)):
        image = cv2.imread(str(in_jpg[num]))
        if image is None:
            print("Not open:", num)
            continue
        
        image_gs = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(settings.MEDIA_ROOT + '\\cascade\\haarcascade_frontalface_alt.xml')
        face_list = cascade.detectMultiScale(image_gs, scaleFactor=1.1, minNeighbors=2, minSize=(64,64))

        if len(face_list) > 0:
            for rect in face_list:
                image = image[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
                if image.shape[0] < 64:
                    continue
                image = cv2.resize(image, (64, 64))
                break

            if image.shape[0] < 64:
                print("too small")
                continue
        
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
    print("draw_images function is called")
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
    print("scratch_image function is called")
    user = User.objects.get(pk=user_id)
    output_dir = settings.MEDIA_ROOT + '\\extended\\' + user.username

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    os.makedirs(output_dir)

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


@shared_task
def face_answer_into_list():
    users = os.listdir(settings.MEDIA_ROOT + '\\extended')
    
    for i in range(len(users)):
        files = os.listdir(settings.MEDIA_ROOT + '\\extended\\' + users[i])
        if len(files) == 0:
            users.pop(i)
            continue

    # print(users)
    
    X_train = []
    y_train = []

    for user in users:
        image_list = glob.glob(settings.MEDIA_ROOT + '\\extended\\' + user + '\\*')
        for i in range(len(image_list)):
            img = cv2.imread(image_list[i])
            if isinstance(img, type(None)) == True:
                image_list.pop(i)
                continue


        for i in range(len(image_list)):
            img = cv2.imread(image_list[i])
            b, g, r = cv2.split(img)
            img = cv2.merge([r, g, b])
            X_train.append(img)
            y_train = np.append(y_train, users.index(user)).reshape(i + 1, 1)
        
    X_train = np.array(X_train)

    # print(X_train)
    # print(y_train)

    with open('users.json', 'w') as outfile:
        json.dump(users, outfile)

    return X_train, y_train


@shared_task
def define_model(X_train, y_train):

    print(X_train)
    print(y_train)
    print(len(X_train))
    print(len(y_train))

    model = Sequential()
    model.add(Conv2D(input_shape=(64, 64, 3), filters=32, kernel_size=(2, 2), strides=(1, 1), padding="same"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(filters=32, kernel_size=(2, 2), strides=(1, 1), padding="same"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(filters=32, kernel_size=(2, 2), strides=(1, 1), padding="same"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Flatten())
    model.add(Dense(256))
    model.add(Activation("sigmoid"))
    model.add(Dense(128))
    model.add(Activation('sigmoid'))
    model.add(Dense(len(users)))
    model.add(Activation('softmax'))


    model.compile(optimizer='sgd', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    model.fit(X_train, y_train, batch_size=32, epochs=50)

    model.save("my_model.h5")


@shared_task
def detect_face(image):
    print(image.shape)

    image_gs = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(settings.MEDIA_ROOT + '\\cascade\\haarcascade_frontalface_alt.xml')

    face_list = cascade.detectMultiScale(image_gs, scaleFactor=1.1, minNeighbors=2, minSize=(64,64))

    if len(face_list) > 0:
        for rect in face_list:
            x, y, width, height = rect
            cv2.rectangle(image, tuple(rect[0:2]), tuple(rect[0:2]+rect[2:4]), (255, 0, 0), thickness=3)
            img = image[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]

            if img.shape[0] < 64:
                print("too small")
                continue
            img = cv2.resize(img, (64, 64))
            img = np.expand_dims(img, axis=0)
            name = detect_who(img)
            cv2.putText(image, name, (x, y+height+20), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 2)

        if name == None:
            print("no face")
    
    else:
        print("no face")

    return image

@shared_task
def detect_who(img):
    name = ""
    model = load_model('my_model.h5')
    
    with open('users.json') as f:
        users = json.load(f)

    label = np.argmax(model.predict(img))

    return users[label]


