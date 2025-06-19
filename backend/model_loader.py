# backend/model_loader.py
import tensorflow as tf
import numpy as np
import cv2


def load_detection_model(model_path):
    """
    Memuat model deteksi Deep Learning dari file.
    Ganti dengan logika pemuatan model Anda (Keras, PyTorch, dll.).
    """
    try:
        model = tf.keras.models.load_model(model_path)
        return model
    except Exception as e:
        print(f"Error loading model from {model_path}: {e}")
        return None

def predict_abnormalities(model, image_array):
    """
    Melakukan prediksi abnormalitas pada citra.
    Asumsi:
    - model menerima input citra yang sudah diproses (enhanced).
    - Model yang dilatih adalah model KLASIFIKASI (Normal/Pneumonia).
    - Fungsi ini akan mengembalikan bounding box dummy jika terdeteksi pneumonia.
    """
    if model is None:
        # Jika model tidak dimuat, kembalikan deteksi dummy acak seperti sebelumnya
        detected_objects = []
        if np.random.rand() > 0.5: # 50% chance to detect something
            original_h, original_w = image_array.shape[:2]
            # Bounding box dummy yang mencakup sebagian besar gambar
            dummy_x = int(original_w * 0.1)
            dummy_y = int(original_h * 0.1)
            dummy_w = int(original_w * 0.8)
            dummy_h = int(original_h * 0.8)
            dummy_label = "Abnormalitas (Contoh - Model Tidak Dimuat)"
            dummy_score = 0.75
            detected_objects.append({
                'bbox': [dummy_x, dummy_y, dummy_w, dummy_h],
                'label': dummy_label,
                'score': float(dummy_score)
            })
        return detected_objects

    # Contoh pre-processing untuk model Keras/TF yang dilatih dengan citra grayscale
    # train_model.py menggunakan IMG_HEIGHT = 150, IMG_WIDTH = 150
    IMG_HEIGHT, IMG_WIDTH = 150, 150 
    
    # Pastikan image_array adalah np.uint8 sebelum diresize
    if image_array.dtype != np.uint8:
        image_array = cv2.normalize(image_array, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

    input_image = cv2.resize(image_array, (IMG_WIDTH, IMG_HEIGHT))
    input_image = np.expand_dims(input_image, axis=-1) # Tambah dimensi channel (1 untuk grayscale)
    input_image = np.expand_dims(input_image, axis=0)  # Tambah dimensi batch (1 karena satu gambar)

    # Normalisasi jika model dilatih dengan nilai 0-1 (seperti di train_model.py)
    input_image = input_image / 255.0

    # Lakukan prediksi
    # Model klasifikasi akan mengembalikan probabilitas (misal, satu nilai antara 0 dan 1)
    predictions = model.predict(input_image)[0][0] # Ambil nilai probabilitas pertama dari output

    detected_objects = []
    # Tentukan threshold untuk memutuskan apakah itu pneumonia
    THRESHOLD = 0.5 

    # Jika probabilitas pneumonia di atas threshold
    if predictions > THRESHOLD:
        # Ini adalah model klasifikasi, jadi kita tidak punya bounding box yang akurat.
        # Kita akan membuat bounding box dummy yang mencakup sebagian besar gambar
        # untuk menunjukkan adanya deteksi abnormalitas (pneumonia).
        original_h, original_w = image_array.shape[:2]
        
        # Bounding box yang mencakup 80% dari tengah gambar
        bbox_x = int(original_w * 0.1)
        bbox_y = int(original_h * 0.1)
        bbox_w = int(original_w * 0.8)
        bbox_h = int(original_h * 0.8)

        # Label akan menjadi "Pneumonia" dengan skor probabilitas dari model
        label = "Pneumonia"
        score = predictions

        detected_objects.append({
            'bbox': [bbox_x, bbox_y, bbox_w, bbox_h],
            'label': label,
            'score': float(score)
        })
    else:
        # Jika probabilitas di bawah threshold, anggap normal
        # Tidak ada objek yang terdeteksi, list tetap kosong
        pass 

    return detected_objects
