from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class profile(models.Model):
	user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,)
	friends=models.ManyToManyField("profile",blank=True)
	#add more attributes here
	def __str__(self):
		return str(self.user.username)

#auto generate profile while creating account
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class friendRequest(models.Model):
	#send_to == follow; send_from == follower
	send_to=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='send_to')
	send_from=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='send_from')

	def __str__(self):
		return "From {} to {}".format(self.send_from.username,self.send_to.username)
