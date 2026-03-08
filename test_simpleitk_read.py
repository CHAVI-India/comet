#!/usr/bin/env python3
"""
Test script to verify SimpleITK can read DICOM series from our directory structure.
"""
import sys
import os
import SimpleITK as sitk

# Test directory
data_directory = '/mnt/share/spatial_overlap_metrics_app/dicom_files/MR_24_016425/1.2.840.113619.2.55.3.279720729.409.1740012168.305/1.2.840.113619.2.55.3.279720729.409.1740012168.494'

print(f"Testing directory: {data_directory}")
print(f"Directory exists: {os.path.exists(data_directory)}")
print(f"Is directory: {os.path.isdir(data_directory)}")

# List DICOM files
dcm_files = [f for f in os.listdir(data_directory) if f.endswith('.dcm')]
print(f"Number of .dcm files: {len(dcm_files)}")
if dcm_files:
    print(f"First file: {dcm_files[0]}")
    print(f"Last file: {dcm_files[-1]}")

print("\n" + "="*60)
print("Attempting to read DICOM series with SimpleITK...")
print("="*60)

# Read the original series. First obtain the series file names using the
# image series reader.
series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(data_directory)
print(f"\nFound {len(series_IDs)} series IDs:")
for sid in series_IDs:
    print(f"  - {sid}")

if not series_IDs:
    print('\nERROR: given directory does not contain a DICOM series that GDCM can recognize.')
    print('\nTrying alternative approach: reading files directly...')
    
    # Try reading individual files
    import pydicom
    first_file = os.path.join(data_directory, dcm_files[0])
    try:
        ds = pydicom.dcmread(first_file, stop_before_pixels=False)
        print(f"\nPydicom can read the file:")
        print(f"  Modality: {ds.Modality}")
        print(f"  SeriesInstanceUID: {ds.SeriesInstanceUID}")
        print(f"  SOPClassUID: {ds.SOPClassUID}")
        print(f"  Image size: {ds.Rows}x{ds.Columns}")
        
        # Check for required tags
        required_tags = [
            'ImagePositionPatient',
            'ImageOrientationPatient',
            'PixelSpacing',
            'SliceThickness',
            'SliceLocation'
        ]
        print(f"\nChecking for required DICOM tags:")
        for tag in required_tags:
            has_tag = hasattr(ds, tag)
            value = getattr(ds, tag, 'N/A') if has_tag else 'N/A'
            print(f"  {tag}: {has_tag} = {value}")
            
    except Exception as e:
        print(f"Error reading with pydicom: {e}")
    
    sys.exit(1)

# Get file names for the first series
series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(
    data_directory, series_IDs[0]
)
print(f"\nFound {len(series_file_names)} files for series {series_IDs[0]}")

if series_file_names:
    print(f"First file: {series_file_names[0]}")
    print(f"Last file: {series_file_names[-1]}")

    # Read the series
    series_reader = sitk.ImageSeriesReader()
    series_reader.SetFileNames(series_file_names)
    series_reader.MetaDataDictionaryArrayUpdateOn()
    series_reader.LoadPrivateTagsOn()
    
    print("\nReading image series...")
    image3D = series_reader.Execute()
    
    print(f"\nSuccess! Image loaded:")
    print(f"  Size: {image3D.GetSize()}")
    print(f"  Spacing: {image3D.GetSpacing()}")
    print(f"  Origin: {image3D.GetOrigin()}")
    print(f"  Direction: {image3D.GetDirection()}")
    
    sys.exit(0)
else:
    print("ERROR: No files found for series")
    sys.exit(1)
