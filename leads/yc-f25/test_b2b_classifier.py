#!/usr/bin/env python3
"""
Quick test script for B2B classifier node.

Usage:
    python3 test_b2b_classifier.py
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from graph.nodes import B2BClassifier

def test_b2b_classifier():
    """Test B2B classifier with sample YC F25 companies."""

    classifier = B2BClassifier()

    test_cases = [
        {
            "name": "JSX Tool",
            "description": "AI-First In-Browser IDE for React Development",
            "industry": "ENGINEERING, PRODUCT AND DESIGN",
            "expected_b2b": True
        },
        {
            "name": "Item",
            "description": "The AI-Native CRM that works for you",
            "industry": "SALES",
            "expected_b2b": True
        },
        {
            "name": "Zephyr Fusion",
            "description": "Powering tomorrow's industrial revolution in space",
            "industry": "INDUSTRIALS",
            "expected_b2b": True  # Industrial space tech is typically B2B
        },
        {
            "name": "Consumer App Example",
            "description": "Social media app connecting users worldwide",
            "industry": "Consumer",
            "expected_b2b": False
        }
    ]

    print("=" * 80)
    print("B2B CLASSIFIER TEST")
    print("=" * 80)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"Description: {test['description']}")
        print(f"Industry: {test['industry']}")
        print(f"Expected: {'B2B' if test['expected_b2b'] else 'B2C'}")
        print("-" * 80)

        row = {
            "description": test["description"],
            "industry": test["industry"]
        }

        result, err = classifier(row)

        if err:
            print(f"ERROR: {err}")
            continue

        is_b2b = result.get("is_b2b")
        confidence = result.get("b2b_confidence", 0.0)
        reason = result.get("classification_reason", "")

        classification = "B2B" if is_b2b else "B2C"
        match = "PASS" if is_b2b == test["expected_b2b"] else "FAIL"

        print(f"Result: {classification} (confidence: {confidence:.2f})")
        print(f"Reason: {reason}")
        print(f"Test: {match}")

    print("\n" + "=" * 80)
    print("Tests completed!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_b2b_classifier()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
