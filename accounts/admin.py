from django.contrib import admin
from .models import User, Institutions
from import_export.admin import ImportExportModelAdmin
from .resources import *

# Register your models here.

admin.site.register(User)

@admin.register(Institutions)
class InstitutionsAdmin(ImportExportModelAdmin):
    resource_class  =   InstitutionsAdminResource
    list_display = ['institution_id', 'name',]
 