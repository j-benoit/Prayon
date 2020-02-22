from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import *


# Define resources for Import/Export
class TypeResource(resources.ModelResource):
    class Meta:
        model = Type


class ExtractSAPResource(resources.ModelResource):
    class Meta:
        model = ExtractSAP


class Updated_InfoResource(resources.ModelResource):
    class Meta:
        model = Updated_info


class WorkDataResource(resources.ModelResource):
    class Meta:
        model = Work_data


class ProjecthistoryResource(resources.ModelResource):
    class Meta:
        model = Project_history
       


# Define class for Import/Export in admin panel
class TypeAdmin(ImportExportModelAdmin):
    resource_class = TypeResource
    # list_display = ('id', 'category',)
    ordering = ('id',)


class ExtractSAPAdmin(ImportExportModelAdmin):
    resource_class = ExtractSAPResource
    ordering = ('id',)


class Updated_InfoAdmin(ImportExportModelAdmin):
    resource_class = Updated_InfoResource
    ordering = ('id',)


class WorkDataAdmin(ImportExportModelAdmin):
    resource_class = WorkDataResource
    list_display = ('id', 'id_SAP', 'id_user', 'status','created_date', 'modified_date')
    ordering = ('id',)


class ProjecthistoryAdmin(ImportExportModelAdmin):
    resource_class = ProjecthistoryResource
    list_display = ('id', 'id_user', 'date', 'open_drawings', 'backlog_drawings', 'closed_drawings', 'checked_drawings', 'avg_closed_time', 'avg_backlog_time')
    ordering = ('id',)


# Register your models here.
admin.site.register(Type, TypeAdmin)
admin.site.register(ExtractSAP, ExtractSAPAdmin)
admin.site.register(Updated_info, Updated_InfoAdmin)
admin.site.register(Work_data, WorkDataAdmin)
admin.site.register(Project_history, ProjecthistoryAdmin)
admin.site.register(communData)
