from django.db import models
<<<<<<< HEAD
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
=======
from django.contrib.auth.models import AbstractBaseUser
import uuid
from django.contrib.auth.models import (
    BaseUserManager, AbstractUser 
)
from django.conf import settings

class AuthorManager(BaseUserManager):
    def create_user(self, email, displayName, password=None):
        """
        Creates and saves a User with the given email, displayname and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not displayName:
            raise ValueError('Users must have an display name')

        user=self.model(
            email=self.normalize_email(email),
            displayName=displayName,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, displayName, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user=self.create_user(
            email,
            password=password,
            displayName=displayName,
        )
        user.is_admin=True
        user.save(using=self._db)
        return user


class Author(AbstractBaseUser):
    email=models.EmailField(
        verbose_name='email address',
        max_length=60,
        unique=True,
    )
    uid_str = uuid.uuid4().urn
    uuid_str = str(settings.HOSTNAME)+"/author/"+uid_str[9:]
    id = models.CharField(primary_key=True, default=uuid_str, editable=False,max_length=100,unique=True)
    displayName = models.CharField(max_length=30)
    host = models.URLField(default=settings.HOSTNAME, max_length=100)
    url = models.URLField(default=uuid_str,max_length=100)
    
    github = models.URLField(default="", max_length=100)
    bio = models.CharField(max_length=200, null=True)
    
    date_joined=models.DateField(verbose_name="date joined", auto_now=True)
    last_login=models.DateField(verbose_name="date joined", auto_now=True)

    is_active=models.BooleanField(default=True)
    is_admin=models.BooleanField(default=False)

    objects=AuthorManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['displayName', ]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
>>>>>>> yipu
