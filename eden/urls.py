"""eden URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from edensystem import views
from accounts import views as accounts_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('<int:user_pk>/', views.tags, name='tags'),
    path('<int:user_pk>/add/', views.add_tag, name='add_tag'),
    path('signup/', accounts_views.signup, name='signup'),
    path('signin/', auth_views.LoginView.as_view(template_name='signin.html'), name='signin'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', accounts_views.profile, name='profile'),
    path('profile/upload/', accounts_views.upload, name='upload_thumbnail'),
    path('profile/upimages/', views.UploadFiles.as_view(), name='upload_images'),
    path('train/', views.train, name='train'),
    path('upload/', views.upload_photo, name='upload'),
    path('result/', views.result, name='result'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)