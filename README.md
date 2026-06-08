# 📸 STRET — Sistem Clustering Kepadatan Sesi Foto

> **Implementasi K-Means dan Fuzzy C-Means Clustering Kepadatan Sesi Foto pada Jasa Street Photography Sudut Kota Lama Berbasis Flask**

---

## 📋 Daftar Isi

- [Tentang Aplikasi](#tentang-aplikasi)
- [Prasyarat](#prasyarat)
- [Instalasi](#instalasi)
- [Cara Menjalankan](#cara-menjalankan)
- [Cara Menggunakan](#cara-menggunakan)
- [Struktur Project](#struktur-project)
- [Format Dataset](#format-dataset)
- [Algoritma & Evaluasi](#algoritma--evaluasi)

---

## 📌 Tentang Aplikasi

STRET adalah aplikasi web berbasis **Flask** yang digunakan untuk membantu manajemen Sudut Kota Lama dalam menganalisis kepadatan sesi foto menggunakan:

- **K-Means Clustering** — Hard clustering berbasis centroid
- **Fuzzy C-Means Clustering** — Soft clustering dengan derajat keanggotaan

Hasil clustering digunakan untuk menentukan **rekomendasi jumlah fotografer** yang bertugas:

| Label Cluster | Rekomendasi |
|---------------|-------------|
| 🔵 Sepi       | 1 Fotografer |
| 🟢 Normal     | 3 Fotografer |
| 🔴 Padat      | 5 Fotografer |

---

## ✅ Prasyarat

Pastikan perangkat Anda sudah terinstall:

- **Python 3.10 / 3.11** → [Download Python](https://www.python.org/downloads/)
- **pip** (sudah otomatis tersedia bersama Python)
- **Git** (opsional, untuk clone repository)

> Cek versi Python dengan perintah:
> ```powershell
> python --version
> ```

---

## 🔧 Instalasi

### Langkah 1 — Clone / Download Project

**Opsi A: Clone via Git**
```powershell
git clone https://github.com/shintothemars/STRET-Clustering-System.git
cd STRET-Clustering-System\STRET
```

**Opsi B: Download ZIP**
1. Klik tombol **Code → Download ZIP** di GitHub
2. Ekstrak ZIP ke folder pilihan Anda
3. Buka terminal dan masuk ke folder `STRET`

---

### Langkah 2 — (Opsional) Buat Virtual Environment

Sangat direkomendasikan agar library tidak bentrok dengan project lain.

```powershell
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment (Windows)
.\venv\Scripts\Activate.ps1
```

> Jika muncul error **"running scripts is disabled"**, jalankan dulu:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Lalu coba aktifkan lagi.

---

### Langkah 3 — Install Semua Library

```powershell
pip install -r requirements.txt
```

Tunggu hingga semua library selesai terdownload dan terinstall.

> ⏳ Proses ini memerlukan koneksi internet dan bisa memakan waktu **2–5 menit** tergantung kecepatan internet.

---

### Langkah 4 — Install scikit-fuzzy (untuk Fuzzy C-Means)

```powershell
pip install scikit-fuzzy
```

> Library ini diperlukan khusus untuk algoritma **Fuzzy C-Means**.

---

### Langkah 5 — Verifikasi Instalasi

Pastikan semua library terinstall dengan benar:

```powershell
python -c "import flask, pandas, sklearn, skfuzzy, matplotlib, seaborn, openpyxl; print('Semua library OK!')"
```

Jika berhasil, output akan menampilkan:
```
Semua library OK!
```

---

## ▶️ Cara Menjalankan

```powershell
python app.py
```

Buka browser dan akses:

```
http://127.0.0.1:5000
```

> Tekan `Ctrl + C` di terminal untuk menghentikan server.

---

## 🖥️ Cara Menggunakan

Ikuti alur berikut secara berurutan:

```
Upload Dataset
    ↓
Data Understanding
    ↓
Preprocessing
    ↓
K-Means Clustering
    ↓
Fuzzy C-Means
    ↓
Perbandingan Algoritma
    ↓
Visualisasi (8 Grafik)
    ↓
Download Hasil (.xlsx)
```

### Detail Setiap Langkah:

| No | Menu | Fungsi |
|----|------|--------|
| 1 | **Upload Dataset** | Upload file Excel (.xlsx) dataset sesi foto |
| 2 | **Data Understanding** | Lihat info dataset, missing value, statistik |
| 3 | **Preprocessing** | Label Encoding + MinMax Scaling otomatis |
| 4 | **K-Means** | Jalankan clustering, lihat evaluasi & distribusi |
| 5 | **Fuzzy C-Means** | Jalankan FCM, lihat FPC & nilai keanggotaan |
| 6 | **Perbandingan** | Bandingkan kedua algoritma, lihat yang terbaik |
| 7 | **Visualisasi** | 8 grafik analisis (histogram, scatter, elbow, dll.) |
| 8 | **Download** | Unduh hasil clustering Excel (3 sheet) |

---

## 📁 Struktur Project

```
STRET/
├── app.py                    ← Entry point Flask (semua routing)
├── clustering.py             ← Logika K-Means & Fuzzy C-Means
├── preprocessing.py          ← Preprocessing data otomatis
├── visualisasi.py            ← Pembuatan 8 grafik analisis
├── requirements.txt          ← Daftar library yang dibutuhkan
├── README.md                 ← File ini
│
├── uploads/                  ← Folder penyimpanan dataset yang diupload
├── outputs/                  ← Folder penyimpanan hasil download Excel
│
├── templates/
│   ├── base.html             ← Layout utama (sidebar + navbar)
│   ├── index.html            ← Dashboard
│   ├── upload.html           ← Halaman upload file
│   ├── data_understanding.html ← EDA & info dataset
│   ├── preprocessing.html    ← Hasil preprocessing
│   ├── kmeans.html           ← Hasil K-Means
│   ├── fcm.html              ← Hasil Fuzzy C-Means
│   ├── comparison.html       ← Perbandingan algoritma
│   ├── visualisasi.html      ← Dashboard 8 grafik
│   └── download.html         ← Halaman download
│
└── static/
    ├── css/style.css         ← Tampilan dark modern dashboard
    └── js/main.js            ← Animasi & interaksi frontend
```

---

## 📊 Format Dataset

Dataset harus berupa file **Excel (.xlsx)** dengan kolom berikut:

| Kolom | Tipe Data | Keterangan |
|-------|-----------|------------|
| `Tanggal` | Date | Tanggal pengambilan foto |
| `Hari` | String | Nama hari (Senin, Selasa, ..., Minggu) |
| `Lokasi` | String | Marba / Pringsewu / Distrik |
| `Jumlah Fotografer` | Integer | Jumlah fotografer yang bertugas |
| `Sesi Foto` | Integer | Jumlah sesi foto pada hari tersebut |
| `Weekend` | Integer | 0 = Bukan weekend, 1 = Weekend |
| `Hari Libur` | Integer | 0 = Bukan hari libur, 1 = Hari libur |

> ⚠️ **Penting:** Nama kolom harus **sama persis** (termasuk huruf kapital dan spasi) seperti di atas.

---

## 🤖 Algoritma & Evaluasi

### Fitur yang Digunakan untuk Clustering

| Fitur | Keterangan |
|-------|-----------|
| `Lokasi` | Label encoded (Marba=0, Pringsewu=1, Distrik=2) |
| `Weekend` | 0 atau 1 |
| `Hari Libur` | 0 atau 1 |
| `Sesi Foto` | Jumlah sesi foto (dinormalisasi MinMax) |

### Metrik Evaluasi

| Metrik | Semakin Baik |
|--------|-------------|
| **Silhouette Score** | Mendekati **1** |
| **Davies-Bouldin Index** | Mendekati **0** |
| **Calinski-Harabász Index** | Semakin **tinggi** |
| **Fuzzy Partition Coefficient** *(FCM only)* | Mendekati **1** |

---

## 📦 Library yang Digunakan

```
Flask==3.0.3           ← Web framework
pandas==2.2.2          ← Manipulasi data
numpy==1.26.4          ← Komputasi numerik
scikit-learn==1.5.0    ← K-Means & metrik evaluasi
scikit-fuzzy==0.4.2    ← Fuzzy C-Means
matplotlib==3.9.0      ← Visualisasi grafik
seaborn==0.13.2        ← Visualisasi statistik
openpyxl==3.1.4        ← Baca/tulis file Excel
Werkzeug==3.0.3        ← Utilitas Flask
scipy==1.13.1          ← Komputasi ilmiah
```

---

## ❓ Troubleshooting

### Error: `ModuleNotFoundError: No module named 'skfuzzy'`
```powershell
pip install scikit-fuzzy
```

### Error: `ModuleNotFoundError: No module named 'flask'`
```powershell
pip install flask
```

### Error: `running scripts is disabled on this system` (saat aktivasi venv)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port 5000 sudah dipakai
```powershell
# Jalankan di port lain, misalnya 8080
python -c "from app import app; app.run(port=8080, debug=True)"
```

---

## 🎓 Informasi Skripsi

- **Judul**: Implementasi K-Means dan Fuzzy C-Means Clustering Kepadatan Sesi Foto pada Jasa Street Photography Sudut Kota Lama Berbasis Flask
- **Program Studi**: Sistem Informasi
- **Objek Penelitian**: Sudut Kota Lama

---

> Dibuat dengan ❤️ untuk keperluan skripsi — 2024/2025
