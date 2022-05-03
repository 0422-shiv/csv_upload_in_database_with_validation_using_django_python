from rest_framework import generics, status, permissions
from rest_framework_tracking.mixins import LoggingMixin
from .serializers import *
from rest_framework.response import Response
from data_upload.models import CsvFileData, CoAuthors,DeploymentMetadata,DeviceMetaData,InputData
from data_upload.serializer import UploadedCoAuthorSerializer
from admin_user_lists.serializers import *
from utils.custom_generic import ListAPIView
from rest_framework import filters
from utils.custom_pagination import CustomPageNumberPagination
import csv
from django.http import HttpResponse
from utils.csv_file_fields_and_functions import deployment_data,device_data,input_data,set_row_data
from io import StringIO
from zipfile import ZipFile 

class AllDataListView(LoggingMixin, ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = CustomPageNumberPagination
    queryset=CsvFileData.objects.filter(csv_type='Input Data').filter(fileuploadstatus_id=8)
    serializer_class = AllDataSerializer
    filter_backends = [filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['assign_name', 'upload_identifier', 'created_at','created_by__username']
    ordering_fields = ['assign_name', 'upload_identifier', 'created_at','created_by__username']

  

class UserDataDetailView(LoggingMixin, generics.ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    def get(self,request, upload_identifier):

        get_csv = UserUploadsDetailsSerializer(CsvFileData.objects.filter(upload_identifier=upload_identifier).filter(
                    fileuploadstatus_id=8), many=True).data

        co_author_count = CoAuthors.objects.filter(upload_identifier=upload_identifier).count()

        co_author_details = UploadedCoAuthorSerializer(CoAuthors.objects.filter(upload_identifier=upload_identifier), many=True).data
                	
     
        total_species=DeploymentMetadata.objects.filter(upload_identifier=upload_identifier).values_list(
            'scientific_name', flat=True).distinct().count() #total number of unique ‘scientificName’ 

        total_individual=DeploymentMetadata.objects.filter(upload_identifier=upload_identifier).values_list(
            'organismid', flat=True).distinct().count() #total number of unique ‘organismID’
        total_tracks=InputData.objects.filter(upload_identifier=upload_identifier).values_list(
            'deploymentID', flat=True).distinct().count() #total number of unique ‘DeploymentID’
        type_of_data=20#dummy data	
        return Response({'status': True, 'get_csv': get_csv,
                         'co_author_count': co_author_count,
                         'co_author_details': co_author_details,
                        'total_species':total_species,
                        'total_individual':total_individual,
                        'total_tracks':total_tracks,
                        'type_of_data':type_of_data}, status=status.HTTP_200_OK)
  
  

class AllThreeFileDownloadListAPIView(LoggingMixin,generics.ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    def get(self, request, upload_identifier, format=None):
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename='+upload_identifier+'.zip'
        z = ZipFile(response,'w')
        deployment_data_status=DeploymentMetadata.objects.filter(upload_identifier=upload_identifier).exists()
        device_data_status=DeviceMetaData.objects.filter(upload_identifier=upload_identifier).exists()
        input_data_status=InputData.objects.filter(upload_identifier=upload_identifier).exists()
        if not deployment_data_status or not device_data_status or not input_data_status:
            raise serializers.ValidationError({'upload_identifier': "upload_identifier "},code='upload_identifier')
        else:
            deployment_csv_buffer=StringIO()
            deployment_writer = csv.writer(deployment_csv_buffer)
            deployment_writer.writerow(deployment_data)
            for data in  DeploymentMetadata.objects.filter(upload_identifier=upload_identifier):
                deployment_writer.writerow(set_row_data(data,"Deployment MetaData"))
            z.writestr("Deployment_MetaData_"+upload_identifier+".csv", deployment_csv_buffer.getvalue())
            device_csv_buffer=StringIO()
            device_writer = csv.writer(device_csv_buffer)
            device_writer.writerow(device_data)
            for data in  DeviceMetaData.objects.filter(upload_identifier=upload_identifier):
                    device_writer.writerow(set_row_data(data,"Device MetaData"))
            z.writestr("Device_MetaData_"+upload_identifier+".csv", device_csv_buffer.getvalue())
            input_csv_buffer=StringIO()
            input_writer = csv.writer(input_csv_buffer)
            input_writer.writerow(input_data)
            for data in  InputData.objects.filter(upload_identifier=upload_identifier):
                    input_writer.writerow(set_row_data(data,"Input Data"))
            z.writestr("InputData_"+upload_identifier+".csv", input_csv_buffer.getvalue())
        return response


 
class FileDownloadListAPIView(LoggingMixin,generics.ListAPIView):
	permission_classes = (permissions.IsAdminUser,)
	def get(self, request, upload_identifier,csv_type, format=None):
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename='+csv_type+"_"+upload_identifier+".csv"
		writer = csv.writer(response)
		if csv_type == 'Deployment MetaData':
			if not DeploymentMetadata.objects.filter(upload_identifier=upload_identifier).exists():
				raise serializers.ValidationError({'upload_identifier': "upload_identifier "},code='upload_identifier')

			else:
				row = DeploymentMetadata.objects.filter(upload_identifier=upload_identifier)
				writer.writerow(deployment_data)

		elif csv_type == 'Device MetaData':
			
			if not DeviceMetaData.objects.filter(upload_identifier=upload_identifier).exists():
				raise serializers.ValidationError({'upload_identifier': "upload_identifier "},code='upload_identifier')

			else:
				row = DeviceMetaData.objects.filter(upload_identifier=upload_identifier)
				writer.writerow(device_data)

		elif csv_type == 'Input Data': 
			if not InputData.objects.filter(upload_identifier=upload_identifier).exists():
				raise serializers.ValidationError({'upload_identifier': "upload_identifier "},code='upload_identifier')

			else:
				row = InputData.objects.filter(upload_identifier=upload_identifier)
				writer.writerow(input_data)
		else:
			raise serializers.ValidationError({'csv_type': "csv_type"},code='csv_type')

		for data in  row:
			writer.writerow(set_row_data(data,csv_type))
		return response


