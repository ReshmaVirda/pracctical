import email
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, firstname, lastname, email,  birthdate,  password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            firstname=firstname,
            lastname=lastname,
            birthdate=birthdate,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, firstname, lastname, email,  birthdate,  password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email=email,
            password=password,
            firstname=firstname,
            lastname=lastname,
            birthdate=birthdate,
            
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    firstname = models.CharField(max_length=250)
    lastname = models.CharField(max_length=250)
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    
    birthdate = models.CharField(default='', blank=True, null=True, max_length=100)
    

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname',  'birthdate']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class Blog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    blog = models.CharField(max_length=255)
    comment = models.CharField(max_length=255)

    def __str__(self):
        return self.user

    

   
    

