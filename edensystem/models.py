from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from sorl.thumbnail import ImageField


GENDER_CHOICES = (
    ("male", 'male'),
    ("female", 'female'),
)

def get_filename(instance, filename):
    return '/'.join(['profile', instance.user.username, filename]) + '/'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sex = models.CharField("gender", max_length=6, choices=GENDER_CHOICES, default='male')
    thumbnail = ImageField(upload_to=get_filename)

    def image_url(self):
        if not (self.thumbnail and hashattr(self.thumbnail, 'url')):
            if self.sex == 'male':
                return '/static/img/if_male3_403019.svg'
            else:
                return '/static/img/if_female1_403023.svg'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Tag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tags')
    description = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tags')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
