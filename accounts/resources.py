from import_export import resources
from .models import  Institutions


class InstitutionsAdminResource(resources.ModelResource):

    class Meta:
        model = Institutions
        skip_unchanged = True
        report_skipped = True
        exclude = ('id',)
        import_id_fields = ('institution_id', 'name',)