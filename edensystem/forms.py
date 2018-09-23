from django import forms
from django.contrib.auth.models import User
from .models import Profile, Tag, Image

        
class AddTagForm(forms.ModelForm):
    
    class Meta:
        model = Tag
        fields = ('description',)


class ImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image')

    class Meta:
        model = Image
        fields = ('image',)