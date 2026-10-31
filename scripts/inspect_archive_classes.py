import zipfile

zip_path = r"C:\Users\Pawar\Downloads\archive.zip"
with zipfile.ZipFile(zip_path, 'r') as z:
    tr_counts = {}
    val_counts = {}
    for n in z.namelist():
        lower_n = n.lower()
        if not lower_n.endswith(('.jpg', '.jpeg', '.png')):
            continue
        parts = n.split('/')
        if len(parts) < 4:
            continue
        split_type = parts[2] # 'train' or 'valid'
        cls_name = parts[3]
        if not cls_name.lower().startswith(('tomato', 'potato')):
            continue
        if split_type == 'train':
            tr_counts[cls_name] = tr_counts.get(cls_name, 0) + 1
        elif split_type == 'valid':
            val_counts[cls_name] = val_counts.get(cls_name, 0) + 1

all_classes = sorted(set(list(tr_counts.keys()) + list(val_counts.keys())))
print(f"{'Class Name':<45} | {'Train':>7} | {'Valid':>7} | {'Total':>7}")
print("-" * 72)
total_tr, total_val = 0, 0
for cls_name in all_classes:
    tr = tr_counts.get(cls_name, 0)
    val = val_counts.get(cls_name, 0)
    total_tr += tr
    total_val += val
    print(f"{cls_name:<45} | {tr:>7} | {val:>7} | {tr + val:>7}")

print("-" * 72)
print(f"{'TOTAL':<45} | {total_tr:>7} | {total_val:>7} | {total_tr + total_val:>7}")

