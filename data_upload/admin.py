from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(FileUploadStatus)
admin.site.register(CsvFileData)
admin.site.register(CsvFileHeaders)
admin.site.register(CoAuthors)
admin.site.register(License)
admin.site.register(DeploymentMetadata)
admin.site.register(DeviceMetaData)
admin.site.register(InputData)
# admin.site.register(TempInputData)

