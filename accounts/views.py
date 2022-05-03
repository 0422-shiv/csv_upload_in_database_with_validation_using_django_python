from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from django.conf import settings
from accounts.models import User, Institutions
from accounts.serializers import *
from django_countries import countries
from utils.response_utils import UWAResponse, UWAErrorResponse
from rest_framework.permissions import IsAuthenticated
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from utils.redirect_utils import CustomRedirect
import os
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from django.template.loader import render_to_string
import smtplib
import email.message
from uwa.settings import js
from rest_framework_tracking.mixins import LoggingMixin
from django.core.exceptions import ValidationError

# ==========================================================user registration view=============================================================================
class RegisterView(LoggingMixin,generics.GenericAPIView):
	serializer_class = RegisterSerializer
	def post(self, request):
		user = request.data   
		serializer = self.serializer_class(data=user)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		user_data = serializer.data
		user = User.objects.get(email=user_data['email'])
		token = RefreshToken.for_user(user).access_token
		redirect_url = user_data['redirect_url']
		try:
			url=redirect_url+"?token="+str(token)
			data_content = {"username": user.username,
								"url": url}
			email_content = render_to_string('email-template-uwa/verify-email-template.html', data_content)
	
			msg = email.message.Message()
			msg['Subject'] = 'Verify your email'

			msg['From'] = email.utils.formataddr((settings.SENDER_NAME, settings.DEFAULT_FROM_EMAIL))
			msg['To'] = user.email
			msg.add_header('Content-Type', 'text/html')
			msg.set_payload(email_content)
			s = smtplib.SMTP(settings.EMAIL_HOST + ':' + str(settings.EMAIL_PORT))
			s.ehlo()
			s.starttls()
			s.ehlo()
			s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
			s.sendmail(settings.DEFAULT_FROM_EMAIL, [msg['To']], msg.as_string())
			msg = js['user_registered']
		except:
			raise ValidationError('Passwords must match')
		return UWAResponse(status=status.HTTP_200_OK, is_success=msg,resp_data=None)





# ============================================================new user email verification view=====================================================
class VerifyEmail(LoggingMixin,generics.GenericAPIView):
	serializer_class = EmailVerificationSerializer

	token_param_config = openapi.Parameter(
		'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

	@swagger_auto_schema(manual_parameters=[token_param_config])

	def get(self, request):
		token = request.GET.get('token')
		try:
			payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
			user = User.objects.get(id=payload['user_id'])
			if not user.is_verified:
				user.is_verified = True
				user.save()
				msg = js['after_email_verification']
				
			else:
				msg = js['link_expired']
			return UWAResponse(resp_data=[],  is_success=msg)
		except jwt.ExpiredSignatureError as identifier:
			return UWAErrorResponse(error_message= js['link_expired'],resp_data=None)
		except jwt.exceptions.DecodeError as identifier:
			return UWAErrorResponse(error_message=js['Invalid_token'], resp_data=None)


#=============================================================Login view============================================================================
class LoginAPIView(LoggingMixin,generics.GenericAPIView):
	serializer_class = LoginSerializer

	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		msg = js['signed_in']
		header_data = serializer.data['tokens']

		
		return Response({'status':True ,'message': js['signed_in'],'access_token':header_data['access_token'],'refresh_token':header_data['refresh_token'],"user_id":(get_object_or_404(User,email=serializer.data['email'])).id},
								status=status.HTTP_200_OK)

#=============================================================log out view===========================================================
class LogoutAPIView(LoggingMixin,generics.GenericAPIView):
	serializer_class = LogoutSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		msg = 'You have successfully logged out'
		return UWAResponse(resp_data=[], status=status.HTTP_200_OK, is_success=msg)


	

#=============================================================common Api for  Institutions and Countries view===========================================================
class InstitutionsCountryListView(LoggingMixin,generics.GenericAPIView):

	def get(self, request):
			countries_list = countries.countries
			institution_list = Institutions.objects.all().values('institution_id', 'name')
			msg = 'Common API institution_list and countries_list get Successfully'
			return Response({"countries_list": countries_list,"institution_list": institution_list}, status=status.HTTP_200_OK,)


#==================================================================forgot password serializer========================================================
class RequestPasswordResetEmail(LoggingMixin,generics.GenericAPIView):
	serializer_class = ResetPasswordEmailRequestSerializer

	def post(self, request):
		serializer = self.serializer_class(data=request.data)

		user_email = request.data.get('email', '')

		if User.objects.filter(email=user_email).exists():
			user = User.objects.get(email=user_email)
			uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
			token = PasswordResetTokenGenerator().make_token(user)
			redirect_url = request.data.get('redirect_url', '')
		
			url=redirect_url+"?token="+token+"&uidb64="+uidb64
			data_content = {"username": user.username,
							"url": url}
			email_content = render_to_string('email-template-uwa/email-template.html', data_content)
			
			msg = email.message.Message()
			msg['Subject'] = 'Need a Password'

			msg['From'] = email.utils.formataddr((settings.SENDER_NAME, settings.DEFAULT_FROM_EMAIL))
			msg['To'] = user.email
			msg.add_header('Content-Type', 'text/html')
			msg.set_payload(email_content)
			s = smtplib.SMTP(settings.EMAIL_HOST + ':' + str(settings.EMAIL_PORT))
			s.ehlo()
			s.starttls()
			s.ehlo()
			s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
			s.sendmail(settings.DEFAULT_FROM_EMAIL, [msg['To']], msg.as_string())
			msg = js['request_password_link']
			return UWAResponse(resp_data=None, status=status.HTTP_200_OK, is_success=msg)

		return UWAErrorResponse(error_message=js['email_not_found'], status=status.HTTP_500_INTERNAL_SERVER_ERROR,
								resp_data='email')

class PasswordTokenCheckAPI(LoggingMixin,generics.GenericAPIView):
	serializer_class = SetNewPasswordSerializer

	def get(self, request, uidb64, token):
		redirect_url = request.GET.get('redirect_url')
		try:
			id = smart_str(urlsafe_base64_decode(uidb64))
			user = User.objects.get(id=id)
			if not PasswordResetTokenGenerator().check_token(user, token):
				if len(redirect_url) > 3:
					return CustomRedirect(redirect_url + '?token_valid=False')
				else:
					return CustomRedirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')
			if redirect_url and len(redirect_url) > 3:
				return CustomRedirect(redirect_url + '?token_valid=True&message=Credentials Valid&uidb64=' + uidb64 + '&token=' + token)
			else:
				return CustomRedirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

		except DjangoUnicodeDecodeError as identifier:
			try:
				if not PasswordResetTokenGenerator().check_token(user):
					return CustomRedirect(redirect_url + '?token_valid=False')
			except UnboundLocalError as e:
				return Response({'status':False ,'message': js['password_reset_Invalid_token']},
								status=status.HTTP_400_BAD_REQUEST)
			
class SetNewPasswordAPIView(LoggingMixin,generics.GenericAPIView):
	serializer_class = SetNewPasswordSerializer

	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		return UWAResponse(resp_data=[], status=status.HTTP_200_OK, is_success=js['password_reset_successfully'])





#==========================================================View for GET and Update user profile ==============================================================
class UserProfileRetrive(LoggingMixin,generics.RetrieveUpdateAPIView):
	queryset=User.objects.all()
	serializer_class=UserProfileSerializer
	
	permission_classes = (permissions.IsAuthenticated,)
  
	def retrieve(self, request, *args, **kwargs):
		baseurl = request.build_absolute_uri()
		instance = self.get_object()
		serializer = self.get_serializer(instance)
		return Response(serializer.data)
	def put(self, request, *args, **kwargs):
		data=self.update(request, *args, **kwargs)
		return UWAResponse(resp_data=[], status=status.HTTP_200_OK, is_success=js['User_Profile_Succesfully_Updated'])
	def patch(self, request, *args, **kwargs):
		data=self.partial_update(request, *args, **kwargs)
		return UWAResponse(resp_data=[], status=status.HTTP_200_OK, is_success=js['User_Profile_Succesfully_Updated'])



#====================================================  An endpoint for changing password.===================================================
class ChangePasswordView(LoggingMixin,generics.UpdateAPIView):
	serializer_class = ChangePasswordSerializer
	model = User
	permission_classes = (IsAuthenticated,)

	def get_object(self, queryset=None):
		obj = self.request.user
		return obj

	def update(self, request, *args, **kwargs):
		self.object = self.get_object()
		serializer = self.get_serializer(data=request.data)

		if serializer.is_valid():
			serializer.is_valid(raise_exception=True)
			serializer.save()
			msg = js['change_password_success']
			return UWAResponse(resp_data=[], status=status.HTTP_200_OK, is_success=msg)
	  
		error=serializer.errors
		if 'confirm_password' in error:
			for data in  error['confirm_password']:
				message=data
				fields='confirm_password'
		elif 'old_password' in error:
			for data in  error['old_password']:
				message=data
				fields='old_password'
		else:
			for data in error['error']:
				message = data
				fields = 'new_password and confirm_password'
		return Response({'status':False,'message':message,'fields':fields}, status=status.HTTP_400_BAD_REQUEST)

