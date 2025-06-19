import cv2
import numpy as np

def apply_clahe(img_8bit):
    """
    Menerapkan Contrast Limited Adaptive Histogram Equalization (CLAHE).
    Asumsi input adalah citra grayscale 8-bit (np.uint8).
    """
    if img_8bit.dtype != np.uint8:
        raise ValueError("Input citra untuk CLAHE harus np.uint8.")
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced_img = clahe.apply(img_8bit)
    return enhanced_img

def apply_median_filter(img_8bit, ksize=5):
    """
    Menerapkan Median Filter untuk pengurangan derau.
    ksize harus ganjil.
    """
    if ksize % 2 == 0:
        raise ValueError("Ukuran kernel (ksize) untuk Median Filter harus ganjil.")
    denoised_img = cv2.medianBlur(img_8bit, ksize)
    return denoised_img

def apply_unsharp_mask(img_8bit, radius=5, amount=1.0):
    """
    Menerapkan Unsharp Masking untuk penajaman.
    radius: Ukuran blurring (misal, 5 berarti GaussianBlur dengan sigmaX=5).
    amount: Kekuatan penajaman.
    """
    blurred = cv2.GaussianBlur(img_8bit, (0,0), radius)
    # Ini adalah rumus umum: sharpened = original + (original - blurred) * amount
    # Atau, sharpened = original * (1 + amount) - blurred * amount
    sharpened = cv2.addWeighted(img_8bit, 1.0 + amount, blurred, -amount, 0)
    # Klip nilai piksel agar tetap dalam rentang 0-255
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
    return sharpened