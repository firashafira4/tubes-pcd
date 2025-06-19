import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import os
# --- Konfigurasi Jalur Dataset dan Model ---

PATH_DATASET = os.path.join(os.getcwd(), 'data', 'chest_xray')

TRAIN_DIR = os.path.join(PATH_DATASET, 'train')
VAL_DIR = os.path.join(PATH_DATASET, 'val')
TEST_DIR = os.path.join(PATH_DATASET, 'test')

# Jalur untuk menyimpan model yang sudah dilatih
MODEL_SAVE_PATH = os.path.join(os.getcwd(), 'backend', 'models', 'lung_detection_model.h5')

# Buat folder models jika belum ada 
os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)

# --- Parameter Model ---
IMG_HEIGHT = 150
IMG_WIDTH = 150
BATCH_SIZE = 32
EPOCHS = 10 
# Jumlah kelas (Normal, Pneumonia)
NUM_CLASSES = 2

# --- 1. Memuat dan Mempersiapkan Data ---
print("Memuat data pelatihan...")
train_datagen = ImageDataGenerator(
    rescale=1./255, # Normalisasi piksel ke rentang 0-1
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

val_datagen = ImageDataGenerator(rescale=1./255) # Hanya normalisasi untuk validasi dan tes
test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='binary', # Untuk 2 kelas (Normal/Pneumonia)
    color_mode='grayscale' # Penting: Citra X-ray adalah grayscale
)

val_generator = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    color_mode='grayscale'
)

test_generator = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    color_mode='grayscale',
    shuffle=False # Jangan acak untuk pengujian
)
print("Data berhasil dimuat.")

# --- 2. Membangun Arsitektur Model CNN ---
print("Membangun model CNN...")
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH, 1)),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Flatten(),
    Dropout(0.5), # Mencegah overfitting
    Dense(512, activation='relu'),
    Dense(1, activation='sigmoid') # Sigmoid untuk binary classification (0 atau 1)
])

# --- 3. Mengkompilasi Model ---
print("Mengkompilasi model...")
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

model.summary()

# --- 4. Melatih Model ---
print(f"Memulai pelatihan model untuk {EPOCHS} epochs...")

# Callbacks untuk menyimpan model terbaik dan menghentikan pelatihan jika tidak ada peningkatan
checkpoint = ModelCheckpoint(
    MODEL_SAVE_PATH,
    monitor='val_accuracy',
    verbose=1,
    save_best_only=True,
    mode='max'
)
early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=3, # Hentikan jika loss tidak membaik setelah 3 epoch
    verbose=1,
    mode='min'
)

history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // BATCH_SIZE,
    epochs=EPOCHS,
    validation_data=val_generator,
    validation_steps=val_generator.samples // BATCH_SIZE,
    callbacks=[checkpoint, early_stopping]
)

print("Pelatihan model selesai.")

# --- 5. Evaluasi Model ---
print("\nMelakukan evaluasi model pada data tes...")
test_loss, test_accuracy = model.evaluate(test_generator, steps=test_generator.samples // BATCH_SIZE)
print(f"Akurasi Tes: {test_accuracy:.4f}")
print(f"Loss Tes: {test_loss:.4f}")

# --- 6. Visualisasi Hasil Pelatihan ---
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Accuracy')
plt.plot(history.history['val_accuracy'], label='Val Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

print(f"\nModel telah disimpan di: {MODEL_SAVE_PATH}")
print("Anda sekarang bisa menggunakan model ini di backend/model_loader.py.")