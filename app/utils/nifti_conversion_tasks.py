"""
Celery tasks for NIfTI conversion.
"""

import logging
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.db import transaction

from app.models import DICOMSeries
from app.utils.dcm_to_nifti_converter import convert_series_with_rtstructs

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def convert_series_to_nifti(self, series_ids):
    """
    Celery task to convert multiple DICOM series and their associated RTStructs to NIfTI.
    
    Args:
        series_ids: List of DICOMSeries IDs to convert
        
    Returns:
        Dictionary with conversion results for all series
    """
    progress_recorder = ProgressRecorder(self)
    total_series = len(series_ids)
    results = {
        'success': True,
        'total_series': total_series,
        'processed_series': 0,
        'failed_series': 0,
        'series_results': [],
        'errors': []
    }
    
    def progress_callback(pct, message):
        """Update progress for Celery."""
        overall_pct = int((results['processed_series'] / total_series) * 100 + (pct / total_series))
        progress_recorder.set_progress(overall_pct, 100, description=message)
    
    for idx, series_id in enumerate(series_ids, 1):
        try:
            series = DICOMSeries.objects.get(id=series_id)
            base_message = f"Converting series {idx}/{total_series}: {series.series_instance_uid[:20]}..."
            progress_recorder.set_progress(
                int((idx - 1) / total_series * 100),
                100,
                description=base_message
            )
            
            # Convert the series and its associated RTStructs
            result = convert_series_with_rtstructs(series_id, progress_callback)
            
            if result['success']:
                results['processed_series'] += 1
            else:
                results['failed_series'] += 1
                results['errors'].extend(result.get('errors', []))
            
            results['series_results'].append({
                'series_id': series_id,
                'series_uid': series.series_instance_uid,
                'success': result['success'],
                'image_nifti': result.get('image_nifti'),
                'rtstruct_count': len(result.get('rtstruct_niftis', [])),
                'errors': result.get('errors', [])
            })
            
        except DICOMSeries.DoesNotExist:
            error_msg = f"Series {series_id} not found"
            logger.error(error_msg)
            results['failed_series'] += 1
            results['errors'].append(error_msg)
            results['series_results'].append({
                'series_id': series_id,
                'success': False,
                'errors': [error_msg]
            })
        except Exception as e:
            error_msg = f"Error processing series {series_id}: {str(e)}"
            logger.error(error_msg)
            results['failed_series'] += 1
            results['errors'].append(error_msg)
            results['series_results'].append({
                'series_id': series_id,
                'success': False,
                'errors': [error_msg]
            })
    
    # Final progress update
    progress_recorder.set_progress(100, 100, description="NIfTI conversion complete!")
    
    # Set overall success flag
    if results['failed_series'] > 0:
        results['success'] = results['processed_series'] > 0
    
    return results
