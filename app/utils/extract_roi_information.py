"""
This function will run as a celery task to extract ROI information from RTStructureset files for the application.
This will also run as an action where the user can select one or multiple RTStructureset files.
The action will first read the instance information to get the path of the file from the DICOMInstance table
After that it will use Pydicom to extract the name of each ROI in the structure set and populate it to the RTStructROI
As the RTStructROI is linked to the DICOMInstance model via the instance field it will update the information on that FK reference.
The extraction of ROI will be done as a celery task using celery progress
"""

import os
import pydicom
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.conf import settings

from app.models import DICOMInstance, DICOMSeries, RTStructROI


@shared_task(bind=True)
def extract_roi_information(self, instance_ids):
    """
    Extract ROI information from RT Structure Set files.

    Args:
        self: Celery task instance
        instance_ids: List of DICOMInstance IDs to process (RTSTRUCT modality)

    Returns:
        dict: A summary of the extraction results
    """
    progress_recorder = ProgressRecorder(self)

    total_instances = len(instance_ids)
    processed_instances = 0
    total_rois_extracted = 0
    errors = []

    for idx, instance_id in enumerate(instance_ids):
        try:
            # Get the instance
            instance = DICOMInstance.objects.select_related('series').get(id=instance_id)

            # Check if series modality is RTSTRUCT
            if instance.series.modality != 'RTSTRUCT':
                errors.append(f"Instance {instance_id}: Not an RTSTRUCT file (modality: {instance.series.modality})")
                processed_instances += 1
                progress_recorder.set_progress(idx + 1, total_instances, description=f"Skipped non-RTSTRUCT instance {instance_id}")
                continue

            # Get the file path
            file_path = instance.instance_file_path
            if not file_path:
                errors.append(f"Instance {instance_id}: No file path available")
                processed_instances += 1
                progress_recorder.set_progress(idx + 1, total_instances, description=f"No file path for instance {instance_id}")
                continue

            # Construct full path (file_path is relative to MEDIA_ROOT or absolute)
            if not os.path.isabs(file_path):
                full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            else:
                full_path = file_path

            # Check if file exists
            if not os.path.exists(full_path):
                errors.append(f"Instance {instance_id}: File not found at {full_path}")
                processed_instances += 1
                progress_recorder.set_progress(idx + 1, total_instances, description=f"File not found for instance {instance_id}")
                continue

            # Read DICOM file
            try:
                ds = pydicom.dcmread(full_path)
            except Exception as e:
                errors.append(f"Instance {instance_id}: Error reading DICOM - {str(e)}")
                processed_instances += 1
                progress_recorder.set_progress(idx + 1, total_instances, description=f"Error reading instance {instance_id}")
                continue

            # Extract ROI information from Structure Set
            if hasattr(ds, 'StructureSetROISequence'):
                rois_in_file = 0
                existing_roi_numbers = set(
                    RTStructROI.objects.filter(instance=instance).values_list('roi_number', flat=True)
                )

                for roi in ds.StructureSetROISequence:
                    roi_number = getattr(roi, 'ROINumber', None)
                    roi_name = getattr(roi, 'ROIName', None)
                    roi_description = getattr(roi, 'ROIDescription', None)
                    roi_generation_algorithm = getattr(roi, 'ROIGenerationAlgorithm', None)

                    if roi_number is not None and roi_name:
                        # Skip if ROI already exists for this instance
                        if roi_number in existing_roi_numbers:
                            continue

                        # Create new RTStructROI
                        RTStructROI.objects.create(
                            instance=instance,
                            roi_number=roi_number,
                            roi_name=roi_name,
                            roi_description=str(roi_description) if roi_description else None,
                            roi_generation_algorithm=str(roi_generation_algorithm) if roi_generation_algorithm else None
                        )
                        rois_in_file += 1
                        total_rois_extracted += 1

                processed_instances += 1
                progress_recorder.set_progress(
                    idx + 1,
                    total_instances,
                    description=f"Extracted {rois_in_file} ROIs from {instance.sop_instance_uid[:20]}..."
                )
            else:
                errors.append(f"Instance {instance_id}: No StructureSetROISequence found")
                processed_instances += 1
                progress_recorder.set_progress(idx + 1, total_instances, description=f"No ROI sequence in instance {instance_id}")

        except DICOMInstance.DoesNotExist:
            errors.append(f"Instance {instance_id}: Not found in database")
            progress_recorder.set_progress(idx + 1, total_instances, description=f"Instance {instance_id} not found")
        except Exception as e:
            errors.append(f"Instance {instance_id}: Unexpected error - {str(e)}")
            progress_recorder.set_progress(idx + 1, total_instances, description=f"Error processing instance {instance_id}")

    result = {
        "success": True,
        "total_instances": total_instances,
        "processed_instances": processed_instances,
        "total_rois_extracted": total_rois_extracted,
        "errors": errors,
    }

    return result