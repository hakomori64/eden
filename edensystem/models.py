from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField()

    def image_url(self):
        if self.image and hashattr(self.image, 'url'):
            return self.image.url
        else:
            return '/static/img/if_male3_403019.svg'

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