from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from app.models import DICOMFileArchive, Patient, DICOMStudy, DICOMSeries, DICOMInstance, RTStructROI
from app.utils.dicom_processor import process_dicom_archive
from app.utils.extract_roi_information import extract_roi_information
import os


def _delete_instance_files(instances):
    """Helper to delete files for a queryset or list of instances."""
    for instance in instances:
        if instance.instance_file_path:
            try:
                if os.path.exists(instance.instance_file_path):
                    os.remove(instance.instance_file_path)
            except Exception:
                pass  # Continue even if file deletion fails


def _get_patient_instances(patient):
    """Get all instances for a patient through the cascade."""
    return DICOMInstance.objects.filter(
        series__study__patient=patient
    )


def _get_study_instances(study):
    """Get all instances for a study through the cascade."""
    return DICOMInstance.objects.filter(
        series__study=study
    )


def _get_series_instances(series):
    """Get all instances for a series."""
    return DICOMInstance.objects.filter(series=series)


def home(request):
    """Home page view."""
    return render(request, "app/home.html")


def dicom_archive_list(request):
    """View to list all uploaded DICOM archives."""
    archives = DICOMFileArchive.objects.all().order_by("-created_at")
    return render(request, "app/archive_list.html", {"archives": archives})


def dicom_archive_upload(request):
    """View to upload a new DICOM zip file."""
    if request.method == "POST":
        if "file" in request.FILES:
            uploaded_file = request.FILES["file"]
            # Check if file is a zip
            if not uploaded_file.name.endswith(".zip"):
                messages.error(request, "Please upload a ZIP file containing DICOM files.")
                return redirect("dicom_archive_upload")
            
            # Save the file
            archive = DICOMFileArchive(file=uploaded_file)
            archive.save()
            messages.success(request, f"File '{uploaded_file.name}' uploaded successfully.")
            return redirect("dicom_archive_list")
        else:
            messages.error(request, "Please select a file to upload.")
    
    return render(request, "app/archive_upload.html")


def dicom_archive_detail(request, pk):
    """View to show details of a specific DICOM archive and process it."""
    archive = get_object_or_404(DICOMFileArchive, pk=pk)
    return render(request, "app/archive_detail.html", {"archive": archive})


@require_POST
def dicom_archive_process(request, pk):
    """View to process a DICOM archive using Celery."""
    archive = get_object_or_404(DICOMFileArchive, pk=pk)
    
    # Enqueue the processing task using Celery
    task = process_dicom_archive.delay(archive_id=pk)
    
    # Return immediately with task_id for celery-progress
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "message": "Processing task queued successfully",
            "task_status": "queued",
            "task_id": task.id
        })
    
    messages.info(request, "DICOM processing task has been queued and will run in the background.")
    return redirect("dicom_archive_detail", pk=pk)


def dicom_archive_delete(request, pk):
    """View to delete a DICOM archive."""
    archive = get_object_or_404(DICOMFileArchive, pk=pk)
    
    if request.method == "POST":
        archive_name = archive.file.name
        archive.delete()
        messages.success(request, f"Archive '{archive_name}' deleted successfully.")
        return redirect("dicom_archive_list")
    
    return render(request, "app/archive_confirm_delete.html", {"archive": archive})


def patient_list(request):
    """View to list all patients."""
    patients = Patient.objects.all().order_by("-created_at")
    return render(request, "app/patient_list.html", {"patients": patients})


def patient_detail(request, pk):
    """View to show patient details with their studies."""
    patient = get_object_or_404(Patient, pk=pk)
    studies = DICOMStudy.objects.filter(patient=patient).prefetch_related("dicomseries_set")
    return render(request, "app/patient_detail.html", {"patient": patient, "studies": studies})


def study_detail(request, pk):
    """View to show study details with series."""
    study = get_object_or_404(DICOMStudy, pk=pk)
    series_list = DICOMSeries.objects.filter(study=study).prefetch_related("dicominstance_set")
    return render(request, "app/study_detail.html", {"study": study, "series_list": series_list})


def rtstruct_list(request):
    """View to list all RT Structure Set series with their instances."""
    rtstruct_series = DICOMSeries.objects.filter(
        modality='RTSTRUCT'
    ).select_related('study', 'study__patient').prefetch_related('dicominstance_set')
    return render(request, "app/rtstruct_list.html", {"rtstruct_series": rtstruct_series})


@require_POST
def rtstruct_extract(request):
    """View to extract ROI information from selected RTSTRUCT instances using Celery."""
    instance_ids = request.POST.getlist('instance_ids')
    
    if not instance_ids:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": False,
                "error": "No RTSTRUCT instances selected."
            })
        messages.error(request, "No RTSTRUCT instances selected.")
        return redirect("rtstruct_list")
    
    # Convert to integers
    try:
        instance_ids = [int(iid) for iid in instance_ids]
    except ValueError:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": False,
                "error": "Invalid instance IDs provided."
            })
        messages.error(request, "Invalid instance IDs provided.")
        return redirect("rtstruct_list")
    
    # Enqueue the extraction task using Celery
    task = extract_roi_information.delay(instance_ids=instance_ids)
    
    # Return immediately with task_id for celery-progress
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "message": "ROI extraction task queued successfully",
            "task_status": "queued",
            "task_id": task.id,
            "total_instances": len(instance_ids)
        })
    
    messages.info(request, f"ROI extraction task has been queued for {len(instance_ids)} instance(s).")
    return redirect("rtstruct_list")


def roi_list(request):
    """View to list all ROIs grouped by referenced image series (CT/MR) with associated RTStructs."""
    from django.db.models import Count
    
    # Get all series that are referenced by RTStruct instances (these are CT/MR image series)
    referenced_series = DICOMSeries.objects.filter(
        referenced_series_uid__isnull=False  # RTStruct instances reference this series
    ).select_related(
        'study', 
        'study__patient'
    ).annotate(
        rtstruct_count=Count('referenced_series_uid__series', distinct=True)
    ).distinct().order_by(
        'study__patient__patient_id',
        'series_instance_uid'
    )
    
    # For each referenced series, get the RTStruct series that reference it
    series_with_rtstructs = []
    for ref_series in referenced_series:
        # Get all RTStruct series that have instances referencing this series
        rtstruct_series = DICOMSeries.objects.filter(
            modality='RTSTRUCT',
            dicominstance__referenced_series_instance_uid=ref_series
        ).select_related(
            'study',
            'study__patient'
        ).annotate(
            roi_count=Count('dicominstance__rtstructroi')
        ).distinct()
        
        series_with_rtstructs.append({
            'referenced_series': ref_series,
            'rtstruct_series': rtstruct_series
        })
    
    return render(request, "app/roi_list.html", {"series_with_rtstructs": series_with_rtstructs})


def roi_detail(request, series_id):
    """View to show all ROIs for a specific structure set (series), grouped by referenced series."""
    series = get_object_or_404(
        DICOMSeries.objects.select_related('study', 'study__patient'),
        id=series_id,
        modality='RTSTRUCT'
    )
    
    # Get all ROIs for this series with their instance and referenced series info
    rois = RTStructROI.objects.filter(
        instance__series=series
    ).select_related(
        'instance',
        'instance__referenced_series_instance_uid'
    ).order_by('instance__instance_number', 'roi_number')
    
    # Group ROIs by referenced series instance UID
    rois_by_ref_series = {}
    for roi in rois:
        ref_series = roi.instance.referenced_series_instance_uid
        ref_series_uid = ref_series.series_instance_uid if ref_series else 'Unknown'
        ref_series_key = ref_series.id if ref_series else None
        
        if ref_series_key not in rois_by_ref_series:
            rois_by_ref_series[ref_series_key] = {
                'series': ref_series,
                'series_uid': ref_series_uid,
                'rois': []
            }
        rois_by_ref_series[ref_series_key]['rois'].append(roi)
    
    return render(request, "app/roi_detail.html", {
        "series": series, 
        "rois_by_ref_series": rois_by_ref_series
    })


@require_POST
def patient_delete_multiple(request):
    """Delete multiple patients and all their associated data including files."""
    patient_ids = request.POST.getlist('patient_ids')
    
    if not patient_ids:
        messages.warning(request, "No patients selected for deletion.")
        return redirect("patient_list")
    
    deleted_count = 0
    error_count = 0
    
    for patient_id in patient_ids:
        try:
            patient = Patient.objects.get(pk=patient_id)
            # First delete all associated files
            instances = _get_patient_instances(patient)
            _delete_instance_files(instances)
            # Then delete the patient (cascades to database records)
            patient.delete()
            deleted_count += 1
        except Patient.DoesNotExist:
            error_count += 1
        except Exception as e:
            error_count += 1
            messages.error(request, f"Error deleting patient {patient_id}: {str(e)}")
    
    if deleted_count > 0:
        messages.success(request, f"Successfully deleted {deleted_count} patient(s) and all their files.")
    if error_count > 0:
        messages.warning(request, f"Failed to delete {error_count} patient(s).")
    
    return redirect("patient_list")


@require_POST
def patient_delete(request, pk):
    """Delete a patient and all associated data including files."""
    patient = get_object_or_404(Patient, pk=pk)
    patient_name = patient.patient_id
    
    try:
        # First delete all associated files
        instances = _get_patient_instances(patient)
        _delete_instance_files(instances)
        # Then delete the patient (cascades to database records)
        patient.delete()
        messages.success(request, f"Patient '{patient_name}' and all associated files deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting patient: {str(e)}")
    
    return redirect("patient_list")


@require_POST
def study_delete(request, pk):
    """Delete a study and all associated series, instances, and files."""
    study = get_object_or_404(DICOMStudy, pk=pk)
    study_uid = study.study_instance_uid[:20]
    patient_pk = study.patient.pk
    
    try:
        # First delete all associated files
        instances = _get_study_instances(study)
        _delete_instance_files(instances)
        # Then delete the study (cascades to series and instances in database)
        study.delete()
        messages.success(request, f"Study '{study_uid}...' and all associated files deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting study: {str(e)}")
    
    return redirect("patient_detail", pk=patient_pk)


@require_POST
def series_delete(request, pk):
    """Delete a series and all associated instances with their files."""
    series = get_object_or_404(DICOMSeries, pk=pk)
    series_uid = series.series_instance_uid[:20]
    study_pk = series.study.pk
    
    try:
        # First delete all associated files
        instances = _get_series_instances(series)
        _delete_instance_files(instances)
        # Then delete the series (cascades to instances in database)
        series.delete()
        messages.success(request, f"Series '{series_uid}...' and all associated files deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting series: {str(e)}")
    
    return redirect("study_detail", pk=study_pk)


@require_POST
def instance_delete(request, pk):
    """Delete an instance and its associated DICOM file."""
    instance = get_object_or_404(DICOMInstance, pk=pk)
    sop_uid = instance.sop_instance_uid[:20]
    series_pk = instance.series.pk
    
    try:
        # Delete the DICOM file
        if instance.instance_file_path:
            import os
            try:
                if os.path.exists(instance.instance_file_path):
                    os.remove(instance.instance_file_path)
            except Exception as e:
                messages.warning(request, f"Could not delete file: {str(e)}")
        
        instance.delete()
        messages.success(request, f"Instance '{sop_uid}...' deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting instance: {str(e)}")
    
    return redirect("study_detail", pk=instance.series.study.pk)
