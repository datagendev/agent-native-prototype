#!/usr/bin/env python3
"""
Test script for SQLite integration.
"""
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from db import LeadDB
import csv

def test_database_integration():
    """Test database creation and CSV import."""
    print("=" * 60)
    print("Testing SQLite Integration")
    print("=" * 60)

    # Test 1: Create database
    print("\n[Test 1] Creating database...")
    lead_path = Path(__file__).parent / "leads" / "example-leads"
    db_path = lead_path / "table.db"

    # Remove existing DB for fresh test
    if db_path.exists():
        db_path.unlink()
        print(f"  Removed existing database: {db_path}")

    db = LeadDB(db_path)
    err = db.connect()
    if err:
        print(f"  ❌ Failed to connect: {err}")
        return False
    print("  ✓ Database connected")

    # Test 2: Initialize schema
    print("\n[Test 2] Initializing schema...")
    err = db.init_schema()
    if err:
        print(f"  ❌ Failed to init schema: {err}")
        return False
    print("  ✓ Schema initialized")

    # Test 3: Import CSV
    print("\n[Test 3] Importing CSV...")
    csv_path = lead_path / "table.csv"

    # Load CSV
    csv_rows = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    print(f"  Found {len(csv_rows)} rows in CSV")

    count, err = db.import_csv(csv_rows)
    if err:
        print(f"  ❌ Failed to import: {err}")
        return False
    print(f"  ✓ Imported {count} rows")

    # Test 4: Query rows
    print("\n[Test 4] Querying rows...")
    rows, err = db.get_rows(limit=3)
    if err:
        print(f"  ❌ Failed to query: {err}")
        return False

    print(f"  ✓ Retrieved {len(rows)} rows")
    for i, row in enumerate(rows):
        print(f"    Row {i+1}: _id={row['_id']}, keys={list(row.keys())[:5]}...")

    # Test 5: Update row
    print("\n[Test 5] Updating row...")
    test_row_id = rows[0]["_id"]
    updates = {"test_column": "test_value", "enriched_field": "enrichment_data"}
    err = db.update_row(test_row_id, updates, status="completed")
    if err:
        print(f"  ❌ Failed to update: {err}")
        return False
    print(f"  ✓ Updated row {test_row_id}")

    # Test 6: Verify update
    print("\n[Test 6] Verifying update...")
    rows, err = db.get_rows(limit=1)
    if err:
        print(f"  ❌ Failed to verify: {err}")
        return False

    updated_row = rows[0]
    if "test_column" in updated_row and updated_row["test_column"] == "test_value":
        print(f"  ✓ Update verified: test_column={updated_row['test_column']}")
    else:
        print(f"  ❌ Update verification failed")
        return False

    # Test 7: Export to CSV
    print("\n[Test 7] Exporting to CSV...")
    export_rows, err = db.export_to_csv()
    if err:
        print(f"  ❌ Failed to export: {err}")
        return False

    print(f"  ✓ Exported {len(export_rows)} rows")

    # Check internal columns are excluded
    if export_rows and "_id" not in export_rows[0]:
        print("  ✓ Internal columns (_id, _status) excluded from export")
    else:
        print("  ❌ Internal columns still present in export")
        return False

    # Test 8: Get stats
    print("\n[Test 8] Getting database stats...")
    stats, err = db.get_stats()
    if err:
        print(f"  ❌ Failed to get stats: {err}")
        return False

    print(f"  ✓ Stats retrieved:")
    print(f"    Total rows: {stats['total_rows']}")
    print(f"    Column count: {stats['column_count']}")
    print(f"    Status counts: {stats['status_counts']}")

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_database_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
