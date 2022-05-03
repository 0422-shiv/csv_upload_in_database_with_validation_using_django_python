from rest_framework import generics, status, permissions
from rest_framework_tracking.mixins import LoggingMixin
from data_upload.models import CsvFileData
from rest_framework.response import Response
from my_uploads.serializer import MyUploadsSerializer
from data_upload.models import CsvFileData,DeploymentMetadata,InputData


class DashboardView(LoggingMixin, generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request): 
        query=CsvFileData.objects.filter(fileuploadstatus_id=8).filter(created_by=request.user).filter(csv_type='Input Data')     
        total_uploads_count=query.count()  
        upload_identifier_list=[] 
        for data in query:
              upload_identifier_list.append(data.upload_identifier)
     
        total_species=DeploymentMetadata.objects.filter(upload_identifier__in=upload_identifier_list).values_list(
            'scientific_name', flat=True).distinct().count() #total number of unique ‘scientificName’ 

        total_individual=DeploymentMetadata.objects.filter(upload_identifier__in=upload_identifier_list).values_list(
            'organismid', flat=True).distinct().count() #total number of unique ‘organismID’
        total_tracks=InputData.objects.filter(upload_identifier__in=upload_identifier_list).values_list(
            'deploymentID', flat=True).distinct().count() #total number of unique ‘DeploymentID’
        latest_uploads = MyUploadsSerializer(CsvFileData.objects.filter(fileuploadstatus_id=8).filter(created_by=request.user).filter(csv_type='Input Data').order_by('-id')[0:7], many=True).data
        
        return Response({'status': True, 'total_uploads': total_uploads_count,
                         'total_species':total_species,
                         'total_tracks':total_tracks,
                         'total_individual':total_individual,
                         'latest_uploads': latest_uploads[:7]},
                            status=status.HTTP_200_OK)
