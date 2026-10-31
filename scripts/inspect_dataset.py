import os
import glob
from collections import Counter
from PIL import Image

DATASET_ROOT = r"C:\Users\Pawar\OneDrive\Desktop\Plant\New Plant Diseases Dataset(Augmented)"
train_dir = os.path.join(DATASET_ROOT, "train")
valid_dir = os.path.join(DATASET_ROOT, "valid")

print(f"Dataset Root: {DATASET_ROOT}")
print(f"Train exists: {os.path.isdir(train_dir)}")
print(f"Valid exists: {os.path.isdir(valid_dir)}")

all_train_dirs = sorted([d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))])
all_valid_dirs = sorted([d for d in os.listdir(valid_dir) if os.path.isdir(os.path.join(valid_dir, d))])

print(f"\nTotal folders in train: {len(all_train_dirs)}")
print(f"Total folders in valid: {len(all_valid_dirs)}")

# Identify Tomato and Potato folders
tomato_potato_train = [d for d in all_train_dirs if d.lower().startswith(('tomato', 'potato'))]
tomato_potato_valid = [d for d in all_valid_dirs if d.lower().startswith(('tomato', 'potato'))]

print(f"\nSelected Tomato/Potato classes in train ({len(tomato_potato_train)}):")
for d in tomato_potato_train:
    print(f" - {d}")

print(f"\nSelected Tomato/Potato classes in valid ({len(tomato_potato_valid)}):")
for d in tomato_potato_valid:
    print(f" - {d}")

# Check parity
if tomato_potato_train != tomato_potato_valid:
    print("\nWARNING: Train and Valid folders for Tomato/Potato do NOT match!")
    diff_tv = set(tomato_potato_train) - set(tomato_potato_valid)
    diff_vt = set(tomato_potato_valid) - set(tomato_potato_train)
    if diff_tv:
        print(f"In train but not valid: {diff_tv}")
    if diff_vt:
        print(f"In valid but not train: {diff_vt}")
else:
    print("\nParity confirmed: Train and Valid class folders match exactly.")

# Detailed image count and format inspection
train_counts = {}
valid_counts = {}
formats = Counter()
dimensions = Counter()

print("\n--- Image Counts and Formats Inspection ---")
for cls_name in tomato_potato_train:
    train_cls_dir = os.path.join(train_dir, cls_name)
    valid_cls_dir = os.path.join(valid_dir, cls_name)
    
    train_files = [f for f in os.listdir(train_cls_dir) if os.path.isfile(os.path.join(train_cls_dir, f))]
    valid_files = [f for f in os.listdir(valid_cls_dir) if os.path.isfile(os.path.join(valid_cls_dir, f))]
    
    train_counts[cls_name] = len(train_files)
    valid_counts[cls_name] = len(valid_files)
    
    # Sample check 5 files per class for format and size
    for f in train_files[:5]:
        fp = os.path.join(train_cls_dir, f)
        try:
            with Image.open(fp) as im:
                formats[im.format] += 1
                dimensions[im.size] += 1
        except Exception as e:
            print(f"Error opening image {fp}: {e}")

print(f"{'Class Name':<45} | {'Train':>7} | {'Valid':>7} | {'Total':>7}")
print("-" * 72)
total_train = 0
total_valid = 0
for cls_name in tomato_potato_train:
    tr = train_counts[cls_name]
    val = valid_counts[cls_name]
    tot = tr + val
    total_train += tr
    total_valid += val
    print(f"{cls_name:<45} | {tr:>7} | {val:>7} | {tot:>7}")

print("-" * 72)
print(f"{'TOTAL':<45} | {total_train:>7} | {total_valid:>7} | {total_train + total_valid:>7}")

print(f"\nImage formats detected: {dict(formats)}")
print(f"Image dimensions detected: {dict(dimensions)}")

