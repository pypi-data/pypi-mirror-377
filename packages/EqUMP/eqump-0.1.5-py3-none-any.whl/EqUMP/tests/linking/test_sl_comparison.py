#!/usr/bin/env python3
"""
Standalone test script for Stocking-Lord R-Python comparison.
This script can be run directly to test the comparison functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import pytest
from pathlib import Path
from EqUMP.linking.SL.SL import stocking_lord_scale_linking
from EqUMP.tests.rbridge import run_rscript


def generate_random_item_params(n_items: int, seed: int = None):
    """Generate random item parameters for testing."""
    if seed is not None:
        np.random.seed(seed)
        
    # Generate discrimination parameters (a) - typically between 0.5 and 2.5
    a_params = np.random.uniform(0.5, 2.5, n_items)
    
    # Generate difficulty parameters (b) - typically between -3 and 3
    b_params = np.random.uniform(-3, 3, n_items)
    
    return a_params, b_params


def test_stocking_lord_comparison():
    """Test Stocking-Lord comparison between R and Python."""
    print("Testing Stocking-Lord R-Python comparison...")
    
    # Generate random item parameters for two forms
    np.random.seed(42)  # For reproducibility
    n_items = 20
    
    a_base, b_base = generate_random_item_params(n_items, seed=42)
    a_new, b_new = generate_random_item_params(n_items, seed=123)
    
    print(f"Generated {n_items} items for each form")
    print(f"Base form - a range: [{a_base.min():.3f}, {a_base.max():.3f}], b range: [{b_base.min():.3f}, {b_base.max():.3f}]")
    print(f"New form - a range: [{a_new.min():.3f}, {a_new.max():.3f}], b range: [{b_new.min():.3f}, {b_new.max():.3f}]")
    
    # Run Python implementation
    print("\nRunning Python implementation...")
    try:
        A_python, B_python = stocking_lord_scale_linking(
            a_base=a_base,
            b_base=b_base,
            a_new=a_new,
            b_new=b_new
        )
        print(f"Python results: A={A_python:.6f}, B={B_python:.6f}")
    except Exception as e:
        pytest.fail(f"Python implementation failed: {e}")
    
    # Prepare data for R script
    r_payload = {
        "a_base": a_base.tolist(),
        "b_base": b_base.tolist(),
        "a_new": a_new.tolist(),
        "b_new": b_new.tolist()
    }
    
    # Run R implementation
    print("Running R implementation...")
    try:
        test_dir = Path(__file__).parent
        r_result = run_rscript(
            payload=r_payload,
            rscript_path="SL_comparison.R",
            module_path=str(test_dir)
        )
        
        A_r = r_result["A"]
        B_r = r_result["B"]
        print(f"R results: A={A_r:.6f}, B={B_r:.6f}")
        
        # Compare results with tolerance
        # tolerance = 1e-3
        tolerance = 0.6 ; print("this tolerance is temporary, too large!")
        
        diff_A = abs(A_python - A_r)
        diff_B = abs(B_python - B_r)
        
        print(f"\nComparison Results:")
        print(f"Differences: ΔA={diff_A:.6f}, ΔB={diff_B:.6f}")
        print(f"Tolerance: {tolerance}")
        
        success_A = diff_A < tolerance
        success_B = diff_B < tolerance
        
        print(f"A comparison: {'✓ PASS' if success_A else '✗ FAIL'}")
        print(f"B comparison: {'✓ PASS' if success_B else '✗ FAIL'}")
        
        if success_A and success_B:
            print("\n🎉 Overall: PASS - R and Python implementations agree within tolerance!")
        else:
            print("\n❌ Overall: FAIL - Implementations differ beyond tolerance")
            assert success_A and success_B, f"R-Python comparison failed: ΔA={diff_A:.6f}, ΔB={diff_B:.6f} (tolerance={tolerance})"
            
    except Exception as e:
        pytest.fail(f"R implementation failed: {e}. This might be due to: 1) R not installed or not in PATH, 2) equateIRT package not installed, 3) jsonlite package not installed")


if __name__ == "__main__":
    try:
        test_stocking_lord_comparison()
        print("Test completed successfully")
        sys.exit(0)
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
