SISTEM ANALISIS CITRA MEDIS PARU-PARU
Aplikasi berbasis web ini dirancang untuk membantu dalam perbaikan citra medis paru-paru dan deteksi awal potensi abnormalitas, khususnya pneumonia, menggunakan teknik pengolahan citra digital dan kecerdasan buatan (Deep Learning).

GAMBARAN UMUM
Dalam diagnosis medis modern, citra X-ray dan CT scan paru-paru sangat krusial. Namun, kualitas citra yang bervariasi (derau, kontras rendah) dan kompleksitas interpretasi manual dapat menghambat diagnosis yang cepat dan akurat. Proyek ini menghadirkan solusi komprehensif yang mengintegrasikan teknik Image Enhancement dengan model Deep Learning untuk memproses citra medis, meningkatkan kualitasnya, dan memberikan indikasi deteksi pneumonia melalui antarmuka web yang intuitif.

FITUR UTAMA
1.Antarmuka Web Interaktif: Dashboard sambutan, halaman analisis citra, dan panduan penggunaan yang mudah dinavigasi.
2.Unggah Citra Fleksibel: Mendukung unggah citra medis dalam format DICOM (.dcm), JPG (.jpg/.jpeg), dan PNG (.png).
3.Perbaikan Citra Otomatis (Image Enhancement):
Contrast Limited Adaptive Histogram Equalization (CLAHE): Untuk peningkatan kontras lokal.
Median Filter: Untuk pengurangan derau pada citra.
Unsharp Masking: Untuk penajaman detail gambar
4.Deteksi Abnormalitas Berbasis AI: Menggunakan model Convolutional Neural Network (CNN) yang dilatih untuk mengklasifikasikan citra X-ray paru-paru sebagai "Normal" atau "Pneumonia".
5.Visualisasi Hasil Komprehensif: Menampilkan 4 kartu gambar setelah proses:
Citra Asli
Perbaikan Citra (hanya hasil enhancement)
Perbaikan Citra & Deteksi (hasil enhancement dengan bounding box deteksi)
Area Deteksi Zoom (area terdeteksi di-crop dan di-zoom dari citra yang diperbaiki)
6.Informasi Deteksi Detail: Menampilkan label penyakit ("Pneumonia") dan tingkat kepercayaan (confidence score) dari model
7.Fitur Unduh Gambar: Memungkinkan pengguna mengunduh setiap citra hasil analisis (asli, diperbaiki, dengan deteksi, area zoom) ke perangkat lokal.
8.Responsif: Tampilan disesuaikan untuk berbagai ukuran layar (desktop, tablet, mobile).
