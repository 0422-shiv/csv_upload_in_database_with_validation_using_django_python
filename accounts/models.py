from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken
from django_countries.fields import CountryField
from utils.models import BaseModel

# from . views import get_ip_addr


class Institutions(models.Model):
    institution_id = models.AutoField(primary_key=True)  # Field name made lowercase.
    name = models.TextField(blank=True, null=True)
  

    class Meta:
        db_table = 'institutions'

    def __str__(self):
        return str(self.name)


class UserManager(BaseUserManager):

    def create_user(self, *args, **kwargs):
        username = kwargs.get('username', None)
        email = kwargs.get('email', None)
        password = kwargs.get('password', None)
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.country = kwargs.get('country', 'IN')
        user.city = kwargs.get('city', None)
        user.first_name = kwargs.get('first_name', None)
        user.last_name = kwargs.get('last_name', None)
        user.institution_id = kwargs.get('institution_id', None)
        user.is_terms_conditions = kwargs.get('is_terms_conditions', False)
        user.redirect_url = kwargs.get('redirect_url', False)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):
        if password is None:
            raise TypeError('Password should not be none')
        user = self.create_user(username=username, email=email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin,BaseModel):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=25,  unique=True,db_index=True, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    is_verified = models.BooleanField(default=False) # User email verified or not
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=35, default=None, null=True, blank=True)
    last_name = models.CharField(max_length=35, default=None, null=True, blank=True)
    city = models.CharField(max_length=35, default=None, null=True, blank=True)
    country = CountryField( default=None, null=True, blank=True)
    institution_id = models.ForeignKey(Institutions, on_delete=models.PROTECT, db_column='institution_id',null=True, blank=True)
    is_terms_conditions = models.BooleanField(default=False,null=False) # Accepted terms and conditions or not
    profile_image = models.ImageField(upload_to='Avatar', default=None,null=True, blank=True)
    sign_in_counts = models.SmallIntegerField(default=0) 
    redirect_url=models.CharField(max_length=255,null=True,blank=True)    
   
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }



