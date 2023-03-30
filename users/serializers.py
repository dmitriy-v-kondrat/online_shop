from django.contrib.auth.password_validation import validate_password
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import Profile


class RegisterSerializer(serializers.ModelSerializer):
    """ Temporarily not connected """
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=Profile.objects.all())]
            )
    phone = PhoneNumberField(label='Телефон', help_text='Enter your phone number in the format +country code'
                                                        'operator code phone number (+12125552368)')
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
