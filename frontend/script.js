document.addEventListener('DOMContentLoaded', () => {
    const imageUpload = document.getElementById('imageUpload');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const processButton = document.getElementById('processButton');
    
    // Elemen untuk 4 kartu gambar
    const originalImage = document.getElementById('originalImage');
    const originalImagePlaceholder = document.getElementById('originalImagePlaceholder');

    const enhancedOnlyImage = document.getElementById('enhancedOnlyImage');
    const enhancedOnlyImagePlaceholder = document.getElementById('enhancedOnlyImagePlaceholder');

    const processedWithDetectionsCanvas = document.getElementById('processedWithDetectionsCanvas');
    const processedWithDetectionsPlaceholder = document.getElementById('processedWithDetectionsPlaceholder');

    const originalWithDetectionsCanvas = document.getElementById('originalWithDetectionsCanvas'); // Ini akan menampilkan zoom deteksi
    const originalWithDetectionsPlaceholder = document.getElementById('originalWithDetectionsPlaceholder');
    
    const detectionList = document.getElementById('detectionList');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');

    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');
    const dashboardActionButtons = document.querySelectorAll('.dashboard-action-button');

    // Pastikan URL backend sesuai dengan yang Anda jalankan
    const BACKEND_URL = 'http://127.0.0.1:5000/upload_and_process';
    

    let selectedFile = null;

    // --- Fungsi Pembantu untuk Mengonversi Kebab-case ke CamelCase ---
    function kebabToCamelCase(kebabString) {
        return kebabString.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
    }

    // --- Fungsi untuk Mengelola Halaman ---
    function showPage(pageId) {
        pages.forEach(page => {
            page.classList.remove('active');
        });
        const targetPage = document.getElementById(pageId);
        if (targetPage) {
            targetPage.classList.add('active');
        } else {
            console.error(`Page with ID '${pageId}' not found.`);
        }

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (kebabToCamelCase(link.dataset.page) + 'Page' === pageId) {
                link.classList.add('active');
            }
        });
    }

    // Event Listeners untuk Navbar Links
    navLinks.forEach(link => {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            showPage(kebabToCamelCase(link.dataset.page) + 'Page');
        });
    });

    // Event Listeners untuk Dashboard Action Buttons
    dashboardActionButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            showPage(kebabToCamelCase(button.dataset.page) + 'Page');
        });
    });

    // Tampilkan Dashboard secara default saat pertama kali load
    showPage('dashboardPage');
    console.log("DOMContentLoaded fired. Attempting to show dashboardPage.");

    // --- Logika Upload dan Proses Gambar ---
    imageUpload.addEventListener('change', (event) => {
        selectedFile = event.target.files[0];
        if (selectedFile) {
            fileNameDisplay.textContent = selectedFile.name;
            processButton.disabled = false;
            hideErrorMessage();
            // Reset tampilan semua kartu
            hideAllImageDisplays();
            detectionList.innerHTML = '<li>Belum ada deteksi. Unggah dan proses citra untuk melihat hasilnya.</li>';
        } else {
            fileNameDisplay.textContent = 'Belum ada file dipilih';
            processButton.disabled = true;
        }
    });

    processButton.addEventListener('click', async () => {
        if (!selectedFile) {
            showErrorMessage('Pilih file citra terlebih dahulu.');
            return;
        }

        const formData = new FormData();
        formData.append('image', selectedFile);

        processButton.disabled = true;
        loadingSpinner.style.display = 'block';
        hideErrorMessage();
        detectionList.innerHTML = '<li>Memproses citra...</li>';
        hideAllImageDisplays(); // Sembunyikan semua tampilan saat loading

        try {
            const response = await fetch(BACKEND_URL, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Tampilkan Citra Asli
            originalImage.src = `data:image/png;base64,${data.original_image}`;
            originalImage.style.display = 'block';
            originalImagePlaceholder.style.display = 'none';

            // Tampilkan Perbaikan Citra (Enhanced Only)
            enhancedOnlyImage.src = `data:image/png;base64,${data.enhanced_only_image}`;
            enhancedOnlyImage.style.display = 'block';
            enhancedOnlyImagePlaceholder.style.display = 'none';

            // Tampilkan Perbaikan Citra & Deteksi (Canvas)
            const imgProcessedWithDetections = new Image();
            imgProcessedWithDetections.onload = () => {
                processedWithDetectionsCanvas.width = imgProcessedWithDetections.width;
                processedWithDetectionsCanvas.height = imgProcessedWithDetections.height;
                const ctx = processedWithDetectionsCanvas.getContext('2d');
                ctx.clearRect(0, 0, processedWithDetectionsCanvas.width, processedWithDetectionsCanvas.height);
                ctx.drawImage(imgProcessedWithDetections, 0, 0);
                
                processedWithDetectionsCanvas.style.display = 'block';
                processedWithDetectionsPlaceholder.style.display = 'none';
            };
            imgProcessedWithDetections.src = `data:image/png;base64,${data.processed_image}`;

            // --- Logika untuk Area Deteksi Zoom (NEW) ---
            const imgEnhancedForZoom = new Image();
            imgEnhancedForZoom.onload = () => {
                originalWithDetectionsCanvas.style.display = 'block'; // Aktifkan canvas
                originalWithDetectionsPlaceholder.style.display = 'none'; // Sembunyikan placeholder

                const ctx = originalWithDetectionsCanvas.getContext('2d');
                ctx.clearRect(0, 0, originalWithDetectionsCanvas.width, originalWithDetectionsCanvas.height);

                if (data.detections && data.detections.length > 0) {
                    // Ambil deteksi pertama (atau yang paling yakin)
                    const detection = data.detections[0]; 
                    const [x, y, w, h] = detection.bbox;
                    const label = detection.label;
                    const score = detection.score;

                    // Pastikan ukuran canvas sesuai dengan ukuran kartu (atau ukuran tetap yang diinginkan)
                    // Untuk zoom, kita akan menggambar bagian yang di-crop ke seluruh area canvas
                    // Atur lebar dan tinggi canvas berdasarkan ukuran gambar asli atau ukuran default yang diinginkan
                    // Agar zoom terlihat, kita bisa mengatur canvas ke ukuran tetap yang besar
                    originalWithDetectionsCanvas.width = imgEnhancedForZoom.width; // Gunakan lebar asli gambar enhanced
                    originalWithDetectionsCanvas.height = imgEnhancedForZoom.height; // Gunakan tinggi asli gambar enhanced

                    // Gambar bagian yang di-crop (bounding box) ke seluruh canvas
                    // ctx.drawImage(image, sx, sy, sWidth, sHeight, dx, dy, dWidth, dHeight);
                    // sx, sy, sWidth, sHeight: source rectangle (bagian yang di-crop dari imgEnhancedForZoom)
                    // dx, dy, dWidth, dHeight: destination rectangle (seluruh area canvas)
                    ctx.drawImage(imgEnhancedForZoom, x, y, w, h, 0, 0, originalWithDetectionsCanvas.width, originalWithDetectionsCanvas.height);

                    // Tambahkan label dan skor di atas gambar yang di-zoom
                    ctx.strokeStyle = '#FF0000'; // Merah
                    ctx.lineWidth = 2;
                    ctx.font = '24px Arial'; // Font lebih besar untuk zoom
                    ctx.fillStyle = '#FF0000';
                    ctx.fillText(`${label} (${(score * 100).toFixed(1)}%)`, 10, 30); // Posisi label di pojok kiri atas canvas
                    
                } else {
                    // Jika tidak ada deteksi, tampilkan pesan di canvas
                    originalWithDetectionsCanvas.width = 300; // Ukuran default jika tidak ada gambar
                    originalWithDetectionsCanvas.height = 200;
                    ctx.font = '16px Inter, sans-serif';
                    ctx.fillStyle = '#95a5a6';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText('Tidak ada abnormalitas terdeteksi', originalWithDetectionsCanvas.width / 2, originalWithDetectionsCanvas.height / 2);
                }
            };
            imgEnhancedForZoom.src = `data:image/png;base64,${data.enhanced_only_image}`; // Sumber gambar adalah yang sudah diperbaiki

            // Tampilkan hasil deteksi dalam daftar
            if (data.detections && data.detections.length > 0) {
                detectionList.innerHTML = '';
                data.detections.forEach(detection => {
                    const li = document.createElement('li');
                    li.textContent = `Deteksi: ${detection.label} (Confidence: ${(detection.score * 100).toFixed(1)}%)`;
                    detectionList.appendChild(li);
                });
            } else {
                detectionList.innerHTML = '<li>Tidak ada abnormalitas yang terdeteksi.</li>';
            }

        } catch (error) {
            console.error('Error:', error);
            showErrorMessage(`Terjadi kesalahan: ${error.message}.`);
            detectionList.innerHTML = '<li>Terjadi kesalahan saat memproses citra.</li>';
            hideAllImageDisplays(true); // Tampilkan placeholder jika error
        } finally {
            loadingSpinner.style.display = 'none';
            processButton.disabled = false;
        }
    });

    function showErrorMessage(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    function hideErrorMessage() {
        errorMessage.style.display = 'none';
    }

    function hideAllImageDisplays(showPlaceholders = false) {
        // Sembunyikan semua gambar/canvas
        originalImage.style.display = 'none';
        enhancedOnlyImage.style.display = 'none';
        processedWithDetectionsCanvas.style.display = 'none';
        originalWithDetectionsCanvas.style.display = 'none';

        // Tampilkan atau sembunyikan placeholder
        originalImagePlaceholder.style.display = showPlaceholders ? 'block' : 'none';
        enhancedOnlyImagePlaceholder.style.display = showPlaceholders ? 'block' : 'none';
        processedWithDetectionsPlaceholder.style.display = showPlaceholders ? 'block' : 'none';
        originalWithDetectionsPlaceholder.style.display = showPlaceholders ? 'block' : 'none';
    }
});
