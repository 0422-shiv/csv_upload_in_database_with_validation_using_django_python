from rest_framework import serializers
from accounts.models import User
from data_upload.models import CsvFileData, CoAuthors,DeploymentMetadata

class UserListsSerializer(serializers.ModelSerializer):
    no_of_uploads = serializers.SerializerMethodField('get_no_of_uploads')
    class Meta:
        model = User
        fields = ['id','username', 'email', 'institution_id', 'country', 'city','no_of_uploads','created_at']
        depth = 1
    

    def get_no_of_uploads(self, obj):
       return CsvFileData.objects.filter(created_by__id=obj.id).filter(csv_type='Input Data').filter(fileuploadstatus_id=8).count()



class UserUploadsSerializer(serializers.ModelSerializer):
    species_name = serializers.SerializerMethodField('get_species_name')
    class Meta:
        model = CsvFileData
        fields = ['assign_name','upload_identifier', 'species_name','created_at']
    
    def get_species_name(self, obj):	
        if DeploymentMetadata.objects.filter(upload_identifier=obj.upload_identifier).first():
            scientific_name =  DeploymentMetadata.objects.filter(upload_identifier=obj.upload_identifier).first().scientific_name
        else:
            scientific_name=''
        return scientific_name



class UserUploadsDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CsvFileData
        fields = ['assign_name','csv_type','created_at','user_name','email','institution','licence_type']

        depth = 1
    user_name = serializers.SerializerMethodField('get_user_name')
    email=serializers.SerializerMethodField('get_user_email')
    institution=serializers.SerializerMethodField('get_user_institution')
    licence_type=serializers.SerializerMethodField('get_licence_type')
    def get_user_name(self, obj):
            return obj.created_by.username
    def get_user_email(self, obj):
            return obj.created_by.email
    def get_user_institution(self, obj):
            if obj.created_by.institution_id:
                return obj.created_by.institution_id.name
            else :
                return None
    def get_licence_type(self, obj):
            if obj.licence_type_id:
                return obj.licence_type_id.name
            else :
                return None

class CoAuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = CoAuthors
        fields = ['author_name','author_email', 'institution_id']

        # depth = 1



