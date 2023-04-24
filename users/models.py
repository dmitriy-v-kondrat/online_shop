from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class ProfileManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class Profile(AbstractBaseUser, PermissionsMixin):
    """ Temporarily not connected """
    username = None
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = PhoneNumberField()
    is_staff = models.BooleanField(default=False)

    objects = ProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = 'profiles'


class Buyer(models.Model):
    """ Model after succeeded pay. """
    email = models.EmailField()
    purchases = models.JSONField(default=dict)
    delivery_data = models.JSONField(default=dict, verbose_name='phone, name, address')

    def __str__(self):
        return self.email


class BuyerPaymentPending(models.Model):
    """ Model creating after a redirect on payment page. """
    payment_id = models.CharField(max_length=36, db_index=True)
    created_at = models.DateTimeField()
    payment_status = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = PhoneNumberField()
    orders_pending = models.JSONField(default=dict)
    postal_code = models.CharField(max_length=9)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=128)
    locality = models.TextField(help_text='town, street, house, etc')
    receive_newsletter = models.BooleanField(default=True, help_text='receive newsletter new product and discount')

    def __str__(self):
        return self.payment_id

