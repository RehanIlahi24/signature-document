from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from .managers import UserManager

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    uid = models.CharField(_('User ID'), max_length=64, db_index=True, blank=False)
    email = models.EmailField(blank=True, null=True)
    username = models.CharField(_('Username'), max_length=250, unique=True)
    first_name = models.CharField(_('First Name'), max_length=250, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=250, blank=True)
    passport_image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    is_active = models.BooleanField(_('Active'), default=False)
    is_staff = models.BooleanField(_('Staff'), default=False)
    last_login = models.DateTimeField(auto_now=True)
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name','last_name' ]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        '''
        Displays email on admin panel
        '''
        return self.email
    
class DocumentFile(models.Model):
    file = models.FileField(upload_to='document_files/')
    
class Document(models.Model):
    DEVICE_CHOICES = (
        ('Pc' , 'Pc'),
        ('Mobile' , 'Mobile'),
        ('Tablet' , 'Tablet'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document_file = models.ForeignKey(DocumentFile, on_delete=models.CASCADE)
    is_signed = models.BooleanField(default=False)

    signature_image = models.ImageField(upload_to='signature_images/', null=True, blank=True)
    signature_code = models.CharField(max_length=255, null=True, blank=True)

    ip_address = models.CharField(max_length=255, null=True, blank=True)
    os = models.CharField(max_length=255, null=True, blank=True)
    os_version = models.CharField(max_length=255, null=True, blank=True)
    browser = models.CharField(max_length=255, null=True, blank=True)
    browser_version = models.CharField(max_length=255, null=True, blank=True)
    device = models.CharField(max_length=255, null=True, blank=True, choices=DEVICE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# class TestDoc(models.Model):
#     document_file = models.FileField(upload_to='document_files/')