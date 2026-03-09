# Spatial Overlap Metrics

This is an open source application designed to provide a graphical user interface for computation of spatial overlap metrics between structures delineated in radiotherapy. This application is built using Django and provides users with a web interface to:
1. Upload a set of DICOM files with images and structureset files. 
2. Automatically processes the DICOM data to extract information on the regions of interest in the structureset files.
3. Converts the dicom structureset regions of interest into compressed nifti files.
4. Computes STAPLE contours from a set of contours. 
5. Computes spatial overlap metrics between arbitrary pair of contours as well as between the STAPLE contour.
6. Allows users to download the metrics for further downstream analysis.


