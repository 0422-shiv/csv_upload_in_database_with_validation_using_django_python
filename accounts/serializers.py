from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib import auth
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.exceptions import APIException
from django.shortcuts import get_object_or_404
from datetime import date
from django.core.files.base import ContentFile
import base64
from PIL import Image
from uwa.settings import js


# ===========================================================Serializer to convert img in bs64=========================================
class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            print(data,six.string_types)
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
                print(decoded_file)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension




# ==========================================================user registration serializer=============================================================================
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    is_terms_conditions = serializers.BooleanField(required=True)
    redirect_url = serializers.CharField(max_length=255, min_length=4,required=False)
    default_error_messages = {
        'username': 'The username should only contain alphanumeric characters'}

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'city', 'country', 'institution_id',
                  'is_terms_conditions',"redirect_url"]

    def validate(self, attrs):
        password = attrs.get('password', '')
        try:
             validate_password(password, User(**attrs))
        except ValidationError as e:
            raise serializers.ValidationError(e)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
  


# ============================================================new user email verification serializer=====================================================
class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']



#=============================================================Login serializer============================================================================
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3, read_only=True)

    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])
        return {
            'refresh_token': user.tokens()['refresh'],
            'access_token': user.tokens()['access']
        }

    class Meta:
        model = User
        fields = ['email', 'password', 'username', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')

        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }



#=============================================================log out serializer===========================================================
class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    default_error_messages = {'logout_bad_token': 'Token is expired or invalid'}

    def validate(self, attrs):
        self.token = attrs['refresh_token']
        # print(attrs)
        return attrs

    def save(self, **kwargs):
        # print(self.token)
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('logout_bad_token')





#==================================================================forgot password serializer========================================================
class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=3)

    redirect_url = serializers.CharField(max_length=500, min_length=4,required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    Confirm_Password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['Password','Confirm_Password', 'token', 'uidb64']
        
    def validate_password(self, value):
        data = self.get_initial()
        password = data.get('Confirm_Password')
        Confirm_Password = value
        if password != Confirm_Password:
            raise ValidationError('Passwords must match')
        return value

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed(401,'invalid_reset_link')
            
            user.set_password(password)
            user.save()
            return (user)
        except Exception as e:
            raise AuthenticationFailed(401,'invalid_reset_link')
        return super().validate(attrs)
    



#==========================================================Serializer for GET and Update user profile ==============================================================
class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = Base64ImageField(
        max_length=None, use_url=True,required=False,
        allow_null=True,
        allow_empty_file=True
    )

    class Meta:
        model = User
        fields = ['email', 'username','first_name', 'last_name', 'city', 'country', 'institution_id','profile_image']



#==============================================================Change Password Serializer===========================================================================
class ChangePasswordSerializer(serializers.Serializer):
    model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(js['wrong_old_password'])
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': js["password_confirm_password_matching"]})
        validate_password(data['new_password'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user
