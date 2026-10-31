import os
import random
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix

# Reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
os.environ['PYTHONHASHSEED'] = str(SEED)

import tensorflow as tf
tf.random.set_seed(SEED)

print(f"TensorFlow: {tf.__version__}")
print(f"GPUs available: {tf.config.list_physical_devices('GPU')}")

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

# Write labels_apple_tomato.txt
labels_path = os.path.join(MODELS_DIR, "labels_apple_tomato.txt")
with open(labels_path, "w", encoding="utf-8") as f:
    for label in NORMALIZED_LABELS:
        f.write(f"{label}\n")
print(f"Generated {labels_path} ({len(NORMALIZED_LABELS)} classes)")

IMG_SIZE = (224, 224)
BATCH_SIZE = 64

print("\n--- 1. Loading Training and Validation Datasets ---")
train_ds = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    labels='inferred',
    label_mode='categorical',
    class_names=TARGET_CLASSES,
    color_mode='rgb',
    batch_size=BATCH_SIZE,
    image_size=IMG_SIZE,
    shuffle=False
)

valid_ds = tf.keras.utils.image_dataset_from_directory(
    VALID_DIR,
    labels='inferred',
    label_mode='categorical',
    class_names=TARGET_CLASSES,
    color_mode='rgb',
    batch_size=BATCH_SIZE,
    image_size=IMG_SIZE,
    shuffle=False
)

# Compute class weights
class_counts = [2016, 1987, 1760, 2008, 1920, 1926]
total_train = sum(class_counts)
num_classes = len(TARGET_CLASSES)
class_weights = {i: total_train / (num_classes * count) for i, count in enumerate(class_counts)}
print(f"Class weights computed: {class_weights}")

# Load Base Pretrained MobileNetV2
print("\n--- 2. Instantiating MobileNetV2 Base ---")
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False

# Bottleneck Feature Extraction for Stage 1
print("\n--- 3. Precomputing Bottleneck Feature Embeddings ---")
print("Extracting features from Training set (11,617 images)...")
t0 = time.time()

train_features_list = []
train_labels_list = []
for batch_x, batch_y in train_ds:
    preprocessed_x = tf.keras.applications.mobilenet_v2.preprocess_input(batch_x)
    feats = base_model(preprocessed_x, training=False)
    pooled_feats = tf.keras.layers.GlobalAveragePooling2D()(feats)
    train_features_list.append(pooled_feats.numpy())
    train_labels_list.append(batch_y.numpy())

X_train_features = np.vstack(train_features_list)
y_train = np.vstack(train_labels_list)
print(f"Train features extracted: shape {X_train_features.shape} in {time.time()-t0:.1f}s")

print("Extracting features from Validation set (2,904 images)...")
val_features_list = []
val_labels_list = []
for batch_x, batch_y in valid_ds:
    preprocessed_x = tf.keras.applications.mobilenet_v2.preprocess_input(batch_x)
    feats = base_model(preprocessed_x, training=False)
    pooled_feats = tf.keras.layers.GlobalAveragePooling2D()(feats)
    val_features_list.append(pooled_feats.numpy())
    val_labels_list.append(batch_y.numpy())

X_val_features = np.vstack(val_features_list)
y_val = np.vstack(val_labels_list)
print(f"Validation features extracted: shape {X_val_features.shape}")

# STAGE 1: Train Dense Classification Head
print("\n=======================================================")
print("STAGE 1: Training Classification Head on Bottleneck Features")
print("=======================================================")

head_inputs = tf.keras.Input(shape=(1280,), name="features_input")
h = tf.keras.layers.Dropout(0.3, name="head_dropout_1")(head_inputs)
h = tf.keras.layers.Dense(256, activation="relu", name="head_dense_256")(h)
h = tf.keras.layers.BatchNormalization(name="head_bn")(h)
h = tf.keras.layers.Dropout(0.2, name="head_dropout_2")(h)
head_outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="predictions")(h)
head_model = tf.keras.Model(inputs=head_inputs, outputs=head_outputs, name="classification_head")

head_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

callbacks_head = [
    tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=4, restore_best_weights=True, verbose=1),
    tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-5, verbose=1)
]

t_head = time.time()
history_stage1 = head_model.fit(
    X_train_features,
    y_train,
    validation_data=(X_val_features, y_val),
    epochs=12,
    batch_size=64,
    class_weight=class_weights,
    callbacks=callbacks_head,
    verbose=1
)
print(f"Stage 1 completed in {time.time() - t_head:.1f}s.")

# STAGE 2: Construct Full End-to-End Model & Fine-Tune
print("\n=======================================================")
print("STAGE 2: End-to-End Fine-Tuning of Upper Layers")
print("=======================================================")

# Connect base and head
full_inputs = tf.keras.Input(shape=(224, 224, 3), name="input_image")
# Data augmentation applied during training
aug_layer = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.08),
    tf.keras.layers.RandomZoom(0.08),
], name="data_augmentation")(full_inputs)

preproc_layer = tf.keras.applications.mobilenet_v2.preprocess_input(aug_layer)
base_output = base_model(preproc_layer, training=False)
gap_layer = tf.keras.layers.GlobalAveragePooling2D(name="gap")(base_output)
final_output = head_model(gap_layer)

full_model = tf.keras.Model(inputs=full_inputs, outputs=final_output, name="FloraScan_MobileNetV2_AppleTomato")

# Unfreeze top 20 layers of base_model for fine-tuning
base_model.trainable = True
for layer in base_model.layers[:-20]:
    layer.trainable = False

trainable_weights = sum(np.prod(p.shape) for p in full_model.trainable_weights)
print(f"Total trainable parameters in fine-tuning: {trainable_weights:,}")

full_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Shuffle training dataset for fine-tuning
train_ds_shuffled = train_ds.shuffle(1000, seed=SEED).prefetch(tf.data.AUTOTUNE)
valid_ds_perf = valid_ds.prefetch(tf.data.AUTOTUNE)

best_keras_path = os.path.join(MODELS_DIR, "plant_disease_apple_tomato.keras")
callbacks_stage2 = [
    tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True, verbose=1),
    tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-6, verbose=1),
    tf.keras.callbacks.ModelCheckpoint(filepath=best_keras_path, monitor='val_accuracy', save_best_only=True, verbose=1)
]

t_fine = time.time()
history_stage2 = full_model.fit(
    train_ds_shuffled,
    validation_data=valid_ds_perf,
    epochs=4,
    class_weight=class_weights,
    callbacks=callbacks_stage2,
    verbose=1
)
print(f"Stage 2 fine-tuning completed in {time.time() - t_fine:.1f}s.")

# Save best model to disk
full_model.save(best_keras_path)
print(f"\nFinal Keras model saved: {best_keras_path} ({os.path.getsize(best_keras_path)/1024/1024:.2f} MB)")

# Build clean inference model (without training augmentation) for TFLite export
print("\n--- 4. Exporting to Quantized TFLite ---")
inf_input = tf.keras.Input(shape=(224, 224, 3), name="input_image")
inf_pre = tf.keras.applications.mobilenet_v2.preprocess_input(inf_input)
inf_base = base_model(inf_pre, training=False)
inf_gap = tf.keras.layers.GlobalAveragePooling2D()(inf_base)
inf_out = head_model(inf_gap)
inference_model = tf.keras.Model(inputs=inf_input, outputs=inf_out)

converter = tf.lite.TFLiteConverter.from_keras_model(inference_model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_bytes = converter.convert()

best_tflite_path = os.path.join(MODELS_DIR, "plant_disease_apple_tomato.tflite")
with open(best_tflite_path, "wb") as f:
    f.write(tflite_bytes)
print(f"Quantized TFLite model saved: {best_tflite_path} ({len(tflite_bytes)/1024/1024:.2f} MB)")

# Generate Training Curves
print("\n--- 5. Generating Training and Validation Curves ---")
train_acc = history_stage1.history.get('accuracy', []) + history_stage2.history.get('accuracy', [])
val_acc = history_stage1.history.get('val_accuracy', []) + history_stage2.history.get('val_accuracy', [])
train_loss = history_stage1.history.get('loss', []) + history_stage2.history.get('loss', [])
val_loss = history_stage1.history.get('val_loss', []) + history_stage2.history.get('val_loss', [])

plt.figure(figsize=(14, 5))
plt.subplot(1, 2, 1)
plt.plot(range(1, len(train_acc)+1), train_acc, 'bo-', label='Train Accuracy')
plt.plot(range(1, len(val_acc)+1), val_acc, 'ro-', label='Val Accuracy')
plt.axvline(x=len(history_stage1.history.get('accuracy', [])), color='gray', linestyle='--', label='Fine-Tuning Start')
plt.title('Training & Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.grid(True, alpha=0.3)
plt.legend(loc='lower right')

plt.subplot(1, 2, 2)
plt.plot(range(1, len(train_loss)+1), train_loss, 'bo-', label='Train Loss')
plt.plot(range(1, len(val_loss)+1), val_loss, 'ro-', label='Val Loss')
plt.axvline(x=len(history_stage1.history.get('loss', [])), color='gray', linestyle='--', label='Fine-Tuning Start')
plt.title('Training & Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.grid(True, alpha=0.3)
plt.legend(loc='upper right')

plt.tight_layout()
curves_path = os.path.join(REPORTS_DIR, "training_curves.png")
plt.savefig(curves_path, dpi=300)
plt.close()
print(f"Saved training curves plot: {curves_path}")

# Rigorous Model Evaluation
print("\n=======================================================")
print("6. FULL VALIDATION EVALUATION & METRICS")
print("=======================================================")

eval_loss, eval_acc = full_model.evaluate(valid_ds_perf, verbose=1)
print(f"\nFinal Validation Loss:     {eval_loss:.4f}")
print(f"Final Validation Accuracy: {eval_acc*100:.2f}%")

# Predictions for Classification Report and Confusion Matrix
y_pred_probs = []
for batch_x, _ in valid_ds:
    preds = inference_model.predict(batch_x, verbose=0)
    y_pred_probs.extend(preds)

y_pred = np.argmax(np.array(y_pred_probs), axis=1)
y_true = np.argmax(y_val, axis=1)

cls_report = classification_report(
    y_true,
    y_pred,
    target_names=TARGET_CLASSES,
    digits=4
)
print("\n--- Detailed Classification Report ---")
print(cls_report)

cm = confusion_matrix(y_true, y_pred)
print("--- Confusion Matrix ---")
print(cm)

# Plot Confusion Matrix
plt.figure(figsize=(9, 7))
plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Greens)
plt.title('Confusion Matrix: Apple & Tomato Diseases')
plt.colorbar()
tick_marks = np.arange(len(TARGET_CLASSES))
short_labels = [c.replace('___', '\n') for c in TARGET_CLASSES]
plt.xticks(tick_marks, short_labels, rotation=35, ha='right', fontsize=9)
plt.yticks(tick_marks, short_labels, fontsize=9)

thresh = cm.max() / 2.
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        plt.text(j, i, format(cm[i, j], 'd'),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black",
                 fontweight='bold')

plt.ylabel('Ground Truth')
plt.xlabel('Model Prediction')
plt.tight_layout()
cm_path = os.path.join(REPORTS_DIR, "confusion_matrix.png")
plt.savefig(cm_path, dpi=300)
plt.close()
print(f"Saved confusion matrix plot: {cm_path}")

# Measure Latency
print("\n--- 7. Measuring Single-Image Inference Latency ---")
sample_img = np.random.rand(1, 224, 224, 3).astype(np.float32)

# Keras latency
for _ in range(5): _ = inference_model.predict(sample_img, verbose=0)
k_times = []
for _ in range(30):
    t_s = time.perf_counter()
    _ = inference_model.predict(sample_img, verbose=0)
    k_times.append((time.perf_counter() - t_s) * 1000)
keras_ms = np.mean(k_times)

# TFLite latency
interpreter = tf.lite.Interpreter(model_path=best_tflite_path)
interpreter.allocate_tensors()
in_idx = interpreter.get_input_details()[0]['index']
out_idx = interpreter.get_output_details()[0]['index']

interpreter.set_tensor(in_idx, sample_img)
interpreter.invoke()
tf_times = []
for _ in range(30):
    t_s = time.perf_counter()
    interpreter.set_tensor(in_idx, sample_img)
    interpreter.invoke()
    _ = interpreter.get_tensor(out_idx)
    tf_times.append((time.perf_counter() - t_s) * 1000)
tflite_ms = np.mean(tf_times)

print(f"Keras CPU Latency:  {keras_ms:.2f} ms")
print(f"TFLite CPU Latency: {tflite_ms:.2f} ms")

# Save summary text file
summary_file = os.path.join(REPORTS_DIR, "evaluation_summary.txt")
with open(summary_file, "w", encoding="utf-8") as f:
    f.write(f"Validation Loss:     {eval_loss:.4f}\n")
    f.write(f"Validation Accuracy: {eval_acc*100:.2f}%\n")
    f.write(f"Keras CPU Latency:   {keras_ms:.2f} ms\n")
    f.write(f"TFLite CPU Latency:  {tflite_ms:.2f} ms\n\n")
    f.write("Classification Report:\n")
    f.write(cls_report)
    f.write("\n\nConfusion Matrix:\n")
    f.write(np.array2string(cm))

print(f"\nAll metrics and plots saved to {REPORTS_DIR}!")
print("TRAINING AND EVALUATION COMPLETE!")
