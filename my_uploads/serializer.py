from rest_framework import serializers
from data_upload.models import *




class MyUploadsSerializer(serializers.ModelSerializer):

	class Meta:
		model = CsvFileData
		fields =['assign_name','upload_identifier','species_name','created_at']
	
	species_name = serializers.SerializerMethodField('get_species_name')

	def get_species_name(self, obj):
			
			if DeploymentMetadata.objects.filter(upload_identifier=obj.upload_identifier).first():
				scientific_name =  DeploymentMetadata.objects.filter(upload_identifier=obj.upload_identifier).first().scientific_name
			else:
				scientific_name=''
			return scientific_name

class MyUploadsDetailsSerializer(serializers.ModelSerializer):

	class Meta:
		model = CsvFileData
		fields =['assign_name','csv_type','created_at','licence_type_id',]
		depth=3

class DeploymentMetaDataFileDetailedDataSerializer(serializers.ModelSerializer):

	class Meta:
		model = DeploymentMetadata
		fields ='__all__'
class DeviceMetaDataFileDetailedDataSerializer(serializers.ModelSerializer):

	class Meta:
		model = DeviceMetaData
		fields ='__all__'
class InputDataFileDetailedDataSerializer(serializers.ModelSerializer):

	class Meta:
		model = InputData
		fields ='__all__'