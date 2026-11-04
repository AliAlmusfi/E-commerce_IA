from django.db import models
from django.contrib.auth.models import BaseUserManager , AbstractBaseUser , PermissionsMixin , Group, Permission
from tools.models import TimeStampedModel
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self , username , email , password = None , **extra_fields):
        if not username:
            raise ValueError('user Must have username')
        if not email:
            raise ValueError('user must have an email')
        email = self.normalize_email(email)
        user = self.model(username = username , email = email , **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username , email , password , **extra_fields):
        extra_fields.setdefault('is_staff' , True)
        extra_fields.setdefault('is_superuser' , True)
        extra_fields.setdefault('is_active' , True)

        return self.create_user(username , email , password , **extra_fields)



class User(AbstractBaseUser , PermissionsMixin , TimeStampedModel):
    class Meta:
        db_table = 'user'
    username = models.CharField(max_length=100 , unique=True)
    email = models.EmailField(unique=True)
    objects = CustomUserManager()

    is_staff    = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',  # <-- Unique reverse accessor
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # <-- Unique reverse accessor
        related_query_name='user',
    )

    def save(self, *args, **kwargs):
        
        if self.pk is None or 'password' in kwargs.get('update_fields', []):
           
            if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
                self.set_password(self.password)
        super().save(*args, **kwargs)







# class Order (TimeStampedModel):
#     class Meta:
#         db_table = 'order'

#     price = models.DecimalField