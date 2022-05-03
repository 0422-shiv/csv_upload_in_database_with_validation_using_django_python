from rest_framework import serializers
from data_upload.models import CsvFileData
from data_upload.serializer import licenseSerializer, FileUploadSerializer
from data_upload.models import License

class AllDataSerializer(serializers.ModelSerializer):

    class Meta:

        model = CsvFileData
        fields = ('assign_name','upload_identifier', 'created_at', 'user_name','species_name')
        # depth = 1
    user_name = serializers.SerializerMethodField('get_user_name')

    def get_user_name(self, obj):
            return obj.created_by.username
        
    species_name = serializers.SerializerMethodField('get_species_name')

    def get_species_name(self, obj):
            return "Shark"
