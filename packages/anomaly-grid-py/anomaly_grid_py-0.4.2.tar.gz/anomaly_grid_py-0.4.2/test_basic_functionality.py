#!/usr/bin/env python3
"""
Basic functionality test for anomaly-grid-py
This file is run by CI to verify the package works correctly.
"""

import sys
import traceback

def test_import():
    """Test that the package can be imported."""
    try:
        import anomaly_grid_py
        print("[OK] Import successful")
        return True
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_basic_usage():
    """Test basic usage workflow."""
    try:
        import anomaly_grid_py
        
        # Create detector
        detector = anomaly_grid_py.AnomalyDetector(max_order=2)
        print("[OK] Detector creation successful")
        
        # Train on simple data
        training_data = [
            ['A', 'B'],
            ['A', 'B'],
            ['A', 'C'],
            ['A', 'C']
        ] * 10  # 40 sequences total
        
        detector.fit(training_data)
        print("[OK] Training successful")
        
        # Test prediction
        test_data = [
            ['A', 'B'],  # Normal
            ['X', 'Y']   # Anomalous
        ]
        
        scores = detector.predict_proba(test_data)
        print(f"[OK] Prediction successful: {scores}")
        
        # Test binary prediction
        predictions = detector.predict(test_data, threshold=0.5)
        print(f"[OK] Binary prediction successful: {predictions}")
        
        # Test metrics
        metrics = detector.get_performance_metrics()
        print(f"[OK] Metrics retrieval successful: {list(metrics.keys())}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Basic usage failed: {e}")
        traceback.print_exc()
        return False

def test_utilities():
    """Test utility functions."""
    try:
        from anomaly_grid_py import (
            train_test_split,
            generate_sequences,
            validate_sequences,
            calculate_sequence_stats
        )
        
        # Test sequence generation
        sequences, labels = generate_sequences(10, 3, ['A', 'B', 'C'])
        print(f"[OK] Sequence generation successful: {len(sequences)} sequences")
        
        # Test train/test split
        train, test = train_test_split(sequences, test_size=0.3, random_state=42)
        print(f"[OK] Train/test split successful: {len(train)} train, {len(test)} test")
        
        # Test validation
        validate_sequences(sequences, min_length=2)
        print("[OK] Sequence validation successful")
        
        # Test statistics
        stats = calculate_sequence_stats(sequences)
        print(f"[OK] Statistics calculation successful: {stats['n_sequences']} sequences")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Utilities test failed: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling."""
    try:
        import anomaly_grid_py
        
        # Test invalid parameter
        try:
            anomaly_grid_py.AnomalyDetector(max_order=0)
            print("[FAIL] Should have failed with max_order=0")
            return False
        except ValueError:
            print("[OK] Parameter validation working")
        
        # Test prediction before training
        detector = anomaly_grid_py.AnomalyDetector(max_order=2)
        try:
            detector.predict_proba([['A', 'B']])
            print("[FAIL] Should have failed when predicting before training")
            return False
        except ValueError:
            print("[OK] Unfitted detector error handling working")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error handling test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all basic functionality tests."""
    print("Running basic functionality tests for anomaly-grid-py")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_import),
        ("Basic Usage Test", test_basic_usage),
        ("Utilities Test", test_utilities),
        ("Error Handling Test", test_error_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"[FAIL] {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("ALL TESTS PASSED - Package is working correctly!")
        return 0
    else:
        print("SOME TESTS FAILED - Package has issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())