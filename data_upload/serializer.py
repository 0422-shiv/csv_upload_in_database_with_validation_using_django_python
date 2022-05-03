from rest_framework import serializers,status
from django.shortcuts import render,get_object_or_404
from .models import *
from django.db import models
from accounts.models import Institutions
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import pandas as pd
from rest_framework_bulk import (
	BulkListSerializer,
	BulkSerializerMixin,
   
)
import csv
from uwa.settings import BASE_URL
from mimetypes import guess_extension, guess_type
import mimetypes
import sys
import csv
from django.db import IntegrityError
import uuid
from cerberus import Validator
from datetime import datetime
from decimal import Decimal
import cerberus
import codecs
from django.db import IntegrityError
import re
import requests
from contextlib import closing
import csv


class Base64FileField(serializers.FileField):
	def to_internal_value(self, data):
		from django.core.files.base import ContentFile
		import base64
		import six
		import uuid
		# Check if this is a base64 string
		if isinstance(data, six.string_types):
			# Check if the base64 string is in the "data:" format

			exten=((mimetypes.guess_type(data, strict=True))[0])
			print(exten)
			if 'data:' in data and ';base64,' in data:
				# Break out the header from the base64 content
				header, data = data.split(';base64,')
			

			# Try to decode the file. Return validation error if it fails.
			try:
				decoded_file = base64.b64decode(data)
			except TypeError:
				self.fail('invalid_file')
			file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
			# if (len(data) * 3) / 4 - data.count('=', -2) > 5000000:# 5000000 byte
			# 	raise serializers.ValidationError(code='more_than_five_mb')
			if (len(data) * 3) / 4 - data.count('=', -2) > 15000000:
				raise serializers.ValidationError(code='more_than_fifteen_mb')
			# elif not exten == '@file/vnd.ms-excel':
			# 	 raise serializers.ValidationError(code='not_csv_file')
			else:
				file_extension = 'csv'
				complete_file_name = "%s.%s" % (file_name, file_extension, )
				data = ContentFile(decoded_file, name=complete_file_name)
		return super(Base64FileField, self).to_internal_value(data)
	


class UploadedCoAuthorSerializer(serializers.ModelSerializer):
	class Meta:
		model = CoAuthors
		fields = ['author_name', 'author_email', 'institution_id','created_by']
		depth=1




class CoAuthorSerializer(serializers.ModelSerializer):
	class Meta:
		model = CoAuthors
		fields = ['author_name', 'author_email', 'institution_id','created_by']
		# depth=1


class FileUploadSerializer(serializers.ModelSerializer):

	upload_identifier = serializers.ReadOnlyField()
	csv_type=serializers.CharField(max_length=20,required=True,write_only=True)
	csv_file=Base64FileField(max_length=None, use_url=True,required=True)
	

	def validate(self,data):
		if data['csv_type'] == "Deployment MetaData" or data['csv_type'] == 'Device MetaData' or data['csv_type'] == 'Input Data':
			return data
		else:
			raise serializers.ValidationError({'wrong_csv_type': "wrong_csv_type "},code='wrong_csv_type')
	class Meta:
		model = CsvFileData
		fields = ['assign_name','csv_type','upload_identifier','csv_file','created_by','fileuploadstatus_id']

	
class bothserializer(serializers.Serializer):
	authors = CoAuthorSerializer(many = True, required = False)
	files= FileUploadSerializer(many = True, required = True)
	class Meta:
		fields = ['files','authors']

		
	def create(self, validated_data):
		u=uuid.uuid1().hex[:6].lower()
		authors_instance=None
		files_instance=None

		if validated_data.get("authors"):
			authors = [CoAuthors(**author,upload_identifier=u) for author in validated_data.get("authors")]
			authors_instance = CoAuthors.objects.bulk_create(authors)
		if validated_data.get("files"):
			files = [CsvFileData(**file,upload_identifier=u) for file in validated_data.get("files")]
			files_instance = CsvFileData.objects.bulk_create(files)

		else:
				raise serializers.ValidationError({'blank_files_array': "blank_files_array "},code='blank_files_array')
		
		organismid=''
		deployment_id=''
		instrumentment_id = ''
		for data in files_instance:

			url = data.csv_file.url
			with closing(requests.get(url, stream=True)) as r:
				f = (line.decode('utf-8') for line in r.iter_lines())
				csvreader = csv.reader(f, delimiter=',', quotechar='"')
				print(csvreader)
			# with open('media/'+str(data.csv_file), 'r', newline='', encoding='ISO-8859-1') as file:
			# 	csvreader = csv.reader(file)
				header = next(csvreader)
				if data.csv_type == 'Deployment MetaData':
						for row in csvreader:
							detail_data=dict(zip(header,row))
							for f in header:
								only_alpha = ""
								for char in  f.lower():
									if char.isalpha():
										only_alpha += char
							
								
								if only_alpha == 'instrumentid'  or only_alpha == "instrument" :
									instrumentment_id=str(detail_data[f])
								

								if only_alpha == 'deploymentid'  or only_alpha == "deployment" :
									
									deployment_id=str(detail_data[f])
								
								
								if only_alpha == 'organism'  or only_alpha == "organismid" :
									organismid=str(detail_data[f])
							
								        
							
				
			unique_id ='MM-'+instrumentment_id[:2]+'-' +deployment_id[:2]+'-'+organismid[:2]
			
			data.upload_identifier = unique_id
			data.save()
		if validated_data.get("authors"):
			for data in authors_instance:
				data.upload_identifier	= unique_id
				data.save()
			
		return {
			"authors":authors_instance,
			"files":files_instance
		}


class ColumnHeaderMatchingSerializer(serializers.Serializer):
	upload_identifier = serializers.CharField(required=True)
	csv_type = serializers.CharField(required=True)
	
	class Meta:
		fields = ['upload_identifier','csv_type']
	
	def validate(self, data):
		if not CsvFileData.objects.filter(upload_identifier=data['upload_identifier']).exists():
			 raise serializers.ValidationError({'upload_identifier': "upload_identifier "},code='upload_identifier')
		elif not CsvFileData.objects.filter(csv_type=data['csv_type']).exists():
			raise serializers.ValidationError({'csv_type': "csv_type"},code='csv_type')
		else:
			CsvFileData.objects.filter(upload_identifier=data['upload_identifier'])
		return data

class FileDataSerializer(serializers.ModelSerializer):
	class Meta:
		model = InputData
		fields ='__all__'

class ValidateMatchingSerializer(serializers.Serializer):
	MatchedColumns=serializers.JSONField(required=True)
	upload_identifier = serializers.CharField(required=True)
	csv_type = serializers.CharField(required=True)
	fileuploadstatus_id= serializers.IntegerField(source='CsvFileData.fileuploadstatus_id')
	class Meta:
		fields = ['MatchedColumns','upload_identifier','csv_type','fileuploadstatus_id']
	def validate(self,data):
		if not data['MatchedColumns']:
			 raise serializers.ValidationError({'MatchedColumns': "MatchedColumns "},code='MatchedColumns')
		else:
			MatchedColumns=data['MatchedColumns']
		if not CsvFileData.objects.filter(upload_identifier=data['upload_identifier']).exists():
			 raise serializers.ValidationError({'upload_identifier': "upload_identifier "},code='upload_identifier')
		elif not CsvFileData.objects.filter(csv_type=data['csv_type']).exists():
			raise serializers.ValidationError({'csv_type': "csv_type"},code='csv_type')
		return data 

	def create(self, data):
			file_headers=get_object_or_404(CsvFileHeaders,csv_file_type=data['csv_type'])
			fileheaders=eval(file_headers.csv_file_headers)
			get_file_instance=get_object_or_404(CsvFileData,upload_identifier=data['upload_identifier'],csv_type=data['csv_type'])
			MatchedColumns=data['MatchedColumns']
			row_count=0
			exists_obj_list=[]
			with open('media/'+str(get_file_instance.csv_file), 'r', newline='', encoding='ISO-8859-1') as file:
				csvreader = csv.reader(file)
			# import requests
			# from contextlib import closing
			# import csv

			# url = get_file_instance.csv_file.url
			# with closing(requests.get(url, stream=True)) as r:
			# 	f = (line.decode('utf-8') for line in r.iter_lines())
			# 	csvreader = csv.reader(f, delimiter=',', quotechar='"')
				header = next(csvreader)
				if data['csv_type'] == 'Deployment MetaData':
					if DeploymentMetadata.objects.filter(upload_identifier=data['upload_identifier']).exists():
						# for data in DeploymentMetadata.objects.filter(upload_identifier=data['upload_identifier']):
						# 	print(data.id)
						# 	exists_obj_list.append(get_object_or_404(DeploymentMetadata,id=data.id))
						# print(exists_obj_list)
						pass
					else:
						for row in csvreader:
									# # print(row)
									detail_data=dict(zip(header,row))
									# if len(exists_obj_list) > 0:
									# 	for idx,item in enumerate(exists_obj_list):
									# 		if idx == count:
									# 			print(item)
									# 			deployment_obj=item

									
									# else:
									deployment_obj =DeploymentMetadata(upload_identifier=data['upload_identifier'])
									CsvFileData.objects.filter(upload_identifier=data['upload_identifier']).update(fileuploadstatus_id=get_object_or_404(FileUploadStatus,id=3))
									for f in header:
										# print(MatchedColumns['deploymentID'])
										if f == MatchedColumns['deploymentID']:
											deployment_obj.deployment_id=detail_data[f]

										elif f == MatchedColumns['instrumentID']:
											deployment_obj.instrumentID=detail_data[f]

										elif f == MatchedColumns['ptt']:
											deployment_obj.ptt=detail_data[f]

										elif f == MatchedColumns['transmissionSettings']:
											deployment_obj.transmission_settings=detail_data[f]

										elif f == MatchedColumns['transmissionMode']:
											deployment_obj.transmission_mode=detail_data[f]

										elif f == MatchedColumns['dutyCycle']:
											deployment_obj.duty_cycle=detail_data[f]

										elif f == MatchedColumns['instrumentSettings']:
											deployment_obj.instrument_settings=detail_data[f]

										elif f == MatchedColumns['deploymentDateTime']:
											deployment_obj.deployment_datetime=datetime.strptime(detail_data[f], "%d-%m-%Y %H:%M")

										elif f == MatchedColumns['deploymentLatitude']:
											# print(detail_data[f],type(detail_data[f]))
											deployment_obj.deployment_latitude=detail_data[f]

										elif f == MatchedColumns['deploymentLongitude']:
											deployment_obj.deployment_longitude=detail_data[f]

										elif f == MatchedColumns['deploymentEndType']:
											deployment_obj.deployment_end_type=detail_data[f]

										elif f == MatchedColumns['detachmentDateTime']:
											deployment_obj.detachment_datetime=datetime.strptime(detail_data[f], "%d-%m-%Y %H:%M")

										elif f == MatchedColumns['detachmentDetails']:
											deployment_obj.detachment_details=detail_data[f]

										elif f == MatchedColumns['detachmentLatitude']:
											deployment_obj.detachment_latitude=detail_data[f]

										elif f == MatchedColumns['detachmentLongitude']:
											deployment_obj.detachment_longitude=detail_data[f]

										elif f == MatchedColumns['trackStartTime']:
											deployment_obj.track_start_time=datetime.strptime(detail_data[f], "%d-%m-%Y %H:%M")

										elif  f ==  MatchedColumns['trackStartLatitude']:
											deployment_obj.track_start_latitude=detail_data[f]

										elif f == MatchedColumns['trackStartLongitude']:
											deployment_obj.track_start_longitude=detail_data[f]        

										elif f == MatchedColumns['trackEndTime']:
											deployment_obj.track_end_time=datetime.strptime(detail_data[f], "%d-%m-%Y %H:%M")

										elif f == MatchedColumns['trackEndLatitude']:
											deployment_obj.track_end_latitude=detail_data[f]

										elif f == MatchedColumns['trackEndLongitude']:
											deployment_obj.track_end_longitude=detail_data[f]

										elif f == MatchedColumns['sunElevationAngle']:
											# print(detail_data[f],type(detail_data[f]))
											deployment_obj.sun_elevation_angle=detail_data[f]
										
										elif f == MatchedColumns['argosFilderMethod']:
											deployment_obj.argos_filter_method=detail_data[f]
										
										elif f == MatchedColumns['organismID']:
											deployment_obj.organismid=detail_data[f]
										
										elif f == MatchedColumns['scientificName']:
											deployment_obj.scientific_name=detail_data[f]
										
										elif f == MatchedColumns['scientificNameSource']:
											deployment_obj.scientific_name_source=detail_data[f]
										
										elif f == MatchedColumns['commonName']:
											deployment_obj.common_name=detail_data[f]
										
										elif f == MatchedColumns['organismSex']:
											deployment_obj.organism_sex=detail_data[f]
										
										elif f == MatchedColumns['organismWeightAtDeployment']:
											deployment_obj.organism_weight_at_deployment=detail_data[f]
										
										elif f == MatchedColumns['organismWeightRemeasurement']:
											deployment_obj.organism_weight_remeasurement=detail_data[f]
										
										elif f == MatchedColumns['organismWeightRemeasurementTime']:
											deployment_obj.organism_weight_remeasurement_time=datetime.strptime(detail_data[f], "%d-%m-%Y %H:%M")
										
										elif f == MatchedColumns['organismSize']:
											deployment_obj.organism_size=detail_data[f]
										
										elif f == MatchedColumns['organismSizeMeasurementType']:
											deployment_obj.organism_size_measurement_type=detail_data[f]
										
										elif f == MatchedColumns['organismSizeMeasurementDescription']:
											deployment_obj.organism_size_measurement_description=detail_data[f]
										
										elif  f ==  MatchedColumns['organismSizeMeasurementTime']:
											deployment_obj.organism_size_measurement_time=datetime.strptime(detail_data[f], "%d-%m-%Y %H:%M")
										
										elif f == MatchedColumns['organismAgeReproductiveClass']:
											deployment_obj.organism_age_reproductive_class=detail_data[f]        
										
										elif f == MatchedColumns['trappingMethodDetails']:
											deployment_obj.trapping_method_details=detail_data[f]
										
										elif f == MatchedColumns['attachmentMethod']:
											deployment_obj.attachment_method=detail_data[f]
										
										elif f == MatchedColumns['environmentalCalibrationsDone']:
											deployment_obj.environmental_calibrations_done=detail_data[f]
										
										elif f == MatchedColumns['environmentalQcDone']:
											# print((detail_data[f]).lower())
											if (detail_data[f]).lower() == 'yes':
												# print("in")
												deployment_obj.environmental_qc_done=True
											elif (detail_data[f]).lower() == 'no':
												deployment_obj.environmental_qc_done=False
											elif (detail_data[f]).lower() == 'y':
												deployment_obj.environmental_qc_done=True
											elif (detail_data[f]).lower() == 'n':
												deployment_obj.environmental_qc_done=False
											else:
												deployment_obj.environmental_qc_done=None
										
										elif f == MatchedColumns['environmentalQcProblemsFound']:
											# print((detail_data[f]).lower())
											if (detail_data[f]).lower() == 'yes':
											# 	# print("in")
												deployment_obj.environmental_qc_problems_found=True
											elif (detail_data[f]).lower() == 'no':
												deployment_obj.environmental_qc_problems_found=False
											elif (detail_data[f]).lower() == 'y':
												deployment_obj.environmental_qc_done=True
											elif (detail_data[f]).lower() == 'n':
												deployment_obj.environmental_qc_done=False
											else:
												deployment_obj.environmental_qc_problems_found=None
										
										elif f == MatchedColumns['environmentalQcNotes']:
											deployment_obj.environmental_qc_notes=detail_data[f]
										
										elif f == MatchedColumns['physiologicalCalibrationsDone']:
											deployment_obj.physiological_calibrations_done=detail_data[f]
										
										elif f == MatchedColumns['physiologicalQcDone']:
											# print(detail_data[f])
											if (detail_data[f]).lower() == 'yes':
												deployment_obj.physiological_qc_done=True
											elif (detail_data[f]).lower() == 'no': 
												deployment_obj.physiological_qc_done=False
											elif (detail_data[f]).lower() == 'y':
												deployment_obj.environmental_qc_done=True
											elif (detail_data[f]).lower() == 'n':
												deployment_obj.environmental_qc_done=False
											else:
												deployment_obj.physiological_qc_done=None
										
										elif f == MatchedColumns['physiologicalQcProblemsFound']:
											# print(detail_data[f])
											if (detail_data[f]).lower() == 'yes':
												deployment_obj.physiological_qc_problems_found=True
											elif (detail_data[f]).lower() == 'no': 
												deployment_obj.physiological_qc_problems_found=False
											elif (detail_data[f]).lower() == 'y':
												deployment_obj.environmental_qc_done=True
											elif (detail_data[f]).lower() == 'n':
												deployment_obj.environmental_qc_done=False
											else:
												deployment_obj.physiological_qc_problems_found=None
										
										elif f == MatchedColumns['physiologicalQcNotes']:
											deployment_obj.physiological_qc_notes=detail_data[f]
										
										elif f == MatchedColumns['accelerometryPositionOfAccelerometerOnOrganism']:
											deployment_obj.accelerometry_position_of_accelerometer_on_organism=detail_data[f]
										
										elif f == MatchedColumns['accelerometryOrientationOfAccelerometerOnOrganism']:
											deployment_obj.accelerometry_orientation_of_accelerometer_on_organism=detail_data[f]
										
										elif f == MatchedColumns['accelerometryCalibrationsDone']:
											deployment_obj.accelerometry_calibrations_done=detail_data[f]
										
										elif f == MatchedColumns['accelerometryQcDone']:
											# print(detail_data[f])
											if (detail_data[f]).lower() == 'yes':
												deployment_obj.accelerometry_qc_done=True
											elif (detail_data[f]).lower() == 'no':
												deployment_obj.accelerometry_qc_done=False
											elif (detail_data[f]).lower() == 'y':
												deployment_obj.environmental_qc_done=True
											elif (detail_data[f]).lower() == 'n':
												deployment_obj.environmental_qc_done=False
											else:
												deployment_obj.accelerometry_qc_done=None
										
										elif f == MatchedColumns['accelerometryQcProblemsFound']:
											# print(detail_data[f])
											if (detail_data[f]).lower() == 'yes':
												deployment_obj.accelerometry_qc_problems_found=True
											elif (detail_data[f]).lower() == 'no':
												deployment_obj.accelerometry_qc_problems_found=False
											elif (detail_data[f]).lower() == 'y':
												deployment_obj.environmental_qc_done=True
											elif (detail_data[f]).lower() == 'n':
												deployment_obj.environmental_qc_done=False
											else:
												deployment_obj.accelerometry_qc_problems_found=None
										
										elif f == MatchedColumns['accelerometryQcNotes']:
											deployment_obj.accelerometry_qc_notes=detail_data[f]
										
										elif  f ==  MatchedColumns['ownerName']:
											deployment_obj.owner_name=detail_data[f]
										
										elif f == MatchedColumns['ownerEmailContact']:
											deployment_obj.owner_email_contact=detail_data[f]
										
										elif f == MatchedColumns['ownerInstitutionalContact']:
											deployment_obj.owner_institutional_contact=detail_data[f]
										
										elif f == MatchedColumns['ownerPhoneContact']:
											deployment_obj.owner_phone_contact=detail_data[f]
										
										elif f == MatchedColumns['license']:
											deployment_obj.license=detail_data[f]
										
										elif f == MatchedColumns['otherRelevantIdentifiers']:
											deployment_obj.other_relevent_identifier=detail_data[f]
										
										elif f == MatchedColumns['otherDataTypesAssociatedWithDeployment']:
											deployment_obj.other_datatypes_associated_with_deployment=detail_data[f]
										
										elif f == MatchedColumns['references']:
											deployment_obj.references=detail_data[f]
										
										elif f == MatchedColumns['citation']:
											deployment_obj.citation=detail_data[f]
									try:
										deployment_obj.save()
									except IntegrityError as e :
										print(e)
										raise serializers.ValidationError({'column_mismatched': "column_mismatched"},code='column_mismatched') 
				elif data['csv_type'] == 'Device MetaData':
					if DeviceMetaData.objects.filter(upload_identifier=data['upload_identifier']).exists():
						pass
					else:
						for row in csvreader:
									detail_data=dict(zip(header,row))
									device_obj=DeviceMetaData(upload_identifier=data['upload_identifier'])
									CsvFileData.objects.filter(upload_identifier=data['upload_identifier']).update(fileuploadstatus_id=get_object_or_404(FileUploadStatus,id=5))
									for f in header:   
										# print(f)       
										if f == MatchedColumns['instrumentID']:
											# print(detail_data[f])
											device_obj.instrument_id=detail_data[f]
										
										elif f == MatchedColumns['instrumentType']:
											device_obj.instrument_type=detail_data[f]
										
										elif f == MatchedColumns['instrumentModel']:
											# print(detail_data[f])
											device_obj.instrument_model_number=detail_data[f]
										
										elif f == MatchedColumns['instrumentManufacturer']:
											device_obj.instrument_manufacturer=detail_data[f]
										
										elif f == MatchedColumns['instrumentSerialNumber']:
											device_obj.instrument_serial_number=detail_data[f]
										
										elif f == MatchedColumns['trackingDevice']:
											device_obj.horizontal_sensor_tracking_device=detail_data[f]
										
										elif f == MatchedColumns['horizontalSensorUplinkInterval']:
											device_obj.horizontal_sensor_uplink_Interval=detail_data[f]
										
										elif f == MatchedColumns['horizontalSensorUplinkIntervalUnits']:
											device_obj.horizontal_sensor_uplink_interval_units=detail_data[f]
										
										elif f == MatchedColumns['verticalSensorUnitsReported']:
											device_obj.vertical_sensor_units_reported=detail_data[f]
										
										elif f == MatchedColumns['resolution']:
											device_obj.vertical_sensor_resolution=detail_data[f]
										
										elif f == MatchedColumns['verticalLowerSensorDetectionLimit']:
											device_obj.vertical_lower_sensor_detection_limit=detail_data[f]
										
										elif f == MatchedColumns['verticalUpperSensorDetectionLimit']:
											device_obj.vertical_upper_sensor_detection_limit=detail_data[f]
										
										elif f == MatchedColumns['verticalSensorPrecision']:
											device_obj.vertical_sensor_precision=detail_data[f]
										
										elif f == MatchedColumns['verticalSensorSamplingFrequency']:
											device_obj.vertical_sensor_sampling_frequency=detail_data[f]
										
										elif f == MatchedColumns['verticalSensorDutyCycling']:
											device_obj.vertical_sensor_duty_cycling=detail_data[f]
										
										elif f == MatchedColumns['verticalSensorCalibrationDate']:
											device_obj.vertical_sensor_calibration_date=datetime.strptime(detail_data[f], "%d-%m-%Y %H:%M")
										
										elif  f ==  MatchedColumns['verticalSensorCalibrationDetails']:
											device_obj.vertical_sensor_calibration_details=detail_data[f]
										
										elif f == MatchedColumns['environmentalSensorType']:
											device_obj.environmental_sensor_type=   detail_data[f]      
										
										elif f == MatchedColumns['environmentalSensorManufacturer']:
											device_obj.environmental_sensor_manufacturer=detail_data[f]
										
										elif f == MatchedColumns['environmentalSensorModel']:
											device_obj.environmental_sensor_model=detail_data[f]
										
										elif f == MatchedColumns['environmentalSensorUnitsReported']:
											device_obj.environmental_sensor_units_reported=detail_data[f]
										
										elif f == MatchedColumns['environmentalLowerSensorDetectionLimit']:
											device_obj.environmental_lower_sensor_detection_limit=detail_data[f]
										
										elif f == MatchedColumns['environmentalUpperSensorDetectionLimit']:
											device_obj.environmental_upper_sensor_detection_limit=detail_data[f]
										
										elif f == MatchedColumns['environmentalSensorPrecision']:
											device_obj.environmental_sensor_precision=detail_data[f]
										
										elif f == MatchedColumns['environmentalSensorSamplingFrequency']:
											device_obj.environmental_sensor_sampling_frequency=detail_data[f]
										
										elif f == MatchedColumns['environmentalSensorDutyCycling']:
											device_obj.environmental_sensor_duty_cycling=detail_data[f]
										
										elif f == MatchedColumns['environmentalSensorCalibrationDate']:
											device_obj.environmental_sensor_calibration_date=datetime.strptime(detail_data[f], "%d-%m-%Y %H:%M")
										
										elif f == MatchedColumns['environmentalSensorCalibrationDetails']:
											device_obj.environmental_sensor_calibration_details=detail_data[f]
										
										elif f == MatchedColumns['physiologicalSensorType']:
											device_obj.physiological_sensor_type=detail_data[f]
										
										elif f == MatchedColumns['physiologicalSensorManufacturer']:
											device_obj.physiological_sensor_manufacturer=detail_data[f]
										
										elif f == MatchedColumns['physiologicalSensorModel']:
											device_obj.physiological_sensor_model=detail_data[f]
										
										elif f == MatchedColumns['physiologicalSensorUnitsReported']:
											device_obj.physiological_sensor_units_reported=detail_data[f]
										
										elif f == MatchedColumns['physiologicalLowerSensorDetectionLimit']:
											device_obj.physiological_lower_sensor_detection_limit=detail_data[f]
										
										elif f == MatchedColumns['physiologicalUpperSensorDetectionLimit']:
											device_obj.physiological_upper_sensor_detection_limit=detail_data[f]
										
										elif  f ==  MatchedColumns['physiologicalSensorPrecision']:
											device_obj.physiological_sensor_precision=detail_data[f]
										
										elif f == MatchedColumns['physiologicalSensorSamplingFrequency']:
											device_obj.physiological_sensor_sampling_frequency=   detail_data[f]     
										
										elif f == MatchedColumns['physiologicalSensorDutyCycling']:
											device_obj.physiological_sensor_duty_cycling=detail_data[f]
										
										elif f == MatchedColumns['physiologicalSensorCalibrationDate']:
											device_obj.physiological_sensor_calibration_date=datetime.strptime(detail_data[f], "%d-%m-%Y %H:%M")
										
										elif f == MatchedColumns['physiologicalSensorCalibrationDetails']:
											device_obj.physiological_sensor_calibration_details=detail_data[f]
										
										elif f == MatchedColumns['accelerometrySensorManufacturer']:
											device_obj.accelerometry_sensor_manufacturer=detail_data[f]
										
										elif f == MatchedColumns['accelerometrySensorModel']:
											device_obj.accelerometry_sensor_model=detail_data[f]
										
										elif f == MatchedColumns['axes']:
											device_obj.accelerometry_sensor_axes=detail_data[f]
										
										elif f == MatchedColumns['accelerometrySensorUnitsReported']:
											device_obj.accelerometry_sensor_units_reported=detail_data[f]
										
										elif f == MatchedColumns['accelerometryLowerSensorDetectionLimit']:
											device_obj.accelerometry_lower_sensor_detection_limit=detail_data[f]
										
										elif f == MatchedColumns['accelerometryUpperSensorDetectionLimit']:
											device_obj.accelerometry_upper_sensor_detection_limit=detail_data[f]
										
										elif f == MatchedColumns['accelerometrySensorPrecision']:
											device_obj.accelerometry_sensor_precision=detail_data[f]
										
										elif f == MatchedColumns['accelerometrySensorSamplingFrequency']:
											device_obj.accelerometry_sensor_sampling_frequency=detail_data[f]
										
										elif f == MatchedColumns['accelerometrySensorDutyCycling']:
											device_obj.accelerometry_sensor_duty_cycling=detail_data[f]
										
										elif f == MatchedColumns['accelerometrySensorCalibrationDate']:
											device_obj.accelerometry_sensor_calibration_date=datetime.strptime(detail_data[f], "%d-%m-%Y %H:%M")
										
										elif  f ==  MatchedColumns['accelerometrySensorCalibrationDetails']:
											device_obj.accelerometry_sensor_calibration_details=detail_data[f]
									try:
										device_obj.save()
									except:
										raise serializers.ValidationError({'column_mismatched': "column_mismatched"},code='column_mismatched')
				elif data['csv_type'] == 'Input Data':
					if InputData.objects.filter(upload_identifier=data['upload_identifier']).exists():
						pass
					else:
						for row in csvreader:
									detail_data=dict(zip(header,row))
									input_obj=InputData(upload_identifier=data['upload_identifier'])
									CsvFileData.objects.filter(upload_identifier=data['upload_identifier']).update(fileuploadstatus_id=get_object_or_404(FileUploadStatus,id=7))
									for f in header:
										# print(f)
										if f == MatchedColumns['instrumentID']:
											input_obj.instrumentID=detail_data[f]
										
										elif f == MatchedColumns['deploymentID']:
											input_obj.deploymentID=detail_data[f]
										
										elif f == MatchedColumns['organismID']:
											input_obj.organismID=detail_data[f]
										
										elif f == MatchedColumns['organismIDSource']:
											input_obj.organismIDSource=detail_data[f]
										
										elif f == MatchedColumns['time']:
											input_obj.time=datetime.strptime(detail_data[f], "%d-%m-%Y %H:%M")# HH:MM[:ss[.uuuuuu]][TZ]
										
										elif f == MatchedColumns['latitude']:
											input_obj.latitude=detail_data[f]
										
										elif f == MatchedColumns['longitude']:
											input_obj.longitude=detail_data[f]
										
										elif f == MatchedColumns['argosLC']:
											if detail_data[f] == '-1':
												input_obj.argosLC='A'
											if detail_data[f] == '-2':
												input_obj.argosLC='B'
											if detail_data[f] == '-9999/-9/-99/-999':
												input_obj.argosLC='z'
											else:
												input_obj.argosLC=detail_data[f]
										
										elif f == MatchedColumns['argosErrorRadius']:
											input_obj.argosErrorRadius=detail_data[f]	
										
										elif f == MatchedColumns['argosSemiMajor']:
											input_obj.argosSemiMajor=detail_data[f]
										
										elif f == MatchedColumns['argosSemiMinor']:
											input_obj.argosSemiMinor=detail_data[f]
										
										elif f == MatchedColumns['argosOrientation']:
											input_obj.argosOrientation=detail_data[f]
										
										elif f == MatchedColumns['argosGDOP']:
											input_obj.argosGDOP=detail_data[f]
										
										elif f == MatchedColumns['gpsSatelliteCount']:
											input_obj.gpsSatelliteCount=detail_data[f]
										
										elif f == MatchedColumns['residualsGPS(rapid acquisition GPS)']:
											input_obj.residualsGPS=detail_data[f]
										
										elif f == MatchedColumns['temperatureGLS']:
											input_obj.temperatureGLS=detail_data[f]
										
										elif f == MatchedColumns['depthGLS']:
											input_obj.depthGLS=detail_data[f]
										
										elif  f ==  MatchedColumns['sensorIType']:
											input_obj.sensor_type=detail_data[f]
										
										elif f == MatchedColumns['sensorIMeasurement']: 
											input_obj.sensorIMeasurement=detail_data[f]
									try:
										input_obj.save()
									except:
										raise serializers.ValidationError({'column_mismatched': "column_mismatched"},code='column_mismatched')

			return data	

			
			
		
class ReUploadSerializer(serializers.ModelSerializer):
	
	upload_identifier = serializers.CharField(max_length=6,required=True,write_only=True)
	csv_type=serializers.CharField(max_length=20,required=True,write_only=True)
	csv_file=Base64FileField(max_length=None, use_url=True,required=True)
	
	def validate(self,data):
		if data['csv_type'] == "Deployment MetaData" or data['csv_type'] == 'Device MetaData' or data['csv_type'] == 'Input Data':
			return data
		else:
			raise serializers.ValidationError({'wrong_csv_type': "wrong_csv_type "},code='wrong_csv_type')
	class Meta:
		model = CsvFileData
		fields = ['csv_type','upload_identifier','csv_file','update_by']

class DeploymentMetadataSerializer(serializers.ModelSerializer):
	class Meta:
		model = DeploymentMetadata
		fields = '__all__'

class DeviceMetadataSerializer(serializers.ModelSerializer):
	class Meta:
		model = DeviceMetaData
		fields = '__all__'

class InputdataSerializer(serializers.ModelSerializer):
	class Meta:
		model = InputData
		fields = '__all__'

class MapSerializer(serializers.ModelSerializer):
	# upload_identifier=serializers.CharField(required=True)
	class Meta:
		model = InputData
		fields = ['longitude','latitude']

		
class licenseSerializer(serializers.ModelSerializer):

	class Meta:
		model = License
		fields ='__all__'

class PostFilelicenseSerializer(serializers.ModelSerializer):
	def validate(self,data):
		if not CsvFileData.objects.filter(upload_identifier=data['upload_identifier']).exists():
			 raise serializers.ValidationError({'upload_identifier': "upload_identifier "},code='upload_identifier')
		elif not License.objects.filter(id=(data['licence_type_id']).id).exists():
			raise serializers.ValidationError({'licence_type_id': "licence_type_id"},code='licence_type_id')
		elif not FileUploadStatus.objects.filter(id=(data['fileuploadstatus_id']).id).exists():
			raise serializers.ValidationError({'fileuploadstatus_id': "fileuploadstatus_id"},code='fileuploadstatus_id')
		return data
	def create(self, data):
		CsvFileData.objects.filter(upload_identifier=data['upload_identifier']).update(licence_type_id=data['licence_type_id'],fileuploadstatus_id=data['fileuploadstatus_id'])
			
		for data in CsvFileData.objects.filter(upload_identifier=data['upload_identifier']):

			instance=get_object_or_404(CsvFileData,id=data.id)
			import os
			if os.path.exists("media/"+str(instance.csv_file)):
				os.remove("media/"+str(instance.csv_file))
		
		return data

	class Meta:
		model = CsvFileData
		fields =['upload_identifier','licence_type_id','fileuploadstatus_id']	

#=============================================Draft APIs serializer=================================================

class DraftSerializer(serializers.ModelSerializer):
	class Meta:
		model = CsvFileData
		fields = ['assign_name','upload_identifier','created_at','update_at','fileuploadstatus_id']

class DraftDetailsSerializer(serializers.Serializer):
	upload_identifier = serializers.CharField(required=True)
	fileuploadstatus_id =  serializers.IntegerField(required=True)
	def validate(self, data):
		# print(data)
		# print((data['fileuploadstatus_id']))
		if not CsvFileData.objects.filter(upload_identifier=data['upload_identifier']).exists():
			 raise serializers.ValidationError({'upload_identifier': "upload_identifier "},code='upload_identifier')
		elif not FileUploadStatus.objects.filter(id=(data['fileuploadstatus_id'])).exists():
			raise serializers.ValidationError({'fileuploadstatus_id': "fileuploadstatus_id"},code='fileuploadstatus_id')
		
		return data
	class Meta:
		fields = ['upload_identifier','fileuploadstatus_id']