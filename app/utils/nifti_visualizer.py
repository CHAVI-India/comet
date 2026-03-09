"""
NIfTI Visualization Module

This module provides functionality to visualize NIfTI files (CT/MR images, RT structure masks,
and STAPLE contours) using matplotlib. It generates multi-slice views with overlay capabilities.
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Tuple, Dict
import numpy as np
import SimpleITK as sitk
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from django.conf import settings

logger = logging.getLogger(__name__)


def normalize_image(image_array: np.ndarray, window_center: Optional[float] = None, 
                    window_width: Optional[float] = None) -> np.ndarray:
    """
    Normalize image array for display with optional windowing.
    
    Args:
        image_array: Input image array
        window_center: Window center for CT windowing
        window_width: Window width for CT windowing
        
    Returns:
        Normalized image array (0-1 range)
    """
    # Make a copy to avoid modifying original
    normalized = image_array.copy().astype(np.float64)
    
    if window_center is not None and window_width is not None:
        # Apply CT windowing
        lower = window_center - window_width / 2
        upper = window_center + window_width / 2
        
        logger.info(f"Applying windowing: center={window_center}, width={window_width}, range=[{lower}, {upper}]")
        logger.info(f"Image value range before windowing: [{np.min(normalized)}, {np.max(normalized)}]")
        
        normalized = np.clip(normalized, lower, upper)
        normalized = (normalized - lower) / (upper - lower)
        
        logger.info(f"Image value range after windowing: [{np.min(normalized)}, {np.max(normalized)}]")
    else:
        # Simple min-max normalization
        min_val = np.min(normalized)
        max_val = np.max(normalized)
        
        logger.info(f"Auto-normalizing image: range=[{min_val}, {max_val}]")
        
        if max_val > min_val:
            normalized = (normalized - min_val) / (max_val - min_val)
        else:
            normalized = np.zeros_like(normalized)
    
    return normalized


def get_slice_indices(total_slices: int, num_slices: int = 9) -> List[int]:
    """
    Get evenly distributed slice indices for visualization.
    
    Args:
        total_slices: Total number of slices in the volume
        num_slices: Number of slices to display
        
    Returns:
        List of slice indices
    """
    if total_slices <= num_slices:
        return list(range(total_slices))
    
    # Get evenly distributed indices
    indices = np.linspace(0, total_slices - 1, num_slices, dtype=int)
    return indices.tolist()


def create_overlay_colormap(color: str = 'red', alpha: float = 0.5) -> ListedColormap:
    """
    Create a colormap for overlay visualization.
    
    Args:
        color: Color name for the overlay ('red', 'green', 'blue', 'yellow', 'cyan', 'magenta')
        alpha: Alpha transparency value (0-1)
        
    Returns:
        ListedColormap for overlay
    """
    color_map = {
        'red': [1, 0, 0],
        'green': [0, 1, 0],
        'blue': [0, 0, 1],
        'yellow': [1, 1, 0],
        'cyan': [0, 1, 1],
        'magenta': [1, 0, 1],
        'orange': [1, 0.5, 0],
        'purple': [0.5, 0, 1]
    }
    
    rgb = color_map.get(color.lower(), [1, 0, 0])
    
    # Create colormap: transparent for 0, colored for non-zero
    colors = [[0, 0, 0, 0], rgb + [alpha]]
    cmap = ListedColormap(colors)
    
    return cmap


def visualize_nifti_slices(
    image_path: str,
    mask_paths: Optional[List[Dict[str, str]]] = None,
    output_path: Optional[str] = None,
    num_slices: int = 9,
    window_center: Optional[float] = None,
    window_width: Optional[float] = None,
    figsize: Tuple[int, int] = (15, 10),
    title: Optional[str] = None
) -> str:
    """
    Visualize NIfTI image with optional mask overlays.
    
    Args:
        image_path: Path to the NIfTI image file
        mask_paths: List of dictionaries with 'path', 'label', and 'color' keys for masks
        output_path: Path to save the visualization (if None, auto-generated)
        num_slices: Number of slices to display
        window_center: Window center for CT windowing
        window_width: Window width for CT windowing
        figsize: Figure size (width, height)
        title: Title for the visualization
        
    Returns:
        Path to the saved visualization image
    """
    try:
        # Load the image
        image = sitk.ReadImage(image_path)
        image_array = sitk.GetArrayFromImage(image)
        
        # Get slice indices
        total_slices = image_array.shape[0]
        slice_indices = get_slice_indices(total_slices, num_slices)
        
        # Calculate grid dimensions
        cols = 3
        rows = int(np.ceil(len(slice_indices) / cols))
        
        # Create figure
        fig, axes = plt.subplots(rows, cols, figsize=figsize)
        if rows == 1 and cols == 1:
            axes = np.array([[axes]])
        elif rows == 1 or cols == 1:
            axes = axes.reshape(rows, cols)
        
        # Normalize image
        normalized_image = normalize_image(image_array, window_center, window_width)
        
        # Load masks if provided
        masks = []
        if mask_paths:
            for mask_info in mask_paths:
                try:
                    mask = sitk.ReadImage(mask_info['path'])
                    mask_array = sitk.GetArrayFromImage(mask)
                    masks.append({
                        'array': mask_array,
                        'label': mask_info.get('label', 'Mask'),
                        'color': mask_info.get('color', 'red')
                    })
                except Exception as e:
                    logger.warning(f"Failed to load mask {mask_info['path']}: {e}")
        
        # Plot each slice
        for idx, slice_idx in enumerate(slice_indices):
            row = idx // cols
            col = idx % cols
            ax = axes[row, col]
            
            # Display base image
            ax.imshow(normalized_image[slice_idx, :, :], cmap='gray', aspect='auto')
            
            # Overlay masks
            for mask in masks:
                mask_slice = mask['array'][slice_idx, :, :]
                if np.any(mask_slice > 0):
                    cmap = create_overlay_colormap(mask['color'], alpha=0.4)
                    ax.imshow(mask_slice, cmap=cmap, vmin=0, vmax=1, aspect='auto')
            
            ax.set_title(f'Slice {slice_idx + 1}/{total_slices}', fontsize=10)
            ax.axis('off')
        
        # Hide unused subplots
        for idx in range(len(slice_indices), rows * cols):
            row = idx // cols
            col = idx % cols
            axes[row, col].axis('off')
        
        # Add title
        if title:
            fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # Add legend for masks
        if masks:
            legend_elements = []
            for mask in masks:
                from matplotlib.patches import Patch
                legend_elements.append(Patch(facecolor=mask['color'], alpha=0.4, label=mask['label']))
            fig.legend(handles=legend_elements, loc='upper right', fontsize=10)
        
        plt.tight_layout()
        
        # Generate output path if not provided
        if output_path is None:
            vis_dir = Path(settings.MEDIA_ROOT) / "visualizations"
            vis_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            import hashlib
            import time
            hash_input = f"{image_path}_{time.time()}"
            file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:10]
            output_path = vis_dir / f"vis_{file_hash}.png"
        
        # Save figure
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        logger.info(f"Visualization saved to {output_path}")
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Error creating visualization: {e}")
        raise


def visualize_patient_rois(
    image_series_id: int,
    roi_names: Optional[List[str]] = None,
    include_staple: bool = True,
    num_slices: int = None,
    window_center: Optional[float] = None,
    window_width: Optional[float] = None
) -> Dict[str, Dict]:
    """
    Create visualizations for a patient's image series with ROI overlays.
    Generates individual slice images for interactive viewing.
    
    Args:
        image_series_id: ID of the image series (CT/MR)
        roi_names: List of ROI names to visualize (if None, visualize all)
        include_staple: Whether to include STAPLE contours
        num_slices: Number of slices to display (None = all slices)
        window_center: Window center for CT windowing
        window_width: Window width for CT windowing
        
    Returns:
        Dictionary mapping ROI names to visualization info with slice paths
    """
    from app.models import DICOMSeries, DICOMInstance
    import json
    import hashlib
    import time
    
    visualizations = {}
    
    try:
        # Get the image series
        image_series = DICOMSeries.objects.get(id=image_series_id)
        
        # Check if NIfTI file exists
        if not image_series.nifti_file_path:
            raise ValueError(f"No NIfTI file found for series {image_series_id}")
        
        image_path = Path(settings.MEDIA_ROOT) / image_series.nifti_file_path
        if not image_path.exists():
            raise ValueError(f"NIfTI file not found: {image_path}")
        
        # Load the image
        image = sitk.ReadImage(str(image_path))
        image_array = sitk.GetArrayFromImage(image)
        total_slices = image_array.shape[0]
        
        logger.info(f"Loaded image: shape={image_array.shape}, dtype={image_array.dtype}")
        logger.info(f"Image statistics: min={np.min(image_array)}, max={np.max(image_array)}, mean={np.mean(image_array):.2f}")
        
        # Set default windowing for CT
        if image_series.modality == 'CT':
            if window_center is None:
                window_center = 40
            if window_width is None:
                window_width = 400
        
        logger.info(f"Modality: {image_series.modality}, Window: center={window_center}, width={window_width}")
        
        # Normalize image
        normalized_image = normalize_image(image_array, window_center, window_width)
        
        # Find all RTStruct series that reference this image series
        rtstruct_series = DICOMSeries.objects.filter(
            modality='RTSTRUCT',
            dicominstance__referenced_series_instance_uid=image_series,
            nifti_file_path__isnull=False
        ).exclude(nifti_file_path='').distinct()
        
        # Collect all available ROIs
        all_rois = {}
        for rtstruct in rtstruct_series:
            nifti_dir = Path(settings.MEDIA_ROOT) / rtstruct.nifti_file_path
            metadata_path = nifti_dir / "rtstruct_metadata.json"
            
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    for roi in metadata.get('rois', []):
                        roi_name = roi['name']
                        if roi_names is None or roi_name in roi_names:
                            if roi_name not in all_rois:
                                all_rois[roi_name] = []
                            
                            # Check if mask file exists
                            from app.utils.dcm_to_nifti_converter import sanitize_for_path
                            safe_roi_name = sanitize_for_path(roi_name)
                            mask_path = nifti_dir / f"{safe_roi_name}.nii.gz"
                            
                            if mask_path.exists():
                                all_rois[roi_name].append({
                                    'path': str(mask_path),
                                    'series_uid': rtstruct.series_instance_uid
                                })
        
        # Colors for different structure sets - use distinct colors for each observer
        colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'orange', 'purple', 'lime', 'pink']
        
        # Load ALL selected ROI masks upfront (like a DICOM viewer)
        all_masks = []
        global_color_idx = 0
        
        for roi_name, mask_infos in all_rois.items():
            try:
                # Load ALL masks for this ROI from all structure sets
                if mask_infos:
                    for idx, mask_info in enumerate(mask_infos):
                        try:
                            mask = sitk.ReadImage(mask_info['path'])
                            mask_array = sitk.GetArrayFromImage(mask)
                            
                            # Label with structure set number if multiple
                            if len(mask_infos) > 1:
                                label = f"{roi_name} (SS{idx+1})"
                            else:
                                label = roi_name
                            
                            # Assign different color to each structure set
                            all_masks.append({
                                'array': mask_array,
                                'label': label,
                                'color': colors[global_color_idx % len(colors)],
                                'roi_name': roi_name
                            })
                            global_color_idx += 1
                            logger.info(f"Loaded mask for ROI: {label}")
                        except Exception as e:
                            logger.warning(f"Failed to load mask for {roi_name} from {mask_info['series_uid']}: {e}")
                
                # Check for STAPLE contour
                if include_staple:
                    patient_id = sanitize_for_path(image_series.study.patient.patient_id)
                    study_uid = sanitize_for_path(image_series.study.study_instance_uid)
                    series_uid = sanitize_for_path(image_series.series_instance_uid)
                    safe_roi_name = sanitize_for_path(roi_name)
                    staple_path = Path(settings.MEDIA_ROOT) / "nifti_files" / patient_id / study_uid / series_uid / "staple" / f"staple_{safe_roi_name}.nii.gz"
                    
                    if staple_path.exists():
                        try:
                            staple_mask = sitk.ReadImage(str(staple_path))
                            staple_array = sitk.GetArrayFromImage(staple_mask)
                            all_masks.append({
                                'array': staple_array,
                                'label': f'⭐ STAPLE {roi_name}',
                                'color': 'gold',  # Bright gold color to stand out
                                'roi_name': roi_name
                            })
                            logger.info(f"Loaded STAPLE contour for ROI: {roi_name}")
                        except Exception as e:
                            logger.warning(f"Failed to load STAPLE mask for {roi_name}: {e}")
                
            except Exception as e:
                logger.error(f"Error loading masks for ROI {roi_name}: {e}")
                continue
        
        if not all_masks:
            logger.warning("No masks loaded for visualization")
            return {}
        
        # Generate unique directory for this visualization session
        hash_input = f"{image_series_id}_{'_'.join(all_rois.keys())}_{time.time()}"
        file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:10]
        
        vis_dir = Path(settings.MEDIA_ROOT) / "visualizations" / f"session_{file_hash}"
        vis_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate CT slices with ALL ROI overlays (DICOM viewer style)
        slice_paths = []
        logger.info(f"Generating {total_slices} CT slices with {len(all_masks)} ROI overlays...")
        
        # Create legend elements once (reuse for all slices)
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=m['color'], alpha=0.3, label=m['label']) for m in all_masks]
        
        # Create figure once and reuse it (major performance improvement)
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        
        for slice_idx in range(total_slices):
            # Clear previous content
            ax.clear()
            
            # Display base CT image
            ax.imshow(normalized_image[slice_idx, :, :], cmap='gray', aspect='auto')
            
            # Overlay ALL ROI masks on this slice
            for mask in all_masks:
                mask_slice = mask['array'][slice_idx, :, :]
                if np.any(mask_slice > 0):
                    cmap = create_overlay_colormap(mask['color'], alpha=0.3)
                    ax.imshow(mask_slice, cmap=cmap, vmin=0, vmax=1, aspect='auto')
            
            # Title showing slice number
            ax.set_title(f"Slice {slice_idx + 1}/{total_slices}", fontsize=12, fontweight='bold')
            ax.axis('off')
            
            # Add legend (reuse elements)
            ax.legend(handles=legend_elements, loc='upper right', fontsize=7, framealpha=0.9)
            
            # Save slice with optimized settings
            slice_filename = f"slice_{slice_idx:04d}.png"
            slice_path = vis_dir / slice_filename
            plt.savefig(slice_path, dpi=80, bbox_inches='tight', facecolor='white', format='png')
            
            # Store relative path
            relative_slice_path = slice_path.relative_to(settings.MEDIA_ROOT)
            slice_paths.append(str(relative_slice_path))
            
            # Log progress every 20 slices
            if (slice_idx + 1) % 20 == 0:
                logger.info(f"Progress: {slice_idx + 1}/{total_slices} slices generated")
        
        # Close figure once at the end
        plt.close(fig)
        
        logger.info(f"Generated {total_slices} CT slices with all ROI overlays")
        
        # Create metadata for this visualization session
        metadata = {
            'total_slices': total_slices,
            'slice_paths': slice_paths,
            'rois': [{'label': m['label'], 'color': m['color'], 'roi_name': m['roi_name']} for m in all_masks],
            'window_center': window_center,
            'window_width': window_width,
            'image_series_id': image_series_id
        }
        
        # Save metadata
        metadata_path = vis_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Return single visualization result with all ROIs
        visualizations['combined'] = {
            'directory': str(vis_dir.relative_to(settings.MEDIA_ROOT)),
            'total_slices': total_slices,
            'slice_paths': slice_paths,
            'rois': metadata['rois']
        }
        
        return visualizations
        
    except Exception as e:
        logger.error(f"Error in visualize_patient_rois: {e}")
        raise


def sanitize_for_path(name: str) -> str:
    """Sanitize a string to be safe for use in file paths."""
    import re
    sanitized = re.sub(r'[^\w\-]', '_', str(name))
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized
