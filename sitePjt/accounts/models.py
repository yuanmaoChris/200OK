from django.db import models
import uuid
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,User
)
from django.conf import settings

class AuthorManager(BaseUserManager):
    
    def create_user(self, email, displayName, is_activated=True, is_active=True, is_admin=False, password=None):
        """
        Creates and saves a User with the given email, displayname and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not displayName:
            raise ValueError('Users must have a display name')
        if not password:
            raise ValueError('Users must have a password')

        user=self.model(
            email=self.normalize_email(email),
            displayName=displayName,
        )

        user.set_password(password)
        user.activated = is_activated
        user.active = is_active
        user.admin = is_admin
        user.save(using=self._db)
        return user

    def create_node(self, email, displayName, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            displayName=displayName,
        )
        user.admin = False
        user.activated = True
        user.node=True
        user.share=False
        user.share_image=False
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
        user.admin=True
        user.activated = True
        user.save(using=self._db)
        return user


class Author(AbstractBaseUser):
    email=models.EmailField(
        verbose_name='email address',
        max_length=60,
        unique=True,
    )
    id = models.CharField(primary_key=True, default=uuid.uuid4().urn[9:], editable=False,max_length=100,unique=True)
    displayName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30, blank=True)
    firstName = models.CharField(max_length=30, blank=True)
    host = models.CharField(default=settings.HOSTNAME, max_length=100)
    url = models.CharField(default="", max_length=100)
    avatar = models.ImageField(upload_to='avatar/', default = 'avatar/default-avatar.png', blank=True, null=True)
    github = models.URLField(default="", max_length=100, null=True)
    bio = models.CharField(default="This guy is too lazy to write a bio...", max_length=200, blank=True, null=True)
    date_joined=models.DateField(verbose_name="date joined", auto_now=True)
    last_login=models.DateField(verbose_name="last login", auto_now=True)

    active=models.BooleanField(default=True)
    activated=models.BooleanField(default=True)
    node=models.BooleanField(default=False)
    admin=models.BooleanField(default=False)
    share=models.BooleanField(default=False)
    share_image=models.BooleanField(default=False)

    objects = AuthorManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['displayName', ]

    def __str__(self):
        return self.displayName

    def get_url(self):
        return "{}author/{}".format(self.host, self.id)

    def has_perm(self, perm, obj=None):
        if perm in ['owner of post', 'owner of comment']:
            return obj and obj.author.id == self.id
        
        elif perm == 'owner of porfile':
            return obj and obj.id == self.id
        
        elif perm in ['share']:
            return self.share

        elif perm in ['share_image']:
            return self.share_image

        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_activated(self):
        return self.activated
    
    @property
    def is_node(self):
        return self.node
    
    @property
    def is_admin(self):
        return self.admin
    
    @property
    def is_staff(self):
        return self.admin

class ServerNode(models.Model):
    server_username = models.CharField(max_length=100)
    server_password = models.CharField(max_length=100)
    token = models.CharField(max_length=200,blank =True)
    host_url = models.CharField(max_length=200)