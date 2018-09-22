from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


GENDER_CHOICES = (
    ("male", '男性'),
    ("female", '女性'),
)


class SignUpForm(UserCreationForm):
    sex = forms.ChoiceField(label="性別", widget=forms.Select, choices=GENDER_CHOICES,)

    class Meta:
        model = User
        fields = ('username', 'sex', 'password1', 'password2',)



class UploadThumbnailForm(forms.Form):
    thumbnail = forms.ImageField()