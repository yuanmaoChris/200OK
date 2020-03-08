from django.db import models
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
    uuid_str = uid_str[9:] # str(settings.HOSTNAME)+"/author/"+
    id = models.CharField(primary_key=True, default=uuid_str, editable=False,max_length=100,unique=True)
    displayName = models.CharField(max_length=30)
    host = models.URLField(default=settings.HOSTNAME, max_length=100)
    url = models.URLField(default=uuid_str,max_length=100)
    avatar = models.ImageField(upload_to='avatar/', default = 'avatar/default-avatar.png', blank=True, null=True)
    
    github = models.URLField(default="", max_length=100, null=True)
    bio = models.CharField(max_length=200, null=True)
    
    date_joined=models.DateField(verbose_name="date joined", auto_now=True)
    last_login=models.DateField(verbose_name="date joined", auto_now=True)
    is_active=models.BooleanField(default=True)
    is_admin=models.BooleanField(default=False)
    
    objects = AuthorManager()

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
    