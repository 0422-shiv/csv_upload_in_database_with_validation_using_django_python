from rest_framework import generics, status, permissions,filters
from .serializer import *
from data_upload.models import CsvFileData, CoAuthors,DeploymentMetadata,DeviceMetaData,InputData
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.response import Response
from data_upload.serializer import UploadedCoAuthorSerializer
from utils.custom_generic import ListAPIView
from django.db.models import Q
from utils.custom_pagination import CustomPageNumberPagination
import csv
from django.http import HttpResponse
from utils.csv_file_fields_and_functions import deployment_data,device_data,input_data,set_row_data
from io import StringIO
from zipfile import ZipFile 
paginator = CustomPageNumberPagination()
# Create your views here.

class MyUploadView(LoggingMixin,ListAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	pagination_class = CustomPageNumberPagination
	serializer_class = MyUploadsSerializer
	filter_backends = [filters.SearchFilter,filters.OrderingFilter]
	search_fields = ['assign_name','upload_identifier','created_at']
	ordering_fields = ['assign_name','upload_identifier','created_at']
	def get_queryset(self):
		
		queryset= CsvFileData.objects.filter(Q(created_by=self.request.user.id) & Q(csv_type='Input Data') & Q(fileuploadstatus_id=8))
		return queryset
	


class MyUploadsDetailsView(LoggingMixin,generics.ListAPIView):
	permission_classes = (permissions.IsAuthenticated,)

	def get(self,request,upload_identifier):
		paginator.page_size = 3
		get_myuploads=MyUploadsDetailsSerializer(paginator.paginate_queryset(CsvFileData.objects.filter(created_by=request.user).filter(upload_identifier=upload_identifier).filter(fileuploadstatus_id=8),request), many=True).data
		co_authors=UploadedCoAuthorSerializer(CoAuthors.objects.filter(upload_identifier=upload_identifier),many=True).data
		co_authors_count=CoAuthors.objects.filter(upload_identifier=upload_identifier).count()
		
		total_species=DeploymentMetadata.objects.filter(upload_identifier=upload_identifier).values_list(
      		'scientific_name', flat=True).distinct().count() #total number of unique ‘scientificName’ 
		
		total_individual=DeploymentMetadata.objects.filter(upload_identifier=upload_identifier).values_list(
      		'organismid', flat=True).distinct().count() #total number of unique ‘organismID’
		total_tracks=InputData.objects.filter(upload_identifier=upload_identifier).values_list(
      		'deploymentID', flat=True).distinct().count() #total number of unique ‘DeploymentID’
		type_of_data=20
		return Response({'status':True,'myuploads_details':get_myuploads,
                   'co_authors':co_authors,
                   'co_authors_count':co_authors_count,
                  'total_species':total_species,
                 'total_individual':total_individual,
                 'total_tracks':total_tracks,
                 'type_of_data':type_of_data}, status=status.HTTP_200_OK)




class FileDetailedDataView(LoggingMixin,generics.ListAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	
	filter_backends = [filters.SearchFilter,filters.OrderingFilter]
	search_fields =  ['upload_identifier']
	ordering_fields = '__all__'
	
	def get_serializer_class(self):
		if self.kwargs['csv_type'] =='Deployment MetaData':
			return DeploymentMetaDataFileDetailedDataSerializer
		elif self.kwargs['csv_type'] =='Device MetaData':
			return DeviceMetaDataFileDetailedDataSerializer
		elif self.kwargs['csv_type'] =='Input Data':
			return InputDataFileDetailedDataSerializer

	
	def get_queryset(self):
		if self.kwargs['csv_type'] =='Deployment MetaData':
			if not DeploymentMetadata.objects.filter(upload_identifier=self.kwargs['upload_identifier']).exists():
				raise serializers.ValidationError({'upload_identifier': "upload_identifier "},code='upload_identifier')
			else:
				queryset=DeploymentMetadata.objects.filter(upload_identifier=self.kwargs['upload_identifier'])
		elif self.kwargs['csv_type'] =='Device MetaData':
			if not DeviceMetaData.objects.filter(upload_identifier=self.kwargs['upload_identifier']).exists():
				raise serializers.ValidationError({'upload_identifier': "upload_identifier "},code='upload_identifier')
			else:
				queryset=DeviceMetaData.objects.filter(upload_identifier=self.kwargs['upload_identifier'])
		elif self.kwargs['csv_type'] =='Input Data':
			if not InputData.objects.filter(upload_identifier=self.kwargs['upload_identifier']).exists():
				raise serializers.ValidationError({'upload_identifier': "upload_identifier "},code='upload_identifier')
			else:
				queryset=InputData.objects.filter(upload_identifier=self.kwargs['upload_identifier'])
		else:
			raise serializers.ValidationError({'wrong_csv_type': "wrong_csv_type "},code='wrong_csv_type')
		return queryset
	def get(self,request,upload_identifier,csv_type):
		limit = self.request.query_params.get('limit', 10)
		self.filter_backends = (filters.SearchFilter,filters.OrderingFilter)	
		self.ordering_fields =  '__all__'
		if csv_type =='Deployment MetaData':
				self.search_fields = self.search_fields =  ('accelerometry_calibrations_done', 'accelerometry_orientation_of_accelerometer_on_organism',
							'accelerometry_position_of_accelerometer_on_organism', 'accelerometry_qc_done', 
							'accelerometry_qc_notes', 'accelerometry_qc_problems_found', 'argos_filter_method', 
							'attachment_method', 'citation', 'common_name', 'deployment_datetime', 'deployment_end_type', 
							'deployment_id', 'deployment_latitude', 'deployment_longitude', 'detachment_datetime', 
							'detachment_details', 'detachment_latitude', 'detachment_longitude', 'duty_cycle', 
							'environmental_calibrations_done', 'environmental_qc_done', 'environmental_qc_notes',
							'environmental_qc_problems_found', 'id', 'instrumentID', 'instrument_settings', 'license',
							'organism_age_reproductive_class', 'organism_sex', 'organism_size', 'organism_size_measurement_description',
								'organism_size_measurement_time', 'organism_size_measurement_type', 'organism_weight_at_deployment',
								'organism_weight_remeasurement', 'organism_weight_remeasurement_time', 
								'organismid', 'other_datatypes_associated_with_deployment', 'other_relevent_identifier', 
								'owner_email_contact', 'owner_institutional_contact', 'owner_name', 'owner_phone_contact',
								'physiological_calibrations_done', 'physiological_qc_done', 'physiological_qc_notes',
								'physiological_qc_problems_found', 'ptt', 'references', 'scientific_name', 
								'scientific_name_source', 'sun_elevation_angle', 'track_end_latitude',
									'track_end_longitude', 'track_end_time', 'track_start_latitude', 
									'track_start_longitude', 'track_start_time', 'transmission_mode', 
									'transmission_settings', 'trapping_method_details', 'upload_identifier')
		elif csv_type=='Device MetaData':
				self.search_fields = ['accelerometry_lower_sensor_detection_limit', 'accelerometry_sensor_axes', 'accelerometry_sensor_calibration_date', 
								'accelerometry_sensor_calibration_details', 'accelerometry_sensor_duty_cycling', 'accelerometry_sensor_manufacturer',
								'accelerometry_sensor_model', 'accelerometry_sensor_precision', 'accelerometry_sensor_sampling_frequency',
								'accelerometry_sensor_units_reported', 'accelerometry_upper_sensor_detection_limit',
								'environmental_lower_sensor_detection_limit', 'environmental_sensor_calibration_date',
									'environmental_sensor_calibration_details', 'environmental_sensor_duty_cycling',
									'environmental_sensor_manufacturer', 'environmental_sensor_model', 
									'environmental_sensor_precision', 'environmental_sensor_sampling_frequency',
									'environmental_sensor_type', 'environmental_sensor_units_reported', 
									'environmental_upper_sensor_detection_limit', 'horizontal_sensor_tracking_device',
									'horizontal_sensor_uplink_Interval', 'horizontal_sensor_uplink_interval_units',
										'id', 'instrument_id', 'instrument_manufacturer', 'instrument_model_number', 'instrument_serial_number', 
										'instrument_type', 'physiological_lower_sensor_detection_limit', 'physiological_sensor_calibration_date',
										'physiological_sensor_calibration_details', 'physiological_sensor_duty_cycling',
									'physiological_sensor_manufacturer', 'physiological_sensor_model', 
									'physiological_sensor_precision', 'physiological_sensor_sampling_frequency',
									'physiological_sensor_type', 'physiological_sensor_units_reported',
										'physiological_upper_sensor_detection_limit', 'upload_identifier',
										'vertical_lower_sensor_detection_limit', 'vertical_sensor_calibration_date',
										'vertical_sensor_calibration_details', 'vertical_sensor_duty_cycling',
										'vertical_sensor_precision', 'vertical_sensor_resolution', 
										'vertical_sensor_sampling_frequency', 'vertical_sensor_units_reported', 
										'vertical_upper_sensor_detection_limit']
		elif csv_type=='Input Data':
				self.search_fields =  ['argosErrorRadius', 'argosGDOP', 'argosLC', 'argosOrientation',
                           					'argosSemiMajor', 'argosSemiMinor', 'deploymentID',
  										'depthGLS', 'gpsSatelliteCount', 'id', 'instrumentID', 'latitude',
            							'longitude', 'organismID', 'organismIDSource',
   										'residualsGPS', 'sensorIMeasurement', 'sensor_type',
             							'temperatureGLS', 'time', 'upload_identifier']
		else:
			raise serializers.ValidationError({'wrong_csv_type': "wrong_csv_type "},code='wrong_csv_type')
		queryset = paginator.paginate_queryset(self.filter_queryset(self.get_queryset()),request )
		serializer = self.get_serializer(queryset, many=True) 
		return Response({'status':True,
						'next_page_link': paginator.get_next_link(),
						'previous_page_link': paginator.get_previous_link(),
						'record_per_page': int(limit),
      					'current_page': paginator.page.number,
						'total_records':paginator.page.paginator.count,
      					'results':serializer.data}, status=status.HTTP_200_OK)
  




class AllThreeFileDownloadListAPIView(LoggingMixin,generics.ListAPIView):
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, upload_identifier, format=None):
        # if not CsvFileData.objects.filter(created_by=self.request.user).filter(upload_identifier=upload_identifier).exists():
        #     raise serializers.ValidationError({'upload_identifier': "upload_identifier "},code='upload_identifier')
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename='+upload_identifier+'.zip'
        z = ZipFile(response,'w')
        deployment_data_status=DeploymentMetadata.objects.filter(upload_identifier=upload_identifier).exists()
        device_data_status=DeviceMetaData.objects.filter(upload_identifier=upload_identifier).exists()
        input_data_status=InputData.objects.filter(upload_identifier=upload_identifier).exists()
        if not deployment_data_status or not device_data_status or not input_data_status:
            raise serializers.ValidationError({'upload_identifier': "upload_identifier "},code='upload_identifier')
        else:
            # deployment_csv_buffer=StringIO()
            # deployment_writer = csv.writer(deployment_csv_buffer)
            # deployment_writer.writerow(deployment_data)
            # for data in  DeploymentMetadata.objects.filter(upload_identifier=upload_identifier):
            #     deployment_writer.writerow(set_row_data(data,"Deployment MetaData"))
            # z.writestr("Deployment_MetaData_"+upload_identifier+".csv", deployment_csv_buffer.getvalue())
            # device_csv_buffer=StringIO()
            # device_writer = csv.writer(device_csv_buffer)
            # device_writer.writerow(device_data)
            # for data in  DeviceMetaData.objects.filter(upload_identifier=upload_identifier):
            #         device_writer.writerow(set_row_data(data,"Device MetaData"))
            # z.writestr("Device_MetaData_"+upload_identifier+".csv", device_csv_buffer.getvalue())
            input_csv_buffer=StringIO()
            input_writer = csv.writer(input_csv_buffer)
            input_writer.writerow(input_data)
            for data in  InputData.objects.filter(upload_identifier=upload_identifier):
                    input_writer.writerow(set_row_data(data,"Input Data"))
            print(input_csv_buffer.getvalue())
            z.writestr("InputData_"+upload_identifier+".csv", 'hi')
        print(z.infolist())
        print(z.debug)
        return response


 
class FileDownloadListAPIView(LoggingMixin,generics.ListAPIView):
	permission_classes = (permissions.IsAuthenticated,)
	def get(self, request, upload_identifier,csv_type, format=None):
		if not CsvFileData.objects.filter(created_by=self.request.user).filter(upload_identifier=upload_identifier).exists():
			raise serializers.ValidationError({'upload_identifier': "upload_identifier "},code='upload_identifier')
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


