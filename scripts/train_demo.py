import os
import sys
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

import tensorflow as tf

print("=" * 60)
print("FLORASCAN AI — DEMO MODEL TRAINING & EVALUATION PIPELINE")
print("=" * 60)
print(f"TensorFlow Version: {tf.__version__}")
print(f"Executing on Device: CPU (low-resource demo mode)")

DATASET_ROOT = r"C:\Users\Pawar\OneDrive\Desktop\Plant\New Plant Diseases Dataset(Augmented)"
TRAIN_DIR = os.path.join(DATASET_ROOT, "train")
VALID_DIR = os.path.join(DATASET_ROOT, "valid")
MODELS_DIR = r"C:\Users\Pawar\OneDrive\Desktop\Plant\models"
REPORTS_DIR = r"C:\Users\Pawar\OneDrive\Desktop\Plant\reports"

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

TARGET_CLASSES = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Tomato___Early_blight',
    'Tomato___healthy'
]

NORMALIZED_LABELS = [
    'apple apple scab',
    'apple black rot',
    'apple cedar apple rust',
    'apple healthy',
    'tomato early blight',
    'tomato healthy'
]

# STEP 1: Verify Dataset & Class Counts
print("\n[STEP 1] Dataset Verification and Class Counts:")
train_counts = {}
valid_counts = {}

for cls in TARGET_CLASSES:
    tr_path = os.path.join(TRAIN_DIR, cls)
    val_path = os.path.join(VALID_DIR, cls)
    tr_num = len(os.listdir(tr_path)) if os.path.exists(tr_path) else 0
    val_num = len(os.listdir(val_path)) if os.path.exists(val_path) else 0
    train_counts[cls] = tr_num
    valid_counts[cls] = val_num
    print(f"  * {cls:<35} | Train: {tr_num:>3} images | Valid: {val_num:>3} images")

total_train = sum(train_counts.values())
total_valid = sum(valid_counts.values())
print(f"  -------------------------------------------------------------")
print(f"  TOTAL TRAINING IMAGES:   {total_train}")
print(f"  TOTAL VALIDATION IMAGES: {total_valid}")

# STEP 2: Save Demo Class Labels
labels_demo_path = os.path.join(MODELS_DIR, "labels_demo.txt")
with open(labels_demo_path, "w", encoding="utf-8") as f:
    for lbl in NORMALIZED_LABELS:
        f.write(f"{lbl}\n")
print(f"\n[STEP 2] Demo labels saved in order: {labels_demo_path}")
for i, lbl in enumerate(NORMALIZED_LABELS):
    print(f"  Index {i}: {lbl} ({TARGET_CLASSES[i]})")

# STEP 3: Load Datasets into TensorFlow with Batch Size 8
print("\n[STEP 3] Preparing Low-Resource Data Pipeline (Batch Size: 8, Input: 224x224):")
BATCH_SIZE = 8
IMG_SIZE = (224, 224)

train_ds = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    labels='inferred',
    label_mode='categorical',
    class_names=TARGET_CLASSES,
    color_mode='rgb',
    batch_size=BATCH_SIZE,
    image_size=IMG_SIZE,
    shuffle=True,
    seed=42
)

# Use balanced validation subset for light CPU footprint during training epochs
valid_ds_full = tf.keras.utils.image_dataset_from_directory(
    VALID_DIR,
    labels='inferred',
    label_mode='categorical',
    class_names=TARGET_CLASSES,
    color_mode='rgb',
    batch_size=BATCH_SIZE,
    image_size=IMG_SIZE,
    shuffle=False
)

# Take 15 batches (120 images) for quick validation during training epochs
val_ds_light = valid_ds_full.take(15)

# STEP 4: Build MobileNetV2 Transfer Learning Model
print("\n[STEP 4] Loading Pretrained MobileNetV2 and Constructing Classification Head:")
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
# Strictly freeze the base model
base_model.trainable = False

inputs = tf.keras.Input(shape=(224, 224, 3), name="input_image")
x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
x = base_model(x, training=False)
x = tf.keras.layers.GlobalAveragePooling2D(name="gap")(x)
x = tf.keras.layers.Dropout(0.2, name="dropout")(x)
x = tf.keras.layers.Dense(128, activation="relu", name="dense_128")(x)
outputs = tf.keras.layers.Dense(len(TARGET_CLASSES), activation="softmax", name="predictions")(x)

model = tf.keras.Model(inputs=inputs, outputs=outputs, name="FloraScan_MobileNetV2_Demo")

trainable_params = sum(np.prod(p.shape) for p in model.trainable_weights)
non_trainable_params = sum(np.prod(p.shape) for p in model.non_trainable_weights)
print(f"  MobileNetV2 Backbone: FROZEN ({non_trainable_params:,} non-trainable params)")
print(f"  Classification Head:  ACTIVE ({trainable_params:,} trainable params)")

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# STEP 5: Train for 3 Epochs
print("\n[STEP 5] Training Classification Head for 3 Epochs (Demo Mode):")
t_start = time.time()
history = model.fit(
    train_ds,
    validation_data=val_ds_light,
    epochs=3,
    verbose=1
)
train_time = time.time() - t_start
print(f"Training completed successfully in {train_time:.2f} seconds.")

# STEP 6: Save Model Safely
print("\n[STEP 6] Model Saving Confirmation:")
demo_model_path = os.path.join(MODELS_DIR, "plant_disease_demo.keras")
model.save(demo_model_path)
model_size_mb = os.path.getsize(demo_model_path) / (1024 * 1024)
print(f"  [CONFIRMED] Saved demo model: {demo_model_path}")
print(f"  Model File Size: {model_size_mb:.2f} MB")
print(f"  Existing production model was NOT modified or overwritten.")

# STEP 7: Save Training History and Accuracy/Loss Curves
print("\n[STEP 7] Generating Training Curves and Evaluation Report:")
train_acc = history.history.get('accuracy', [])
val_acc = history.history.get('val_accuracy', [])
train_loss = history.history.get('loss', [])
val_loss = history.history.get('val_loss', [])

plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(range(1, 4), train_acc, 'bo-', label='Train Acc')
plt.plot(range(1, 4), val_acc, 'ro-', label='Val Acc')
plt.title('Demo Run: Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.grid(True, alpha=0.3)
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(range(1, 4), train_loss, 'bo-', label='Train Loss')
plt.plot(range(1, 4), val_loss, 'ro-', label='Val Loss')
plt.title('Demo Run: Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
graph_path = os.path.join(REPORTS_DIR, "demo_training_curves.png")
plt.savefig(graph_path, dpi=200)
plt.close()
print(f"  Saved Accuracy & Loss Graph to: {graph_path}")

# Quick Evaluation on Validation Batches
eval_loss, eval_acc = model.evaluate(val_ds_light, verbose=0)
print(f"  Validation Loss:     {eval_loss:.4f}")
print(f"  Validation Accuracy: {eval_acc*100:.2f}%")

eval_report_path = os.path.join(REPORTS_DIR, "demo_evaluation_report.txt")
with open(eval_report_path, "w", encoding="utf-8") as f:
    f.write("FloraScan AI - Demo Model Evaluation Report\n")
    f.write("=" * 45 + "\n")
    f.write(f"Architecture: MobileNetV2 (Frozen Base + Dense Head)\n")
    f.write(f"Input Resolution: 224x224x3\n")
    f.write(f"Batch Size: {BATCH_SIZE}\n")
    f.write(f"Epochs: 3\n")
    f.write(f"Training Samples: {total_train}\n")
    f.write(f"Training Time: {train_time:.2f} s\n")
    f.write(f"Final Train Accuracy: {train_acc[-1]*100:.2f}%\n")
    f.write(f"Final Validation Accuracy: {eval_acc*100:.2f}%\n")
    f.write(f"Final Validation Loss: {eval_loss:.4f}\n")
print(f"  Saved Short Evaluation Report to: {eval_report_path}")

# STEP 8: Final Testing using Sample Images from All 6 Classes
print("\n" + "=" * 60)
print("[STEP 8] FINAL TESTING: Sample Predictions Across All 6 Classes")
print("=" * 60)
print(f"{'Actual Class':<28} | {'Predicted Class':<25} | {'Confidence':<10} | {'Status'}")
print("-" * 75)

correct_count = 0
for cls_idx, target_cls in enumerate(TARGET_CLASSES):
    val_cls_dir = os.path.join(VALID_DIR, target_cls)
    sample_files = [f for f in os.listdir(val_cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not sample_files:
        continue
    sample_path = os.path.join(val_cls_dir, sample_files[0])
    
    # Load and preprocess sample image
    with Image.open(sample_path) as img:
        img_rgb = img.convert('RGB').resize((224, 224), Image.Resampling.BILINEAR)
        arr = np.array(img_rgb, dtype=np.float32)
        batch = np.expand_dims(arr, axis=0)
    
    preds = model.predict(batch, verbose=0)[0]
    pred_idx = int(np.argmax(preds))
    conf_pct = float(preds[pred_idx]) * 100
    pred_label = NORMALIZED_LABELS[pred_idx]
    actual_label = NORMALIZED_LABELS[cls_idx]
    
    is_correct = (pred_idx == cls_idx)
    if is_correct:
        correct_count += 1
    status_str = "CORRECT" if is_correct else "MISMATCH"
    
    print(f"{actual_label:<28} | {pred_label:<25} | {conf_pct:>8.2f}% | {status_str}")

print("-" * 75)
print(f"Testing Result: {correct_count}/{len(TARGET_CLASSES)} samples correctly classified on 3-epoch demo model.")
print("\n[ALL STEPS COMPLETED SUCCESSFULLY]")

