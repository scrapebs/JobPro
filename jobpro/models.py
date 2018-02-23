from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)

class MyUserManager(BaseUserManager):
    def create_user(self, email, account_type, username, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            account_type=account_type,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, account_type, username, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
        	username=username,
            email=email,
            password=password,
            account_type=account_type,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractUser):
    EMPLOYEE = 'EM'
    ORGANISATION = 'OR'
    ACOUNTS_TYPE_CHOICES = (
        (EMPLOYEE, 'Соискатель'),
        (ORGANISATION, 'Организация')
    )
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=False,
    )
    account_type = models.CharField(max_length=2, choices=ACOUNTS_TYPE_CHOICES, default=EMPLOYEE)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()
    REQUIRED_FIELDS =['account_type', 'email']

    def __str__self(self):
    	return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True
        
"""
class Profile(models.Model):
    EMPLOYEE = 'EM'
    ORGANISATION = 'OR'
    ACOUNTS_TYPE_CHOICES = (
        (EMPLOYEE, 'Соискатель'),
        (ORGANISATION, 'Организация')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=2, choices=ACOUNTS_TYPE_CHOICES, default=EMPLOYEE)
    def __str__(self):
        return self.user.username + '-' + self.account_type

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

"""

class Vacancy(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    created_date = models.DateTimeField(blank = True, null = True)
    salary = models.IntegerField(default = 60000)
    actual = models.BooleanField(default = True)
    owner = models.ForeignKey(auth.get_user_model(), related_name='vacancies', on_delete=models.CASCADE, null=True)

    AVTO = 'AV'
    BANK = 'BA'
    SECURE = 'SE'
    SPORT = 'SP'
    IT = 'IT'
    SCIENCE = 'SC'
    TRADE = 'TR'
    LAWYERS = 'LA'
    PROFESSION_CHOICES = (
        (AVTO, 'Автомобильный бизнес'),
        (BANK, 'Банки, инвестиции'),
        (SECURE, 'Безопасность'),
        (SPORT, 'Спорт'),
        (IT, 'Информационные технологии, интернет, телеком'),
        (SCIENCE, 'Наука, образование'),
        (TRADE, 'Продажи'),
        (LAWYERS, 'Юристы')
    )
    profession = models.CharField(max_length=2,
                                      choices=PROFESSION_CHOICES,
                                      default=AVTO)

    def __str__(self):
    	return self.name


class Favourite(models.Model):
    user = models.ForeignKey(auth.get_user_model(), related_name = 'favourite', on_delete=models.CASCADE)
    vacancy = models.ForeignKey('jobpro.Vacancy', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + '->' + self.vacancy.name