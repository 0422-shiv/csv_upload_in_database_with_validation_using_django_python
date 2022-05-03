from rest_framework import serializers, permissions
from rest_framework.exceptions import AuthenticationFailed
from django.contrib import auth
from accounts.models import User
from accounts.serializers import Base64ImageField
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from uwa.settings import js

#=============================================================Login serializer============================================================================
class AdminLoginSerializer(serializers.ModelSerializer):

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
class AdminLogoutSerializer(serializers.Serializer):
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






class ProfileSerializer(serializers.ModelSerializer):
    profile_image = Base64ImageField(
        max_length=None, use_url=True,required=False,
        allow_null=True,
        allow_empty_file=True
    )

    class Meta:
        model = User
        fields = ['profile_image', 'first_name', 'last_name', 'email', 'country', 'city']



#==============================================================Change Password Serializer===========================================================================
class AdminChangePasswordSerializer(serializers.Serializer):
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
