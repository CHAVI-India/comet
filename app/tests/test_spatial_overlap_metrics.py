"""
Test Suite for Spatial Overlap Metrics

This module contains comprehensive tests for all spatial overlap metrics
to ensure correctness of computations.
"""

import numpy as np
import unittest
from app.utils.spatial_overlap_metrics import (
    dice_similarity,
    jaccard_similarity,
    hausdorff_distance_95,
    mean_surface_distance,
    added_path_length,
    overcontouring_mean_distance_to_conformity,
    undercontouring_mean_distance_to_conformity,
    mean_distance_to_conformity,
    volume_overlap_error,
    variation_of_information,
    cosine_similarity,
    surface_dsc,
)


class TestBasicOverlapMetrics(unittest.TestCase):
    """Test basic overlap metrics: DSC, Jaccard, VOE"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create simple test volumes
        self.volume_size = (10, 10, 10)
        
        # Perfect overlap - identical volumes
        self.vol_identical_1 = np.zeros(self.volume_size, dtype=np.uint8)
        self.vol_identical_1[3:7, 3:7, 3:7] = 255
        self.vol_identical_2 = self.vol_identical_1.copy()
        
        # Partial overlap - 50% overlap
        self.vol_partial_1 = np.zeros(self.volume_size, dtype=np.uint8)
        self.vol_partial_1[2:6, 2:6, 2:6] = 255
        self.vol_partial_2 = np.zeros(self.volume_size, dtype=np.uint8)
        self.vol_partial_2[4:8, 4:8, 4:8] = 255
        
        # No overlap
        self.vol_no_overlap_1 = np.zeros(self.volume_size, dtype=np.uint8)
        self.vol_no_overlap_1[1:3, 1:3, 1:3] = 255
        self.vol_no_overlap_2 = np.zeros(self.volume_size, dtype=np.uint8)
        self.vol_no_overlap_2[7:9, 7:9, 7:9] = 255
        
        # Empty volumes
        self.vol_empty_1 = np.zeros(self.volume_size, dtype=np.uint8)
        self.vol_empty_2 = np.zeros(self.volume_size, dtype=np.uint8)
    
    def test_dice_perfect_overlap(self):
        """Test DSC with perfect overlap (should be 1.0)"""
        dsc = dice_similarity(self.vol_identical_1, self.vol_identical_2)
        self.assertAlmostEqual(dsc, 1.0, places=6)
    
    def test_dice_no_overlap(self):
        """Test DSC with no overlap (should be 0.0)"""
        dsc = dice_similarity(self.vol_no_overlap_1, self.vol_no_overlap_2)
        self.assertAlmostEqual(dsc, 0.0, places=6)
    
    def test_dice_empty_volumes(self):
        """Test DSC with empty volumes (should be 1.0 by convention)"""
        dsc = dice_similarity(self.vol_empty_1, self.vol_empty_2)
        self.assertAlmostEqual(dsc, 1.0, places=6)
    
    def test_dice_partial_overlap(self):
        """Test DSC with partial overlap"""
        dsc = dice_similarity(self.vol_partial_1, self.vol_partial_2)
        # Calculate expected DSC
        intersection = np.sum((self.vol_partial_1 > 0) & (self.vol_partial_2 > 0))
        size1 = np.sum(self.vol_partial_1 > 0)
        size2 = np.sum(self.vol_partial_2 > 0)
        expected_dsc = (2.0 * intersection) / (size1 + size2)
        self.assertAlmostEqual(dsc, expected_dsc, places=6)
    
    def test_jaccard_perfect_overlap(self):
        """Test Jaccard with perfect overlap (should be 1.0)"""
        jaccard = jaccard_similarity(self.vol_identical_1, self.vol_identical_2)
        self.assertAlmostEqual(jaccard, 1.0, places=6)
    
    def test_jaccard_no_overlap(self):
        """Test Jaccard with no overlap (should be 0.0)"""
        jaccard = jaccard_similarity(self.vol_no_overlap_1, self.vol_no_overlap_2)
        self.assertAlmostEqual(jaccard, 0.0, places=6)
    
    def test_jaccard_empty_volumes(self):
        """Test Jaccard with empty volumes (should be 1.0 by convention)"""
        jaccard = jaccard_similarity(self.vol_empty_1, self.vol_empty_2)
        self.assertAlmostEqual(jaccard, 1.0, places=6)
    
    def test_jaccard_relationship_with_dice(self):
        """Test mathematical relationship: Jaccard = DSC / (2 - DSC)"""
        dsc = dice_similarity(self.vol_partial_1, self.vol_partial_2)
        jaccard = jaccard_similarity(self.vol_partial_1, self.vol_partial_2)
        expected_jaccard = dsc / (2 - dsc) if dsc < 2 else 1.0
        self.assertAlmostEqual(jaccard, expected_jaccard, places=6)
    
    def test_voe_perfect_overlap(self):
        """Test VOE with perfect overlap (should be 0.0)"""
        voe = volume_overlap_error(self.vol_identical_1, self.vol_identical_2)
        self.assertAlmostEqual(voe, 0.0, places=6)
    
    def test_voe_no_overlap(self):
        """Test VOE with no overlap (should be 1.0)"""
        voe = volume_overlap_error(self.vol_no_overlap_1, self.vol_no_overlap_2)
        self.assertAlmostEqual(voe, 1.0, places=6)
    
    def test_voe_relationship_with_jaccard(self):
        """Test relationship: VOE = 1 - Jaccard"""
        jaccard = jaccard_similarity(self.vol_partial_1, self.vol_partial_2)
        voe = volume_overlap_error(self.vol_partial_1, self.vol_partial_2)
        self.assertAlmostEqual(voe, 1.0 - jaccard, places=6)


class TestDistanceMetrics(unittest.TestCase):
    """Test distance-based metrics: HD95, MSD, APL"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create simple test volumes with known distances
        self.volume_size = (20, 20, 20)
        self.spacing = (1.0, 1.0, 1.0)
        
        # Two cubes separated by known distance
        self.vol_cube_1 = np.zeros(self.volume_size, dtype=np.uint8)
        self.vol_cube_1[5:10, 5:10, 5:10] = 255
        
        self.vol_cube_2 = np.zeros(self.volume_size, dtype=np.uint8)
        self.vol_cube_2[12:17, 5:10, 5:10] = 255  # Separated by 2 voxels in x
        
        # Identical cubes
        self.vol_identical = self.vol_cube_1.copy()
    
    def test_hausdorff_identical_volumes(self):
        """Test HD95 with identical volumes (should be 0.0)"""
        hd95 = hausdorff_distance_95(self.vol_cube_1, self.vol_identical)
        self.assertAlmostEqual(hd95, 0.0, places=6)
    
    def test_hausdorff_separated_volumes(self):
        """Test HD95 with separated volumes"""
        hd95 = hausdorff_distance_95(self.vol_cube_1, self.vol_cube_2)
        # The minimum distance between surfaces should be 2.0 (gap of 2 voxels)
        self.assertGreater(hd95, 0.0)
        self.assertLess(hd95, 10.0)  # Reasonable upper bound
    
    def test_msd_identical_volumes(self):
        """Test MSD with identical volumes (should be 0.0)"""
        msd = mean_surface_distance(self.vol_cube_1, self.vol_identical)
        self.assertAlmostEqual(msd, 0.0, places=6)
    
    def test_msd_separated_volumes(self):
        """Test MSD with separated volumes"""
        msd = mean_surface_distance(self.vol_cube_1, self.vol_cube_2)
        self.assertGreater(msd, 0.0)
        self.assertLess(msd, 10.0)
    
    def test_apl_identical_volumes(self):
        """Test APL with identical volumes (should be 0.0)"""
        apl = added_path_length(self.vol_cube_1, self.vol_identical, spacing=self.spacing)
        self.assertAlmostEqual(apl, 0.0, places=6)
    
    def test_apl_different_volumes(self):
        """Test APL with different volumes"""
        apl = added_path_length(self.vol_cube_1, self.vol_cube_2, spacing=self.spacing)
        # Should have non-zero added path length
        self.assertGreater(apl, 0.0)


class TestMDCMetrics(unittest.TestCase):
    """Test Mean Distance to Conformity metrics: OMDC, UMDC, MDC"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.volume_size = (15, 15, 15)
        self.spacing = (1.0, 1.0, 1.0)
        
        # Reference volume (larger)
        self.vol_reference = np.zeros(self.volume_size, dtype=np.uint8)
        self.vol_reference[3:12, 3:12, 3:12] = 255
        
        # Test volume (smaller - undercontouring)
        self.vol_under = np.zeros(self.volume_size, dtype=np.uint8)
        self.vol_under[5:10, 5:10, 5:10] = 255
        
        # Test volume (larger - overcontouring)
        self.vol_over = np.zeros(self.volume_size, dtype=np.uint8)
        self.vol_over[2:13, 2:13, 2:13] = 255
        
        # Identical volume
        self.vol_identical = self.vol_reference.copy()
    
    def test_umdc_identical_volumes(self):
        """Test UMDC with identical volumes (should be 0.0)"""
        umdc = undercontouring_mean_distance_to_conformity(
            self.vol_reference, self.vol_identical, spacing=self.spacing
        )
        self.assertAlmostEqual(umdc, 0.0, places=6)
    
    def test_umdc_undercontouring(self):
        """Test UMDC with undercontouring (test smaller than reference)"""
        umdc = undercontouring_mean_distance_to_conformity(
            self.vol_reference, self.vol_under, spacing=self.spacing
        )
        # Should be 0 because there's no undercontouring (reference is larger)
        self.assertAlmostEqual(umdc, 0.0, places=6)
    
    def test_omdc_identical_volumes(self):
        """Test OMDC with identical volumes (should be 0.0)"""
        omdc = overcontouring_mean_distance_to_conformity(
            self.vol_reference, self.vol_identical, spacing=self.spacing
        )
        self.assertAlmostEqual(omdc, 0.0, places=6)
    
    def test_omdc_overcontouring(self):
        """Test OMDC with overcontouring (test larger than reference)"""
        omdc = overcontouring_mean_distance_to_conformity(
            self.vol_reference, self.vol_over, spacing=self.spacing
        )
        # Should have non-zero overcontouring distance
        self.assertGreater(omdc, 0.0)
    
    def test_mdc_identical_volumes(self):
        """Test MDC with identical volumes (should be 0.0)"""
        mdc = mean_distance_to_conformity(
            self.vol_reference, self.vol_identical, spacing=self.spacing
        )
        self.assertAlmostEqual(mdc, 0.0, places=6)
    
    def test_mdc_relationship(self):
        """Test MDC is average of OMDC and UMDC"""
        omdc = overcontouring_mean_distance_to_conformity(
            self.vol_reference, self.vol_over, spacing=self.spacing
        )
        umdc = undercontouring_mean_distance_to_conformity(
            self.vol_reference, self.vol_over, spacing=self.spacing
        )
        mdc = mean_distance_to_conformity(
            self.vol_reference, self.vol_over, spacing=self.spacing
        )
        expected_mdc = (omdc + umdc) / 2.0
        self.assertAlmostEqual(mdc, expected_mdc, places=6)


class TestAdvancedMetrics(unittest.TestCase):
    """Test advanced metrics: VI, Cosine, Surface DSC"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.volume_size = (10, 10, 10)
        self.spacing = (1.0, 1.0, 1.0)
        
        # Identical volumes
        self.vol_1 = np.zeros(self.volume_size, dtype=np.uint8)
        self.vol_1[3:7, 3:7, 3:7] = 255
        self.vol_2 = self.vol_1.copy()
        
        # Different volumes
        self.vol_3 = np.zeros(self.volume_size, dtype=np.uint8)
        self.vol_3[4:8, 4:8, 4:8] = 255
    
    def test_cosine_identical_volumes(self):
        """Test Cosine similarity with identical volumes (should be 1.0)"""
        cosine = cosine_similarity(self.vol_1, self.vol_2)
        self.assertAlmostEqual(cosine, 1.0, places=6)
    
    def test_cosine_different_volumes(self):
        """Test Cosine similarity with different volumes"""
        cosine = cosine_similarity(self.vol_1, self.vol_3)
        # Should be less than 1.0 but greater than 0.0
        self.assertGreater(cosine, 0.0)
        self.assertLess(cosine, 1.0)
    
    def test_variation_of_information_identical(self):
        """Test VI with identical volumes (should be 0.0)"""
        vi = variation_of_information(self.vol_1, self.vol_2)
        self.assertAlmostEqual(vi, 0.0, places=6)
    
    def test_variation_of_information_different(self):
        """Test VI with different volumes (should be > 0.0)"""
        vi = variation_of_information(self.vol_1, self.vol_3)
        self.assertGreaterEqual(vi, 0.0)
    
    def test_surface_dsc_identical_volumes(self):
        """Test Surface DSC with identical volumes (should be 1.0)"""
        sdsc = surface_dsc(self.vol_1, self.vol_2, tau=3.0, spacing=self.spacing)
        self.assertAlmostEqual(sdsc, 1.0, places=6)
    
    def test_surface_dsc_different_volumes(self):
        """Test Surface DSC with different volumes"""
        sdsc = surface_dsc(self.vol_1, self.vol_3, tau=3.0, spacing=self.spacing)
        # Should be between 0 and 1
        self.assertGreaterEqual(sdsc, 0.0)
        self.assertLessEqual(sdsc, 1.0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.volume_size = (10, 10, 10)
        self.spacing = (1.0, 1.0, 1.0)
    
    def test_empty_volumes(self):
        """Test all metrics with empty volumes"""
        vol_empty_1 = np.zeros(self.volume_size, dtype=np.uint8)
        vol_empty_2 = np.zeros(self.volume_size, dtype=np.uint8)
        
        # DSC and Jaccard should be 1.0 for empty volumes
        self.assertAlmostEqual(dice_similarity(vol_empty_1, vol_empty_2), 1.0)
        self.assertAlmostEqual(jaccard_similarity(vol_empty_1, vol_empty_2), 1.0)
        
        # VOE should be 0.0 for empty volumes
        self.assertAlmostEqual(volume_overlap_error(vol_empty_1, vol_empty_2), 0.0)
        
        # Distance metrics should return inf for empty volumes
        self.assertTrue(np.isinf(hausdorff_distance_95(vol_empty_1, vol_empty_2)))
        self.assertTrue(np.isinf(mean_surface_distance(vol_empty_1, vol_empty_2)))
    
    def test_one_empty_volume(self):
        """Test metrics when one volume is empty"""
        vol_full = np.zeros(self.volume_size, dtype=np.uint8)
        vol_full[3:7, 3:7, 3:7] = 255
        vol_empty = np.zeros(self.volume_size, dtype=np.uint8)
        
        # DSC and Jaccard should be 0.0
        self.assertAlmostEqual(dice_similarity(vol_full, vol_empty), 0.0)
        self.assertAlmostEqual(jaccard_similarity(vol_full, vol_empty), 0.0)
        
        # VOE should be 1.0
        self.assertAlmostEqual(volume_overlap_error(vol_full, vol_empty), 1.0)
    
    def test_single_voxel_volumes(self):
        """Test metrics with single voxel volumes"""
        vol_1 = np.zeros(self.volume_size, dtype=np.uint8)
        vol_1[5, 5, 5] = 255
        
        vol_2 = np.zeros(self.volume_size, dtype=np.uint8)
        vol_2[5, 5, 5] = 255
        
        # Should handle single voxel correctly
        self.assertAlmostEqual(dice_similarity(vol_1, vol_2), 1.0)
        self.assertAlmostEqual(jaccard_similarity(vol_1, vol_2), 1.0)
    
    def test_different_intensity_values(self):
        """Test that metrics work with different intensity values"""
        vol_1 = np.zeros(self.volume_size, dtype=np.uint8)
        vol_1[3:7, 3:7, 3:7] = 255
        
        vol_2 = np.zeros(self.volume_size, dtype=np.uint8)
        vol_2[3:7, 3:7, 3:7] = 128  # Different intensity but same region
        
        # Should treat both as binary (> 0)
        self.assertAlmostEqual(dice_similarity(vol_1, vol_2), 1.0)
        self.assertAlmostEqual(jaccard_similarity(vol_1, vol_2), 1.0)


class TestNumericalStability(unittest.TestCase):
    """Test numerical stability and precision"""
    
    def test_symmetry_dice(self):
        """Test that DSC(A, B) = DSC(B, A)"""
        vol_1 = np.random.randint(0, 2, (10, 10, 10), dtype=np.uint8) * 255
        vol_2 = np.random.randint(0, 2, (10, 10, 10), dtype=np.uint8) * 255
        
        dsc_1 = dice_similarity(vol_1, vol_2)
        dsc_2 = dice_similarity(vol_2, vol_1)
        self.assertAlmostEqual(dsc_1, dsc_2, places=10)
    
    def test_symmetry_jaccard(self):
        """Test that Jaccard(A, B) = Jaccard(B, A)"""
        vol_1 = np.random.randint(0, 2, (10, 10, 10), dtype=np.uint8) * 255
        vol_2 = np.random.randint(0, 2, (10, 10, 10), dtype=np.uint8) * 255
        
        jaccard_1 = jaccard_similarity(vol_1, vol_2)
        jaccard_2 = jaccard_similarity(vol_2, vol_1)
        self.assertAlmostEqual(jaccard_1, jaccard_2, places=10)
    
    def test_metric_bounds(self):
        """Test that metrics stay within expected bounds"""
        vol_1 = np.random.randint(0, 2, (10, 10, 10), dtype=np.uint8) * 255
        vol_2 = np.random.randint(0, 2, (10, 10, 10), dtype=np.uint8) * 255
        
        # DSC, Jaccard, Cosine should be in [0, 1]
        dsc = dice_similarity(vol_1, vol_2)
        self.assertGreaterEqual(dsc, 0.0)
        self.assertLessEqual(dsc, 1.0)
        
        jaccard = jaccard_similarity(vol_1, vol_2)
        self.assertGreaterEqual(jaccard, 0.0)
        self.assertLessEqual(jaccard, 1.0)
        
        # VOE should be in [0, 1]
        voe = volume_overlap_error(vol_1, vol_2)
        self.assertGreaterEqual(voe, 0.0)
        self.assertLessEqual(voe, 1.0)


if __name__ == '__main__':
    unittest.main()
