import os
import hashlib
from collections import Counter
from PIL import Image

DATASET_ROOT = r"C:\Users\Pawar\OneDrive\Desktop\Plant\New Plant Diseases Dataset(Augmented)"
train_dir = os.path.join(DATASET_ROOT, "train")
valid_dir = os.path.join(DATASET_ROOT, "valid")

print("=== RECURSIVE DATASET INSPECTION ===")
print(f"Dataset root: {DATASET_ROOT}")

train_entries = sorted(os.listdir(train_dir))
valid_entries = sorted(os.listdir(valid_dir))

train_classes = [d for d in train_entries if os.path.isdir(os.path.join(train_dir, d)) and d.lower().startswith(('apple', 'tomato'))]
valid_classes = [d for d in valid_entries if os.path.isdir(os.path.join(valid_dir, d)) and d.lower().startswith(('apple', 'tomato'))]

print(f"\nTrain classes identified ({len(train_classes)}):")
for c in train_classes:
    print(f"  - {c}")

print(f"\nValid classes identified ({len(valid_classes)}):")
for c in valid_classes:
    print(f"  - {c}")

missing_in_valid = set(train_classes) - set(valid_classes)
missing_in_train = set(valid_classes) - set(train_classes)

print(f"\nParity Check:")
if missing_in_valid:
    print(f"  [MISSING IN VALID]: {missing_in_valid}")
if missing_in_train:
    print(f"  [MISSING IN TRAIN]: {missing_in_train}")
if not missing_in_valid and not missing_in_train:
    print("  All classes match between train and valid.")

# Deep verification: Count, formats, corrupted check, duplicate check
def verify_folder(split_dir, classes):
    counts = {}
    corrupted = []
    duplicates = {}
    seen_hashes = {}
    formats = Counter()
    dims = Counter()
    
    for cls in classes:
        cls_path = os.path.join(split_dir, cls)
        files = [f for f in os.listdir(cls_path) if os.path.isfile(os.path.join(cls_path, f))]
        counts[cls] = len(files)
        
        for fname in files:
            fpath = os.path.join(cls_path, fname)
            # Integrity and corruption check
            try:
                with Image.open(fpath) as img:
                    img.verify() # Check integrity
                with Image.open(fpath) as img:
                    formats[img.format] += 1
                    dims[img.size] += 1
            except Exception as e:
                corrupted.append((fpath, str(e)))
                continue

            # Duplicate check via md5
            try:
                with open(fpath, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                if file_hash in seen_hashes:
                    duplicates.setdefault(file_hash, [seen_hashes[file_hash]]).append(fpath)
                else:
                    seen_hashes[file_hash] = fpath
            except Exception as e:
                pass
                
    return counts, corrupted, duplicates, formats, dims

print("\nVerifying Training Dataset images...")
train_counts, train_corrupt, train_dup, train_fmt, train_dims = verify_folder(train_dir, train_classes)

print("Verifying Validation Dataset images...")
valid_counts, valid_corrupt, valid_dup, valid_fmt, valid_dims = verify_folder(valid_dir, valid_classes)

print("\n=== SUMMARY TABLE ===")
all_classes = sorted(set(train_classes) | set(valid_classes))
print(f"{'Class Name':<35} | {'Train':>7} | {'Valid':>7} | {'Total':>7}")
print("-" * 62)
total_tr, total_val = 0, 0
for c in all_classes:
    tr = train_counts.get(c, 0)
    val = valid_counts.get(c, 0)
    total_tr += tr
    total_val += val
    print(f"{c:<35} | {tr:>7} | {val:>7} | {tr + val:>7}")
print("-" * 62)
print(f"{'TOTAL':<35} | {total_tr:>7} | {total_val:>7} | {total_tr + total_val:>7}")

print(f"\nCorrupted images in train: {len(train_corrupt)}")
if train_corrupt:
    for path, err in train_corrupt[:5]:
        print(f"  {path}: {err}")

print(f"Corrupted images in valid: {len(valid_corrupt)}")
if valid_corrupt:
    for path, err in valid_corrupt[:5]:
        print(f"  {path}: {err}")

print(f"\nDuplicate images in train: {len(train_dup)}")
print(f"Duplicate images in valid: {len(valid_dup)}")

print(f"\nImage Formats: Train={dict(train_fmt)}, Valid={dict(valid_fmt)}")
print(f"Image Dimensions: Train={dict(train_dims)}, Valid={dict(valid_dims)}")

