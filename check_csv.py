#!/usr/bin/env python3
"""
CSV Diagnostic Tool

This script helps diagnose issues with your CSV file format.
Run it to check if your CSV is properly formatted for the config generator.
"""

import sys
from pathlib import Path
import pandas as pd


def diagnose_csv(csv_path: str):
    """
    Diagnose CSV file format issues.

    Args:
        csv_path: Path to the CSV file to diagnose.
    """
    csv_file = Path(csv_path)

    print("=" * 70)
    print("CSV DIAGNOSTIC TOOL")
    print("=" * 70)
    print()

    # Check if file exists
    if not csv_file.exists():
        print(f"✗ File not found: {csv_path}")
        print()
        return False

    print(f"✓ File found: {csv_path}")
    print(f"  Size: {csv_file.stat().st_size:,} bytes")
    print()

    # Try reading with different separators
    print("Analyzing file format...")
    print()

    # Try tab-separated
    print("1. Trying TAB-separated format...")
    try:
        df_tab = pd.read_csv(csv_file, sep='\t', nrows=5)
        num_cols_tab = len(df_tab.columns)
        print(f"   Columns found: {num_cols_tab}")
        if num_cols_tab >= 2:
            print(f"   ✓ Valid! First columns: {list(df_tab.columns[:5])}")
        else:
            print(f"   ✗ Not enough columns")
        print()
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        print()
        df_tab = None
        num_cols_tab = 0

    # Try comma-separated
    print("2. Trying COMMA-separated format...")
    try:
        df_comma = pd.read_csv(csv_file, sep=',', nrows=5)
        num_cols_comma = len(df_comma.columns)
        print(f"   Columns found: {num_cols_comma}")
        if num_cols_comma >= 2:
            print(f"   ✓ Valid! First columns: {list(df_comma.columns[:5])}")
        else:
            print(f"   ✗ Not enough columns")
        print()
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        print()
        df_comma = None
        num_cols_comma = 0

    # Determine best format
    print("-" * 70)
    print()

    if num_cols_tab >= 2 and num_cols_tab >= num_cols_comma:
        print("RECOMMENDATION: File appears to be TAB-separated ✓")
        df = df_tab
        separator = "TAB"
    elif num_cols_comma >= 2:
        print("RECOMMENDATION: File appears to be COMMA-separated")
        print("⚠️  WARNING: The config generator requires TAB-separated format!")
        print()
        print("To convert:")
        print("  1. Open the file in Excel or Google Sheets")
        print("  2. Save As / Export as 'Tab Delimited Text' or '.tsv'")
        print()
        df = df_comma
        separator = "COMMA"
    else:
        print("✗ Could not determine file format")
        print()
        print("Please ensure:")
        print("  1. File is tab-separated (not comma-separated)")
        print("  2. First line contains column headers")
        print("  3. File is not corrupted")
        print()
        return False

    # Analyze structure
    print("-" * 70)
    print()
    print(f"STRUCTURE ANALYSIS ({separator}-separated):")
    print()
    print(f"Total columns: {len(df.columns)}")
    print()

    # Check for expected columns
    has_cat = False
    has_subcat = False
    audience_cols = []

    for i, col in enumerate(df.columns):
        if i == 0:
            has_cat = True
            print(f"Column 1 (Category):    '{col}'")
        elif i == 1:
            has_subcat = True
            print(f"Column 2 (Subcategory): '{col}'")
        else:
            if '_Audience%' in col or '_Index' in col or '_Minutes' in col:
                audience_name = col.rsplit('_', 1)[0]
                if audience_name not in [a for a, _ in audience_cols]:
                    audience_cols.append((audience_name, [col]))
                else:
                    for j, (name, cols) in enumerate(audience_cols):
                        if name == audience_name:
                            audience_cols[j][1].append(col)

    print()

    if has_cat and has_subcat:
        print("✓ Category and Subcategory columns found")
    else:
        print("✗ Missing Category or Subcategory columns")

    print()

    if audience_cols:
        print(f"✓ Found {len(audience_cols)} audience(s):")
        for audience_name, cols in audience_cols:
            print(f"  • {audience_name}")
            for col in cols:
                suffix = col.rsplit('_', 1)[1]
                print(f"    - {suffix}")
        print()

        # Check if all audiences have required columns
        print("Checking audience columns...")
        all_valid = True
        for audience_name, cols in audience_cols:
            has_percent = any('_Audience%' in c for c in cols)
            has_index = any('_Index' in c for c in cols)

            if has_percent and has_index:
                print(f"  ✓ {audience_name}: Has both Audience% and Index")
            else:
                print(f"  ✗ {audience_name}: Missing required columns")
                if not has_percent:
                    print(f"    Missing: {audience_name}_Audience%")
                if not has_index:
                    print(f"    Missing: {audience_name}_Index")
                all_valid = False
        print()

        if not all_valid:
            print("⚠️  Some audiences are missing required columns")
            print()
    else:
        print("✗ No audience columns found")
        print()
        print("Expected column naming pattern:")
        print("  {AudienceName}_Minutes")
        print("  {AudienceName}_Audience%")
        print("  {AudienceName}_Index")
        print()

    # Sample data
    print("-" * 70)
    print()
    print("SAMPLE DATA (first 3 rows):")
    print()
    if len(df) > 0:
        # Show only first few columns to avoid clutter
        display_cols = min(5, len(df.columns))
        print(df.iloc[:3, :display_cols].to_string(index=False))
        if len(df.columns) > display_cols:
            print(f"\n  ... and {len(df.columns) - display_cols} more columns")
    else:
        print("  (No data rows found)")

    print()
    print("-" * 70)
    print()

    # Final verdict
    if separator == "TAB" and has_cat and has_subcat and len(audience_cols) > 0:
        print("✓ CSV FORMAT IS VALID FOR CONFIG GENERATOR")
        print()
        print("You can now run:")
        print(f"  python generate_config.py {csv_path} persona1.md persona2.md")
        print()
        return True
    elif separator == "COMMA":
        print("⚠️  FILE NEEDS TO BE CONVERTED TO TAB-SEPARATED FORMAT")
        print()
        print("Steps to fix:")
        print("  1. Open file in Excel or Google Sheets")
        print("  2. File → Save As → Tab Delimited Text (.txt or .tsv)")
        print("  3. Rename to data.csv if needed")
        print("  4. Run this diagnostic again to verify")
        print()
        return False
    else:
        print("✗ CSV FORMAT HAS ISSUES")
        print()
        print("Please review the errors above and fix the file format.")
        print()
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_csv.py <csv_file>")
        print()
        print("Example:")
        print("  python check_csv.py data.csv")
        print()
        sys.exit(1)

    csv_path = sys.argv[1]
    success = diagnose_csv(csv_path)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
