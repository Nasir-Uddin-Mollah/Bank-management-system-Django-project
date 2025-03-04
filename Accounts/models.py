from django.db import models
from django.contrib.auth.models import User
from .constants import ACCOUNT_TYPE, GENDER_TYPE
# Create your models here.


class UserBankAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    account_number = models.IntegerField(unique=True)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_TYPE)
    initial_deposite_date= models.DateField(auto_now_add=True)
    balance = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.account_number)


class UserAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='address')
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    postal_code = models.IntegerField()
    country = models.CharField(max_length=50)

    def __str__(self):
        return self.user.email