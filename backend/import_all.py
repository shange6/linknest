"""Import all batch_*.jsonl files"""
import sys, glob, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())
from batch_import import import_batch

files = sorted(glob.glob("batch_*.jsonl"))
print(f"Found {len(files)} batch files\n")

total_imported = 0
for f in files:
    print(f"\n{'='*60}")
    print(f"IMPORTING: {f}")
    print(f"{'='*60}")
    imported = import_batch(f)
    total_imported += imported

print(f"\n{'='*60}")
print(f"ALL DONE. Total newly imported: {total_imported}")
print(f"{'='*60}")
