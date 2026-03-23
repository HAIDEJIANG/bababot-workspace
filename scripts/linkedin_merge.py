#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Data Merge Script
"""

import pandas as pd
from pathlib import Path
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# File paths
DESKTOP = Path("C:/Users/Haide/Desktop/real business post")
BACKUP_FILE = DESKTOP / "LinkedIn_Business_Posts_Master_Table_backup_20260308_0040.csv"
CURRENT_FILE = DESKTOP / "LinkedIn_Business_Posts_Master_Table.csv"
OUTPUT_FILE = DESKTOP / "LinkedIn_Business_Posts_Master_Table.csv"

print("Step 1: Reading backup file...")
backup_df = pd.read_csv(BACKUP_FILE, encoding='utf-8')
print(f"   Backup: {len(backup_df)} records")

print("Step 2: Reading current file...")
try:
    current_df = pd.read_csv(CURRENT_FILE, encoding='utf-8')
    print(f"   Current: {len(current_df)} records")
except pd.errors.EmptyDataError:
    print("   Current file is empty, skipping...")
    current_df = pd.DataFrame()

print("Step 3: Merging data...")
merged_df = pd.concat([backup_df, current_df], ignore_index=True)
print(f"   Merged: {len(merged_df)} records")

print("Step 4: Removing duplicates (by source_url)...")
merged_df = merged_df.drop_duplicates(subset=['source_url'], keep='first')
print(f"   After dedup: {len(merged_df)} records")

print("Step 5: Sorting by date...")
sort_col = 'collected_at' if 'collected_at' in merged_df.columns else 'timestamp'
merged_df = merged_df.sort_values(sort_col, ascending=False)

print("Step 6: Saving file...")
merged_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
print(f"   Saved: {OUTPUT_FILE}")

print(f"\nDONE! Total {len(merged_df)} records")
