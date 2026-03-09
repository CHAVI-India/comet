# Spatial Overlap Metrics - Complete Test Documentation

## Table of Contents
1. [Overview](#overview)
2. [Test Suite Architecture](#test-suite-architecture)
3. [Cubic Shape Tests (Cases 1-10)](#cubic-shape-tests)
4. [Spherical Shape Tests (Cases 11-14)](#spherical-shape-tests)
5. [Metric Formulas and Validation](#metric-formulas-and-validation)
6. [Running the Tests](#running-the-tests)
7. [Interpreting Results](#interpreting-results)
8. [Adding New Tests](#adding-new-tests)

---

## Overview

### Purpose
This test suite validates the **mathematical correctness** of all 12 spatial overlap metrics used in medical image segmentation analysis. Unlike integration tests that verify system behavior, these tests ensure that each metric implementation produces mathematically accurate results.

### Key Features
- ✅ **Pre-calculated Expected Values**: All test cases have manually computed ground truth
- ✅ **Geometric Diversity**: Tests use both rectangular (cubes) and curved (spheres) shapes
- ✅ **Comprehensive Coverage**: All 12 metrics tested across 14 scenarios
- ✅ **Fast Execution**: Complete suite runs in ~0.2 seconds
- ✅ **Zero Dependencies**: No external validation libraries required

### Metrics Tested
1. **DSC** - Dice Similarity Coefficient
2. **Jaccard** - Jaccard Index (IoU)
3. **HD95** - 95th Percentile Hausdorff Distance
4. **MSD** - Mean Surface Distance
5. **APL** - Added Path Length
6. **OMDC** - Overcontouring Mean Distance to Conformity
7. **UMDC** - Undercontouring Mean Distance to Conformity
8. **MDC** - Mean Distance to Conformity
9. **VOE** - Volume Overlap Error
10. **VI** - Variation of Information
11. **Cosine** - Cosine Similarity
12. **Surface DSC** - Surface Dice Similarity Coefficient

---

## Test Suite Architecture

### File Structure
```
app/tests/
├── __init__.py
├── test_metrics_mathematical_correctness.py  # Main test file (81 tests)
├── TEST_DOCUMENTATION.md                     # This file
└── README_TESTS.md                          # Quick reference guide

run_metric_tests.py                          # Test runner script
```

### Test Organization
```python
TestCase1_IdenticalCubes           # 11 tests - Perfect overlap
TestCase2_NoOverlap                # 7 tests - No overlap
TestCase3_PartialOverlap_50Percent # 5 tests - Known overlap
TestCase4_ConcentricCubes_Under    # 5 tests - Undercontouring
TestCase5_ConcentricCubes_Over     # 5 tests - Overcontouring
TestCase6_EmptyVolumes             # 5 tests - Edge case
TestCase7_SingleVoxel              # 4 tests - Minimal volume
TestCase8_DifferentIntensities     # 3 tests - Binary threshold
TestCase9_VariationOfInformation   # 5 tests - VI metric
TestCase10_SurfaceDSC              # 7 tests - Surface metric
TestCase11_IdenticalSpheres        # 7 tests - Curved surfaces
TestCase12_ConcentricSpheres       # 5 tests - Radial geometry
TestCase13_OffsetSpheres           # 6 tests - Partial curved overlap
TestCase14_SeparatedSpheres        # 6 tests - No curved overlap
```

---

## Cubic Shape Tests

### Test Case 1: Identical Cubes
**Geometry**: Two 4×4×4 cubes at identical positions in 10×10×10 volume

**Volume Calculation**:
- Cube volume: 4³ = 64 voxels
- Intersection: 64 voxels (100% overlap)
- Union: 64 voxels

**Expected Results**:
```python
DSC = 2 × 64 / (64 + 64) = 1.0
Jaccard = 64 / 64 = 1.0
VOE = 1 - 1.0 = 0.0
HD95 = 0.0 (identical surfaces)
MSD = 0.0 (identical surfaces)
APL = 0.0 (no missing contour)
OMDC = 0.0 (no overcontouring)
UMDC = 0.0 (no undercontouring)
MDC = 0.0 (perfect conformity)
Cosine = 1.0 (identical vectors)
Surface DSC = 1.0 (perfect surface agreement)
```

**Tests**: 11 individual tests validating perfect overlap scenario

---

### Test Case 2: No Overlap
**Geometry**: Two 2×2×2 cubes separated in space
- Cube 1: [1:3, 1:3, 1:3]
- Cube 2: [7:9, 7:9, 7:9]

**Volume Calculation**:
- Each cube: 2³ = 8 voxels
- Intersection: 0 voxels
- Union: 16 voxels
- Separation: ~10.4 voxels (diagonal distance)

**Expected Results**:
```python
DSC = 2 × 0 / (8 + 8) = 0.0
Jaccard = 0 / 16 = 0.0
VOE = 1 - 0.0 = 1.0
Cosine = 0.0 (orthogonal vectors)
Surface DSC = 0.0 (no surface agreement)
HD95 > 5.0 (large distance)
MSD > 5.0 (large distance)
```

**Tests**: 7 individual tests validating no overlap scenario

---

### Test Case 3: Partial Overlap (50%)
**Geometry**: Two 4×4×4 cubes with 2×2×2 intersection
- Cube 1: [2:6, 2:6, 2:6] → 64 voxels
- Cube 2: [4:8, 4:8, 4:8] → 64 voxels
- Intersection: [4:6, 4:6, 4:6] → 8 voxels

**Volume Calculation**:
```
Intersection = 8 voxels
Union = 64 + 64 - 8 = 120 voxels
```

**Expected Results**:
```python
DSC = 2 × 8 / (64 + 64) = 16/128 = 0.125
Jaccard = 8 / 120 = 0.0666...
VOE = 1 - 0.0666... = 0.9333...
Cosine = 8 / √(64 × 64) = 8/64 = 0.125
```

**Mathematical Relationships Verified**:
- Jaccard = DSC / (2 - DSC) = 0.125 / 1.875 = 0.0666...
- VOE = 1 - Jaccard = 0.9333...

**Tests**: 5 individual tests including relationship validation

---

### Test Case 4: Concentric Cubes (Undercontouring)
**Geometry**: Smaller cube inside larger cube
- Reference (larger): [2:8, 2:8, 2:8] → 6³ = 216 voxels
- Test (smaller): [3:7, 3:7, 3:7] → 4³ = 64 voxels
- Gap: 1 voxel on each side

**Volume Calculation**:
```
Intersection = 64 voxels (all of test)
Union = 216 voxels (all of reference)
```

**Expected Results**:
```python
DSC = 2 × 64 / (216 + 64) = 128/280 = 0.457142...
Jaccard = 64 / 216 = 0.296296...
VOE = 1 - 0.296296... = 0.703703...
OMDC = 0.0 (test doesn't extend beyond reference)
UMDC = 1.0 (reference extends 1 voxel beyond test)
```

**Tests**: 5 individual tests validating undercontouring detection

---

### Test Case 5: Concentric Cubes (Overcontouring)
**Geometry**: Larger cube around smaller cube
- Reference (smaller): [3:7, 3:7, 3:7] → 4³ = 64 voxels
- Test (larger): [2:8, 2:8, 2:8] → 6³ = 216 voxels
- Gap: 1 voxel on each side

**Expected Results**:
```python
DSC = 2 × 64 / (64 + 216) = 128/280 = 0.457142...
Jaccard = 64 / 216 = 0.296296...
VOE = 0.703703...
OMDC = 1.0 (test extends 1 voxel beyond reference)
UMDC = 0.0 (reference doesn't extend beyond test)
```

**Tests**: 5 individual tests validating overcontouring detection

---

### Test Case 6: Empty Volumes
**Geometry**: Both volumes are completely empty (all zeros)

**Expected Results** (by convention):
```python
DSC = 1.0 (perfect agreement on emptiness)
Jaccard = 1.0 (perfect agreement)
VOE = 0.0 (no error)
HD95 = inf (no surfaces to compare)
MSD = inf (no surfaces to compare)
APL = 0.0 (no contours)
OMDC = 0.0 (no voxels)
UMDC = 0.0 (no voxels)
MDC = 0.0 (no voxels)
VI = 0.0 (no information difference)
```

**Tests**: 5 individual tests validating edge case handling

---

### Test Case 7: Single Voxel
**Geometry**: Both volumes contain exactly one voxel at [5,5,5]

**Expected Results**:
```python
DSC = 1.0 (perfect overlap)
Jaccard = 1.0 (perfect overlap)
VOE = 0.0 (no error)
Cosine = 1.0 (identical)
```

**Tests**: 4 individual tests validating minimal volume handling

---

### Test Case 8: Different Intensities
**Geometry**: Same 4×4×4 cube region but different intensity values
- Volume 1: intensity = 255
- Volume 2: intensity = 128

**Expected Results**:
```python
DSC = 1.0 (both treated as binary >0)
Jaccard = 1.0 (both treated as binary >0)
VOE = 0.0 (both treated as binary >0)
```

**Purpose**: Verify binary thresholding (>0) is applied correctly

**Tests**: 3 individual tests

---

### Test Case 9: Variation of Information
**Geometry**: Multiple scenarios for VI metric testing

**Scenarios**:
1. Identical volumes → VI = 0.0
2. Different volumes → VI > 0.0
3. Empty volumes → VI = 0.0

**Mathematical Formula**:
```
VI = H(X) + H(Y) - 2 × MI(X,Y)
where:
  H(X) = entropy of X
  H(Y) = entropy of Y
  MI(X,Y) = mutual information between X and Y
```

**Properties Verified**:
- Non-negativity: VI ≥ 0
- Symmetry: VI(A,B) = VI(B,A)
- Identity: VI(A,A) = 0

**Tests**: 5 individual tests

---

### Test Case 10: Surface DSC
**Geometry**: Various offset scenarios with tolerance τ=3mm

**Scenarios**:
1. Identical volumes → Surface DSC = 1.0
2. 1-voxel offset (within τ) → Surface DSC > 0.0
3. Separated volumes → Surface DSC = 0.0
4. Empty volumes → Surface DSC = 1.0
5. One empty → Surface DSC = 0.0

**Tolerance Effect**:
- Small τ (0.5mm) → Lower Surface DSC for offset
- Large τ (5mm) → Higher Surface DSC for offset

**Tests**: 7 individual tests including tolerance validation

---

## Spherical Shape Tests

### Test Case 11: Identical Spheres
**Geometry**: Two identical spheres with radius = 5 voxels
- Center: (10, 10, 10) in 20×20×20 volume
- Volume: ~523 voxels (4/3 × π × 5³)

**Creation Method**:
```python
distance = √((x-10)² + (y-10)² + (z-10)²)
sphere = (distance ≤ 5)
```

**Expected Results**:
```python
DSC = 1.0 (perfect overlap)
Jaccard = 1.0 (perfect overlap)
VOE = 0.0 (no error)
HD95 = 0.0 (identical curved surfaces)
MSD = 0.0 (identical curved surfaces)
Cosine = 1.0 (identical)
Surface DSC = 1.0 (perfect surface agreement)
```

**Purpose**: Validate metrics work correctly with curved surfaces

**Tests**: 7 individual tests

---

### Test Case 12: Concentric Spheres
**Geometry**: Two concentric spheres with different radii
- Inner sphere: radius = 3 → ~113 voxels
- Outer sphere: radius = 5 → ~523 voxels
- Radial gap: 2 voxels

**Volume Calculation**:
```
V_inner = 4/3 × π × 3³ ≈ 113 voxels
V_outer = 4/3 × π × 5³ ≈ 523 voxels
Intersection = V_inner (completely inside)
```

**Expected Results**:
```python
DSC = 2 × 113 / (113 + 523) = 226/636 ≈ 0.355
Jaccard = 113 / 523 ≈ 0.216
VOE = 1 - 0.216 ≈ 0.784
OMDC = 0.0 (inner doesn't extend beyond outer)
UMDC ≈ 2.0 (outer extends ~2 voxels beyond inner)
```

**Purpose**: Validate radial distance calculations and MDC metrics with curved surfaces

**Tests**: 5 individual tests

---

### Test Case 13: Offset Spheres
**Geometry**: Two spheres offset by known distance
- Sphere 1: radius = 4, center at (10, 10, 10)
- Sphere 2: radius = 4, center at (14, 10, 10)
- Offset: 4 voxels in x-direction
- Spheres touch with minimal overlap

**Expected Behavior**:
- 0 < DSC < 1 (partial overlap)
- 0 < Jaccard < 1 (partial overlap)
- HD95 > 0 (positive distance)
- MSD > 0 (positive distance)
- Surface DSC depends on tolerance τ

**Purpose**: Test partial overlap with curved surfaces and validate distance metrics

**Tests**: 6 individual tests

---

### Test Case 14: Separated Spheres
**Geometry**: Two spheres completely separated
- Sphere 1: radius = 3, center at (7, 7, 7)
- Sphere 2: radius = 3, center at (17, 17, 17)
- Distance between centers: √(10² + 10² + 10²) ≈ 17.3 voxels

**Expected Results**:
```python
DSC = 0.0 (no overlap)
Jaccard = 0.0 (no overlap)
VOE = 1.0 (complete error)
Cosine = 0.0 (no overlap)
HD95 > 10.0 (large distance)
MSD > 10.0 (large distance)
```

**Purpose**: Validate no-overlap scenario with curved surfaces

**Tests**: 6 individual tests

---

## Metric Formulas and Validation

### Overlap Metrics

#### Dice Similarity Coefficient (DSC)
```
DSC = 2 × |A ∩ B| / (|A| + |B|)

Range: [0, 1]
Interpretation: 1 = perfect overlap, 0 = no overlap
```

#### Jaccard Index
```
Jaccard = |A ∩ B| / |A ∪ B|

Range: [0, 1]
Relationship: Jaccard = DSC / (2 - DSC)
```

#### Volume Overlap Error (VOE)
```
VOE = 1 - Jaccard

Range: [0, 1]
Interpretation: 0 = perfect overlap, 1 = no overlap
```

### Distance Metrics

#### Hausdorff Distance 95% (HD95)
```
HD95 = max(h₉₅(A→B), h₉₅(B→A))

where h₉₅(A→B) = 95th percentile of distances from surface of A to B

Units: mm or voxels
Interpretation: Lower is better
```

**Implementation Note**: Uses surface voxels only (not all foreground voxels)

#### Mean Surface Distance (MSD)
```
MSD = (mean(d(A→B)) + mean(d(B→A))) / 2

where d(A→B) = distances from surface of A to B

Units: mm or voxels
Interpretation: Lower is better
```

**Implementation Note**: Uses surface voxels only

#### Added Path Length (APL)
```
APL = Σ (contour length in reference missing from test)

Units: mm
Interpretation: 0 = perfect agreement, higher = more missing contour
```

### Conformity Metrics

#### Mean Distance to Conformity (MDC)
```
MDC = (OMDC + UMDC) / 2

Units: mm
Interpretation: 0 = perfect conformity
```

#### Overcontouring MDC (OMDC)
```
OMDC = mean distance from (Test - Reference) to Reference boundary

Uses axis-aligned distance calculation
Units: mm
```

#### Undercontouring MDC (UMDC)
```
UMDC = mean distance from (Reference - Test) to Test boundary

Uses axis-aligned distance calculation
Units: mm
```

### Advanced Metrics

#### Variation of Information (VI)
```
VI = H(X) + H(Y) - 2 × MI(X,Y)

where:
  H(X) = -Σ p(x) log p(x)  (entropy)
  MI(X,Y) = Σ p(x,y) log(p(x,y)/(p(x)p(y)))  (mutual information)

Range: [0, ∞)
Properties: VI ≥ 0, VI(A,B) = VI(B,A), VI(A,A) = 0
```

#### Cosine Similarity
```
Cosine = (A · B) / (||A|| × ||B||)

Range: [0, 1] for binary volumes
Interpretation: 1 = identical, 0 = orthogonal
```

#### Surface DSC
```
Surface DSC = (|S_A ∩ N_τ(S_B)| + |S_B ∩ N_τ(S_A)|) / (|S_A| + |S_B|)

where:
  S_A, S_B = surface voxels
  N_τ(S) = voxels within tolerance τ of surface S

Range: [0, 1]
Parameter: τ (tolerance in mm, default = 3.0)
```

---

## Running the Tests

### Method 1: Using Test Runner Script
```bash
cd /mnt/share/spatial_overlap_metrics_app
source venv/bin/activate
python run_metric_tests.py
```

### Method 2: Using Django Test Framework
```bash
python manage.py test app.tests.test_metrics_mathematical_correctness
```

### Method 3: Using unittest Directly
```bash
# All tests
python -m unittest app.tests.test_metrics_mathematical_correctness -v

# Specific test case
python -m unittest app.tests.test_metrics_mathematical_correctness.TestCase11_IdenticalSpheres -v

# Specific test method
python -m unittest app.tests.test_metrics_mathematical_correctness.TestCase3_PartialOverlap_50Percent.test_dsc -v
```

### Expected Output
```
test_dsc (TestCase1_IdenticalCubes) ... ok
test_jaccard (TestCase1_IdenticalCubes) ... ok
...
----------------------------------------------------------------------
Ran 81 tests in 0.200s

OK

======================================================================
TEST SUMMARY
======================================================================
Total tests run: 81
Successes: 81
Failures: 0
Errors: 0
```

---

## Interpreting Results

### Success Indicators
✅ **All tests pass**: Implementation is mathematically correct  
✅ **Fast execution (<1s)**: No performance issues  
✅ **No warnings**: Clean implementation

### Failure Analysis

#### If DSC/Jaccard Tests Fail
**Possible Causes**:
- Incorrect intersection calculation
- Wrong formula implementation
- Binary thresholding not applied (>0)

**Debug Steps**:
1. Check intersection: `np.sum((vol1 > 0) & (vol2 > 0))`
2. Check sizes: `np.sum(vol1 > 0)`, `np.sum(vol2 > 0)`
3. Verify formula: `2 * intersection / (size1 + size2)`

#### If HD95/MSD Tests Fail
**Possible Causes**:
- Using all foreground voxels instead of surface voxels
- Incorrect distance transform
- Wrong percentile calculation

**Debug Steps**:
1. Verify surface extraction: `surface = binary & ~binary_erosion(binary)`
2. Check distance transform: `distance_transform_edt(~binary)`
3. Verify percentile: `np.percentile(distances, 95)`

#### If OMDC/UMDC Tests Fail
**Possible Causes**:
- Using Euclidean distance instead of axis-aligned
- Incorrect region identification
- Wrong direction (over vs under)

**Debug Steps**:
1. Check regions: `over = (test > 0) & ~(ref > 0)`
2. Verify axis-aligned search in `_calculate_axis_aligned_distance`
3. Confirm direction: OMDC measures test→ref, UMDC measures ref→test

#### If VI Tests Fail
**Possible Causes**:
- Incorrect entropy calculation
- Wrong mutual information formula
- Numerical precision issues

**Debug Steps**:
1. Verify sklearn import: `from sklearn.metrics import mutual_info_score`
2. Check formula: `H(X) + H(Y) - 2*MI(X,Y)`
3. Test with known values

#### If Surface DSC Tests Fail
**Possible Causes**:
- Incorrect contour extraction
- Wrong tolerance application
- Distance map calculation error

**Debug Steps**:
1. Verify SimpleITK usage: `sitk.BinaryContourImageFilter()`
2. Check distance map: `sitk.SignedMaurerDistanceMap()`
3. Verify tolerance: `contour * (dist <= tau)`

---

## Adding New Tests

### Template for New Test Case
```python
class TestCase15_YourScenario(unittest.TestCase):
    """
    Test Case 15: Brief description
    
    Geometry: Detailed description of volumes
    
    Expected Results:
    - DSC: X.XXX (explanation)
    - Jaccard: X.XXX (explanation)
    - ... (list all expected values)
    """
    
    def setUp(self):
        # Create test volumes
        self.vol1 = np.zeros((size, size, size), dtype=np.uint8)
        # ... define vol1
        
        self.vol2 = np.zeros((size, size, size), dtype=np.uint8)
        # ... define vol2
        
        self.spacing = (1.0, 1.0, 1.0)
        
        # Calculate expected values
        intersection = np.sum((self.vol1 > 0) & (self.vol2 > 0))
        size1 = np.sum(self.vol1 > 0)
        size2 = np.sum(self.vol2 > 0)
        
        self.expected = {
            'DSC': (2.0 * intersection) / (size1 + size2),
            'Jaccard': intersection / (size1 + size2 - intersection),
            # ... add all expected values
        }
    
    def test_dsc(self):
        result = dice_similarity(self.vol1, self.vol2)
        self.assertAlmostEqual(result, self.expected['DSC'], places=6,
                              msg=f"DSC: expected {self.expected['DSC']:.6f}, got {result:.6f}")
    
    # Add test methods for each metric
```

### Steps to Add New Test
1. **Define Geometry**: Create clear, simple geometric shapes
2. **Calculate Expected Values**: Manually compute all metrics
3. **Document**: Add detailed comments explaining the scenario
4. **Implement**: Write setUp() and test_*() methods
5. **Register**: Add to `run_metric_tests.py`
6. **Verify**: Run and ensure all tests pass
7. **Document**: Update this file with the new test case

### Best Practices
- Use simple, well-defined geometries
- Pre-calculate all expected values
- Add detailed docstrings
- Test edge cases
- Verify mathematical relationships
- Keep execution time low (<0.5s per test case)

---

## Troubleshooting

### Import Errors
```bash
# Ensure Django is configured
export DJANGO_SETTINGS_MODULE=spatialmetrics.settings
python manage.py test
```

### Numerical Precision Issues
- Adjust `places` parameter in `assertAlmostEqual()`
- Typical tolerance: 6 decimal places (1e-6)
- For spheres: may need 3 decimal places due to discretization

### Missing Dependencies
```bash
pip install numpy scipy scikit-learn SimpleITK
```

### Test Discovery Issues
```bash
# Ensure __init__.py exists
touch app/tests/__init__.py

# Run with explicit path
python -m unittest discover -s app/tests -p "test_*.py"
```

---

## Continuous Integration

### Pre-commit Checks
```bash
# Run before committing
python run_metric_tests.py
```

### CI/CD Pipeline
```yaml
# Example GitHub Actions
- name: Run Metric Tests
  run: |
    source venv/bin/activate
    python run_metric_tests.py
```

### Performance Benchmarks
- Total execution time should be < 1 second
- Individual test case should be < 0.1 seconds
- Memory usage should be < 100MB

---

## References

### Mathematical Foundations
- Dice, L. R. (1945). "Measures of the Amount of Ecologic Association Between Species"
- Jaccard, P. (1912). "The Distribution of the Flora in the Alpine Zone"
- Hausdorff, F. (1914). "Grundzüge der Mengenlehre"
- Nikolov et al. (2021). "Surface DSC for Medical Image Segmentation"

### Implementation References
- GitHub: CHAVI-India/draw-client-2.0
- GitHub: VendenIX/RTStructSegmentationAnalysis
- GitHub: pyplati/platipy

---

## Contact

For questions about the test suite or to report issues:
- Review test failures carefully
- Check this documentation
- Verify expected values manually
- Contact development team if needed

---

**Last Updated**: March 9, 2026  
**Test Suite Version**: 1.0  
**Total Tests**: 81  
**Success Rate**: 100%
