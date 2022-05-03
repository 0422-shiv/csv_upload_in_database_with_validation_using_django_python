
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework import generics, status, permissions
from utils.response_utils import UWAResponse
from rest_framework.response import Response
from uwa.settings import js
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from accounts.models import User
from .serializers import *


#=============================================================Login view================================================
class LoginAPIView(LoggingMixin,generics.GenericAPIView):
    serializer_class = AdminLoginSerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if User.objects.filter(is_staff=True).filter(email=serializer.data['email']).exists():
            msg = js['signed_in']
            header_data = serializer.data['tokens']
            return Response({'status':True ,'message': js['signed_in'],'access_token':header_data['access_token'],
                            'refresh_token':header_data['refresh_token'],
                            "user_id":(get_object_or_404(User,email=serializer.data['email'])).id}, status=status.HTTP_200_OK)

        else:
            raise AuthenticationFailed('Invalid credentials, try again')
#=============================================================log out view==============================================
class LogoutAPIView(LoggingMixin,generics.GenericAPIView):
    serializer_class = AdminLogoutSerializer
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        msg = 'You have successfully logged out'
        return UWAResponse(resp_data=[], status=status.HTTP_200_OK, is_success=msg)




class ProfileRetriveView(LoggingMixin, generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer

    permission_classes = (permissions.IsAdminUser,)

    def retrieve(self, request, *args, **kwargs):
        baseurl = request.build_absolute_uri()
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        data = self.update(request, *args, **kwargs)
        return UWAResponse(resp_data=[], status=status.HTTP_200_OK, is_success=js['User_Profile_Succesfully_Updated'])

    def patch(self, request, *args, **kwargs):
        data = self.partial_update(request, *args, **kwargs)
        return UWAResponse(resp_data=[], status=status.HTTP_200_OK, is_success=js['User_Profile_Succesfully_Updated'])


# ====================================================  An endpoint for changing password.==============================
class ChangePasswordView(LoggingMixin, generics.UpdateAPIView):
    serializer_class = AdminChangePasswordSerializer
    model = User
    permission_classes =  (permissions.IsAdminUser,)

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

        error = serializer.errors
        if 'confirm_password' in error:
            for data in error['confirm_password']:
                message = data
                fields = 'confirm_password'
        elif 'old_password' in error:
            for data in error['old_password']:
                message = data
                fields = 'old_password'
        else:
            for data in error['error']:
                message = data
                fields = 'new_password and confirm_password'
        return Response({'status': False, 'message': message, 'fields': fields}, status=status.HTTP_400_BAD_REQUEST)
