from data_upload.models import CsvFileData,DeploymentMetadata,DeviceMetaData,InputData
import django_filters

class CsvFileDataFilter(django_filters.FilterSet):
    class Meta:
        model = CsvFileData
        fields = ['assign_name','upload_identifier', 'created_at']


class DeploymentMetadataFilter(django_filters.FilterSet):
    class Meta:
        model = DeploymentMetadata
        fields =  '__all__'


class DeviceMetaDataFilter(django_filters.FilterSet):
    class Meta:
        model = DeviceMetaData
        fields =  '__all__'


class InputDataFilter(django_filters.FilterSet):
    class Meta:
        model = InputData
        fields = '__all__'