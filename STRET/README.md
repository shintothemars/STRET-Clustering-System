# STRET — Sistem Clustering Kepadatan Sesi Foto

**Implementasi K-Means dan Fuzzy C-Means Clustering Kepadatan Sesi Foto
pada Jasa Street Photography Sudut Kota Lama Berbasis Flask**

---

## 📁 Struktur Project

```
STRET/
├── app.py                  # Entry point Flask (routing)
├── clustering.py           # Logika K-Means & Fuzzy C-Means
├── preprocessing.py        # Preprocessing: missing, duplikat, encoding, scaling
├── visualisasi.py          # Pembuatan chart (Matplotlib, Seaborn)
├── requirements.txt        # Dependensi Python
├── .gitignore
├── uploads/                # Folder upload dataset Excel
├── outputs/                # Folder output hasil download
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── data_understanding.html
│   ├── preprocessing.html
│   ├── kmeans.html
│   ├── fcm.html
│   ├── comparison.html
│   ├── visualisasi.html
│   └── download.html
└── static/
    ├── css/style.css
    └── js/main.js
```

---

## 🚀 Cara Instalasi & Menjalankan

### 1. Prasyarat
- Python 3.11 (pastikan sudah terinstall)
- pip (package manager Python)

### 2. Buka Terminal / PowerShell di VSCode
Tekan `Ctrl + ~` untuk membuka terminal di VSCode.

### 3. Masuk ke Folder Project
```powershell
cd "c:\Users\Lenovo LOQ\OneDrive\Documents\sKRIPSI\STRET"
```

### 4. (Opsional) Buat Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 5. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 6. Jalankan Aplikasi Flask
```powershell
python app.py
```

### 7. Buka Browser
Kunjungi: **http://127.0.0.1:5000**

---

## 📋 Alur Penggunaan

1. **Upload Dataset** → Upload file Excel (.xlsx) dengan kolom yang sesuai
2. **Data Understanding** → Lihat info dataset, missing value, statistik deskriptif
3. **Preprocessing** → Label encoding & MinMax scaling otomatis
4. **K-Means** → Jalankan K-Means, lihat evaluasi & distribusi cluster
5. **Fuzzy C-Means** → Jalankan FCM, lihat FPC & keanggotaan
6. **Perbandingan** → Bandingkan kedua algoritma, lihat pemenang
7. **Visualisasi** → 8 grafik analisis (histogram, scatter, elbow, dll.)
8. **Download** → Unduh hasil clustering dalam format Excel

---

## 📊 Format Dataset

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| Tanggal | Date | Tanggal pengambilan foto |
| Hari | String | Nama hari (Senin–Minggu) |
| Lokasi | String | Marba / Pringsewu / Distrik |
| Jumlah Fotografer | Integer | Jumlah fotografer aktif |
| Sesi Foto | Integer | Jumlah sesi foto |
| Weekend | Integer | 0 = Tidak, 1 = Ya |
| Hari Libur | Integer | 0 = Tidak, 1 = Ya |

---

## 🤖 Algoritma

### K-Means Clustering
- Hard clustering berbasis centroid
- Evaluasi: Silhouette Score, DBI, CHI

### Fuzzy C-Means (FCM)
- Soft clustering dengan derajat keanggotaan
- Parameter: m=2.0, maxiter=1000
- Evaluasi: Silhouette, DBI, CHI, **FPC**

### Fitur Clustering
- Lokasi (encoded)
- Weekend
- Hari Libur
- Sesi Foto

---

## 🏷️ Label & Rekomendasi

| Label | Rekomendasi Fotografer |
|-------|----------------------|
| Sepi | 1 Fotografer |
| Normal | 3 Fotografer |
| Padat | 5 Fotografer |

---

## 📦 Dependencies Utama

```
Flask==3.0.3
pandas==2.2.2
scikit-learn==1.5.0
scikit-fuzzy==0.4.2
matplotlib==3.9.0
seaborn==0.13.2
openpyxl==3.1.4
```

---

## 🎓 Informasi Skripsi

- **Judul**: Implementasi K-Means dan Fuzzy C-Means Clustering Kepadatan Sesi Foto pada Jasa Street Photography Sudut Kota Lama Berbasis Flask
- **Program Studi**: Sistem Informasi
- **Lokasi Penelitian**: Sudut Kota Lama
