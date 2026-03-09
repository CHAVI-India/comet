from django.contrib import admin
from app.models import Patient, DICOMStudy, DICOMSeries, DICOMInstance, StapleROI, RTStructROI, DICOMFileArchive, StructureROIPair

# Register your models here.

class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'patient_name', 'patient_dob', 'patient_gender')
    search_fields = ('patient_id', 'patient_name')
    list_filter = ('patient_gender',)

admin.site.register(Patient, PatientAdmin)


class DICOMStudyAdmin(admin.ModelAdmin):
    list_display = ( 'patient','study_instance_uid', 'study_date')
    search_fields = ('study_instance_uid', 'patient__patient_id', 'patient__patient_name')
    list_filter = ('study_date',)

admin.site.register(DICOMStudy, DICOMStudyAdmin)

class DICOMSeriesAdmin(admin.ModelAdmin):
    list_display = ('get_patient_id', 'get_study_id', 'series_instance_uid', 'modality', 'series_date')
    search_fields = ('series_instance_uid', 'study__study_instance_uid', 'study__patient__patient_id')
    list_filter = ('modality', 'study__study_date', 'series_date')
    
    @admin.display(ordering='study__study_instance_uid', description='Study ID')
    def get_study_id(self, obj):
        return obj.study.study_instance_uid if obj.study else '-'
    
    @admin.display(ordering='study__patient__patient_id', description='Patient ID')
    def get_patient_id(self, obj):
        return obj.study.patient.patient_id if obj.study and obj.study.patient else '-'

admin.site.register(DICOMSeries, DICOMSeriesAdmin)

class DICOMInstanceAdmin(admin.ModelAdmin):
    list_display = ('get_patient_id', 'get_study_id', 'get_series_id', 'sop_instance_uid', 'instance_number')
    search_fields = ('sop_instance_uid', 'series__series_instance_uid', 'series__study__study_instance_uid', 'series__study__patient__patient_id')
    list_filter = ('series__modality', 'series__study__study_date')
    
    @admin.display(ordering='series__series_instance_uid', description='Series ID')
    def get_series_id(self, obj):
        return obj.series.series_instance_uid if obj.series else '-'
    
    @admin.display(ordering='series__study__study_instance_uid', description='Study ID')
    def get_study_id(self, obj):
        return obj.series.study.study_instance_uid if obj.series and obj.series.study else '-'
    
    @admin.display(ordering='series__study__patient__patient_id', description='Patient ID')
    def get_patient_id(self, obj):
        return obj.series.study.patient.patient_id if obj.series and obj.series.study and obj.series.study.patient else '-'

admin.site.register(DICOMInstance, DICOMInstanceAdmin)

class StapleROIAdmin(admin.ModelAdmin):
    list_display = ('get_patient_id', 'get_study_id', 'get_series_id', 'get_instance_id', 'created_at')
    search_fields = ('instance__sop_instance_uid', 'instance__series__series_instance_uid', 'instance__series__study__study_instance_uid', 'instance__series__study__patient__patient_id')
    list_filter = ('created_at', 'instance__series__modality')
    
    @admin.display(ordering='instance__sop_instance_uid', description='Instance ID')
    def get_instance_id(self, obj):
        return obj.instance.sop_instance_uid if obj.instance else '-'
    
    @admin.display(ordering='instance__series__series_instance_uid', description='Series ID')
    def get_series_id(self, obj):
        return obj.instance.series.series_instance_uid if obj.instance and obj.instance.series else '-'
    
    @admin.display(ordering='instance__series__study__study_instance_uid', description='Study ID')
    def get_study_id(self, obj):
        return obj.instance.series.study.study_instance_uid if obj.instance and obj.instance.series and obj.instance.series.study else '-'
    
    @admin.display(ordering='instance__series__study__patient__patient_id', description='Patient ID')
    def get_patient_id(self, obj):
        return obj.instance.series.study.patient.patient_id if obj.instance and obj.instance.series and obj.instance.series.study and obj.instance.series.study.patient else '-'

admin.site.register(StapleROI, StapleROIAdmin)

class RTStructROIAdmin(admin.ModelAdmin):
    list_display = ('roi_name', 'roi_number', 'get_patient_id', 'get_study_id', 'get_series_id', 'get_instance_id', 'get_staple_roi')
    search_fields = ('roi_name', 'roi_number', 'instance__sop_instance_uid', 'instance__series__series_instance_uid', 'instance__series__study__study_instance_uid', 'instance__series__study__patient__patient_id')
    list_filter = ('roi_name', 'created_at', 'instance__series__modality')
    
    @admin.display(ordering='instance__sop_instance_uid', description='Instance ID')
    def get_instance_id(self, obj):
        return obj.instance.sop_instance_uid if obj.instance else '-'
    
    @admin.display(ordering='staple_roi__instance__sop_instance_uid', description='Staple ROI')
    def get_staple_roi(self, obj):
        return obj.staple_roi.instance.sop_instance_uid if obj.staple_roi and obj.staple_roi.instance else '-'
    
    @admin.display(ordering='instance__series__series_instance_uid', description='Series ID')
    def get_series_id(self, obj):
        return obj.instance.series.series_instance_uid if obj.instance and obj.instance.series else '-'
    
    @admin.display(ordering='instance__series__study__study_instance_uid', description='Study ID')
    def get_study_id(self, obj):
        return obj.instance.series.study.study_instance_uid if obj.instance and obj.instance.series and obj.instance.series.study else '-'
    
    @admin.display(ordering='instance__series__study__patient__patient_id', description='Patient ID')
    def get_patient_id(self, obj):
        return obj.instance.series.study.patient.patient_id if obj.instance and obj.instance.series and obj.instance.series.study and obj.instance.series.study.patient else '-'

admin.site.register(RTStructROI, RTStructROIAdmin)

class DICOMFileArchiveAdmin(admin.ModelAdmin):
    list_display = ('file', 'archive_extracted', 'archive_extraction_date_time', 'created_at')
    search_fields = ('file',)
    list_filter = ('archive_extracted', 'created_at', 'archive_extraction_date_time')

admin.site.register(DICOMFileArchive, DICOMFileArchiveAdmin)

class StructureROIPairAdmin(admin.ModelAdmin):
    list_display = ('get_reference_roi', 'get_target_roi', 'metric_calculated', 'metric_value', 'created_at')
    search_fields = ('reference_rt_structure_roi__roi_name', 'target_rt_structure_roi__roi_name', 'metric_calculated')
    list_filter = ('metric_calculated', 'created_at')
    
    @admin.display(ordering='reference_rt_structure_roi__roi_name', description='Reference ROI')
    def get_reference_roi(self, obj):
        return obj.reference_rt_structure_roi.roi_name if obj.reference_rt_structure_roi else '-'
    
    @admin.display(ordering='target_rt_structure_roi__roi_name', description='Target ROI')
    def get_target_roi(self, obj):
        return obj.target_rt_structure_roi.roi_name if obj.target_rt_structure_roi else '-'

admin.site.register(StructureROIPair, StructureROIPairAdmin)


