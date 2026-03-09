# Spatial Overlap Metrics Test Suite - Quick Reference

## Quick Start

```bash
# Run all tests
cd /mnt/share/spatial_overlap_metrics_app
source venv/bin/activate
python run_metric_tests.py
```

## Test Suite Overview

| Metric | Test Cases | Total Tests | Status |
|--------|-----------|-------------|---------|
| DSC | 14 | 14 | ✅ |
| Jaccard | 14 | 14 | ✅ |
| VOE | 11 | 11 | ✅ |
| HD95 | 8 | 8 | ✅ |
| MSD | 8 | 8 | ✅ |
| APL | 2 | 2 | ✅ |
| OMDC | 4 | 4 | ✅ |
| UMDC | 4 | 4 | ✅ |
| MDC | 2 | 2 | ✅ |
| VI | 1 | 5 | ✅ |
| Cosine | 7 | 7 | ✅ |
| Surface DSC | 3 | 7 | ✅ |
| **TOTAL** | **14 Cases** | **81 Tests** | **✅ 100%** |

## Test Cases Summary

### Cubic Shapes (1-10)
1. **Identical Cubes** - Perfect overlap validation
2. **No Overlap** - Separated cubes
3. **Partial Overlap** - 50% overlap with exact calculations
4. **Undercontouring** - Smaller inside larger
5. **Overcontouring** - Larger around smaller
6. **Empty Volumes** - Edge case handling
7. **Single Voxel** - Minimal volume
8. **Different Intensities** - Binary threshold test
9. **Variation of Information** - VI metric tests
10. **Surface DSC** - Surface-based metric tests

### Spherical Shapes (11-14)
11. **Identical Spheres** - Perfect overlap with curves
12. **Concentric Spheres** - Radial geometry
13. **Offset Spheres** - Partial curved overlap
14. **Separated Spheres** - No curved overlap

## Expected Values Cheat Sheet

### Perfect Overlap
```
DSC = 1.0, Jaccard = 1.0, VOE = 0.0
HD95 = 0.0, MSD = 0.0, APL = 0.0
OMDC = 0.0, UMDC = 0.0, MDC = 0.0
Cosine = 1.0, Surface DSC = 1.0
```

### No Overlap
```
DSC = 0.0, Jaccard = 0.0, VOE = 1.0
HD95 > 0, MSD > 0
Cosine = 0.0, Surface DSC = 0.0
```

### Empty Volumes
```
DSC = 1.0, Jaccard = 1.0, VOE = 0.0
HD95 = inf, MSD = inf
All others = 0.0
```

## Mathematical Relationships

```python
# Jaccard-DSC Relationship
Jaccard = DSC / (2 - DSC)

# VOE-Jaccard Relationship
VOE = 1 - Jaccard

# MDC Relationship
MDC = (OMDC + UMDC) / 2

# Symmetry Properties
Metric(A, B) = Metric(B, A)  # for symmetric metrics
```

## Common Test Patterns

### Test Perfect Overlap
```python
def test_metric_perfect_overlap(self):
    vol1 = create_volume()
    vol2 = vol1.copy()
    result = metric_function(vol1, vol2)
    self.assertAlmostEqual(result, expected_value, places=6)
```

### Test No Overlap
```python
def test_metric_no_overlap(self):
    vol1 = create_volume_at_position_1()
    vol2 = create_volume_at_position_2()  # separated
    result = metric_function(vol1, vol2)
    self.assertAlmostEqual(result, 0.0, places=6)
```

### Test Bounds
```python
def test_metric_bounds(self):
    result = metric_function(vol1, vol2)
    self.assertGreaterEqual(result, 0.0)
    self.assertLessEqual(result, 1.0)
```

## Troubleshooting Quick Guide

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| DSC/Jaccard fail | Wrong formula | Check `2*intersection/(size1+size2)` |
| HD95/MSD fail | Using all voxels | Use surface voxels only |
| OMDC/UMDC fail | Euclidean distance | Use axis-aligned distance |
| VI fails | Import error | Check sklearn import |
| Surface DSC fails | Wrong tolerance | Verify τ parameter |
| All tests fail | Import error | Check Django setup |

## File Locations

```
app/tests/
├── test_metrics_mathematical_correctness.py  # Main tests (81 tests)
├── TEST_DOCUMENTATION.md                     # Detailed docs
├── README_TESTS.md                          # Medium detail
└── QUICK_REFERENCE.md                       # This file

run_metric_tests.py                          # Test runner
```

## Running Specific Tests

```bash
# All tests
python run_metric_tests.py

# Specific test case
python -m unittest app.tests.test_metrics_mathematical_correctness.TestCase11_IdenticalSpheres -v

# Specific metric
python -m unittest app.tests.test_metrics_mathematical_correctness.TestCase3_PartialOverlap_50Percent.test_dsc -v

# With Django
python manage.py test app.tests.test_metrics_mathematical_correctness
```

## Performance Benchmarks

- **Total execution**: ~0.2 seconds
- **Per test case**: <0.02 seconds
- **Memory usage**: <100 MB
- **Success rate**: 100%

## Key Formulas

### DSC
```
DSC = 2 × |A ∩ B| / (|A| + |B|)
```

### Jaccard
```
Jaccard = |A ∩ B| / |A ∪ B|
```

### HD95
```
HD95 = max(h₉₅(A→B), h₉₅(B→A))
```

### Surface DSC
```
Surface DSC = (|S_A ∩ N_τ(S_B)| + |S_B ∩ N_τ(S_A)|) / (|S_A| + |S_B|)
```

## Success Criteria

✅ All 81 tests pass  
✅ Execution time < 1 second  
✅ No warnings or errors  
✅ All metrics within expected bounds  

## Documentation Hierarchy

1. **QUICK_REFERENCE.md** (this file) - Fast lookup
2. **README_TESTS.md** - Medium detail, test case descriptions
3. **TEST_DOCUMENTATION.md** - Complete reference with formulas

---

**Last Updated**: March 9, 2026  
**Version**: 1.0  
**Status**: All tests passing ✅
