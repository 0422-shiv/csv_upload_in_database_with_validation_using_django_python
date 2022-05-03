from accounts.models import User
from rest_framework import generics, status, permissions
from rest_framework_tracking.mixins import LoggingMixin
from data_upload.models import CsvFileData,DeploymentMetadata
from rest_framework.response import Response
from data_upload.models import CsvFileData
import datetime
import calendar
from admin_user_lists.serializers import UserListsSerializer
from data_upload.serializer import DraftSerializer


class DashboardView(LoggingMixin, generics.ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    def get(self, request):      
        total_uploads_count=CsvFileData.objects.filter(fileuploadstatus_id=8).filter(csv_type='Input Data').count()      
        total_user_count=User.objects.filter(is_staff=False).count()
        today = datetime.date.today()
        new_users_this_month_count = User.objects.filter(is_staff=False, created_at__year=today.year, created_at__month=today.month).count()
        current_month = calendar.month_name[today.month]
        latest_registration = UserListsSerializer(User.objects.filter(is_staff=False).order_by('-id'), many=True).data
        latest_uploads = DraftSerializer(CsvFileData.objects.filter(fileuploadstatus_id=8).filter(csv_type='Input Data').order_by('-id'), many=True).data
        
        total_species=DeploymentMetadata.objects.values_list('scientific_name', flat=True).distinct().count() #total number of unique ‘scientificName’
        return Response({'status': True, 'total_uploads': total_uploads_count, 'total_no._of_users': total_user_count, 'total_species':total_species,
             'new_users_this_month': new_users_this_month_count, 'current_month': current_month, 
             'latest_registration': latest_registration[:7], 'latest_uploads': latest_uploads[:7]}, status=status.HTTP_200_OK)
