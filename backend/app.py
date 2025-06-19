import os
import base64
import numpy as np
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS
import pydicom
from PIL import Image

# Import modul pemrosesan citra dan model
from image_processing import apply_clahe, apply_median_filter, apply_unsharp_mask
from model_loader import load_detection_model, predict_abnormalities

app = Flask(__name__)
CORS(app) # Mengizinkan CORS dari frontend

# Direktori untuk menyimpan file yang diupload sementara
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Muat model deteksi saat aplikasi dimulai
try:
    MODEL_FILE_NAME = 'lung_detection_model.h5' # Nama file model Anda
    MODEL_PATH = os.path.join(app.root_path, 'models', MODEL_FILE_NAME)

    LUNG_DETECTION_MODEL = load_detection_model(MODEL_PATH)
    if LUNG_DETECTION_MODEL:
        print(f"Model deteksi paru-paru berhasil dimuat dari: {MODEL_PATH}")
    else:
        print(f"Model deteksi paru-paru GAGAL dimuat dari: {MODEL_PATH}. Fungsi deteksi abnormalitas tidak akan tersedia.")

except Exception as e:
    LUNG_DETECTION_MODEL = None
    print(f"Terjadi kesalahan saat memuat model: {e}")
    print("Fungsi deteksi abnormalitas tidak akan tersedia.")


def process_image(file_path):
    """Memproses citra (membaca, perbaikan, deteksi)"""
    img_original_display = None
    img_enhanced_only_display = None # NEW: Untuk citra yang hanya diperbaiki
    img_processed_with_detections_display = None # Untuk citra diperbaiki + deteksi
    detection_results = []

    try:
        # 1. Baca Citra (Mendukung DICOM, JPG, PNG)
        if file_path.endswith('.dcm'):
            dicom_data = pydicom.dcmread(file_path)
            pixel_array = dicom_data.pixel_array
            if pixel_array.dtype != np.uint8:
                min_val = pixel_array.min()
                max_val = pixel_array.max()
                if max_val - min_val > 0:
                    img = ((pixel_array - min_val) / (max_val - min_val) * 255).astype(np.uint8)
                else:
                    img = np.zeros_like(pixel_array, dtype=np.uint8)
            else:
                img = pixel_array
        else:
            img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise ValueError("File tidak dapat dibaca sebagai citra.")
            if img.dtype != np.uint8:
                img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

        img_original_display = img.copy() # Salin untuk tampilan asli

        # 2. Perbaikan Citra (Image Enhancement)
        if img.dtype != np.uint8:
            img_to_enhance = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        else:
            img_to_enhance = img.copy()

        img_enhanced = apply_clahe(img_to_enhance)
        img_enhanced = apply_median_filter(img_enhanced, ksize=5)

        # NEW: Simpan citra yang hanya diperbaiki sebelum ditambahkan deteksi
        img_enhanced_only_display = img_enhanced.copy() 
        
        # Salin citra yang sudah diperbaiki untuk kemudian ditambahkan deteksi
        img_processed_with_detections_display = img_enhanced.copy() 

        # 3. Deteksi Objek Abnormal (jika model tersedia)
        if LUNG_DETECTION_MODEL:
            detection_results = predict_abnormalities(LUNG_DETECTION_MODEL, img_enhanced)
            
            # Gambar bounding box pada citra yang sudah diperbaiki untuk tampilan "Perbaikan Citra & Deteksi"
            if img_processed_with_detections_display.dtype != np.uint8:
                img_processed_with_detections_display = cv2.normalize(img_processed_with_detections_display, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            
            img_processed_with_detections_display = cv2.cvtColor(img_processed_with_detections_display, cv2.COLOR_GRAY2BGR)
            
            for det in detection_results:
                if len(det.get('bbox', [])) == 4:
                    x, y, w, h = det['bbox']
                    label = det.get('label', 'Unknown')
                    score = det.get('score', 0.0)
                    
                    if x >= 0 and y >= 0 and w > 0 and h > 0:
                        color = (0, 255, 0) # Hijau
                        cv2.rectangle(img_processed_with_detections_display, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(img_processed_with_detections_display, f"{label}: {score:.2f}", (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                else:
                    app.logger.warning(f"Deteksi dengan bbox tidak valid: {det}")

        # Encode citra untuk dikirim ke frontend
        _, buffer_original = cv2.imencode('.png', img_original_display)
        _, buffer_enhanced_only = cv2.imencode('.png', img_enhanced_only_display) # NEW
        _, buffer_processed_with_detections = cv2.imencode('.png', img_processed_with_detections_display)

        img_original_b64 = base64.b64encode(buffer_original).decode('utf-8')
        img_enhanced_only_b64 = base64.b64encode(buffer_enhanced_only).decode('utf-8') # NEW
        img_processed_with_detections_b64 = base64.b64encode(buffer_processed_with_detections).decode('utf-8')

        return {
            'original_image': img_original_b64,
            'enhanced_only_image': img_enhanced_only_b64, # NEW
            'processed_image': img_processed_with_detections_b64, # Ini yang sudah ada deteksinya
            'detections': detection_results
        }

    except Exception as e:
        app.logger.error(f"Error processing image: {e}")
        return None

@app.route('/upload_and_process', methods=['POST'])
def upload_and_process():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        result = process_image(filepath)
        os.remove(filepath) # Hapus file setelah diproses

        if result:
            return jsonify(result), 200
        else:
            return jsonify({'error': 'Failed to process image'}), 500

if __name__ == '__main__':
    app.run(debug=True) # debug=True hanya untuk pengembangan
