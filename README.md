# 🚢 Marine Analytics Dashboard

Sistem dashboard analitik maritim berbasis **Streamlit** untuk pemantauan armada kapal, kualitas air, dan logistik operasional secara *real-time*.

## 🌟 Fitur Utama

### 1. 🏠 Dashboard Operasional
- **KPI Real-time**: Memantau status armada (Operating, Maintenance, Idle).
- **Statistik Order**: Melacak misi yang sedang berjalan, selesai, atau gagal.
- **Tinjauan Pendapatan**: (Hanya untuk Role Admin/Finance/Marcom) Grafik tren pendapatan bulanan.

### 2. 🗺️ Peta Pantauan Kapal (Vessel Map)
- **Pelacakan Posisi Terkini**: Menampilkan lokasi kapal secara *live* menggunakan peta interaktif.
- **Simulasi Riwayat Perjalanan**: Memutar ulang rute perjalanan kapal dengan animasi pergerakan.
- **Heatmap Status**: Visualisasi warna marker berdasarkan status kapal atau kecepatan.

### 3. 🔥 Peta Lingkungan (Environmental Heatmap)
- **Monitoring Kualitas Air**: Heatmap interaktif untuk Salinitas, Kekeruhan (Turbidity), Oksigen, dll.
- **Radar Chart**: Analisis kesehatan lingkungan di area tertentu.

### 4. 📈 Riwayat Sensor (Sensor History)
- **Grafik Telemetri**: Visualisasi data sensor dari *buoy* dalam rentang waktu tertentu.
- **Multi-Parameter**: Membandingkan beberapa parameter (misal: Pasang Surut vs Arus) dalam satu grafik.

### 5. 👥 Manajemen Klien & Laporan
- **Analisis Klien**: Ringkasan portfolio klien berdasarkan wilayah.
- **Audit Log**: Mencatat setiap perubahan data sensitif di sistem.

## 🛠️ Teknologi yang Digunakan

- **Frontend/Backend**: [Streamlit](https://streamlit.io/) (Python)
- **Visualisasi**: Plotly, Altair, Folium (Leaflet)
- **Database**: PostgreSQL
- **Optimasi**: `asyncio` untuk *data fetching* paralel & Caching agresif.

## 📂 Struktur Proyek

Proyek ini telah direfaktor menjadi struktur modular agar mudah dikembangkan:

```bash
Marine-Web/
├── dashboard/
│   ├── main.py              # Router Utama Aplikasi
│   ├── constants.py         # Definisi Role User
│   ├── page/                # Modul Halaman (UI)
│   │   ├── home.py          # Halaman Dashboard Utama
│   │   ├── analytics.py     # Halaman Analitik Performa
│   │   ├── environmental.py # Halaman Heatmap
│   │   ├── clients.py       # Halaman Daftar Klien
│   │   ├── settings.py      # Pengaturan Akun
│   │   ├── auth.py          # Halaman Login
│   │   └── audit.py         # Modal Audit Log
│   └── back/                # Logika Backend
│       ├── src/
│       │   ├── map.py       # Logika Peta Kapal
│       │   ├── utils.py     # Fungsi Utilitas Umum
│       │   └── ...
│       └── query/           # Koneksi & Query Database
└── database/                # Skema Database
```

## 🚀 Cara Menjalankan

1.  **Pastikan Python terinstall** (Disarankan Python 3.9+).
2.  **Install dependencies**:
    ```bash
    pip install -r dashboard/requirements.txt
    ```
3.  **Setup Environment Variables** (Buat file `.env` di folder `dashboard/`):
    ```env
    DB_USER=username_db
    DB_PASS=password_db
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=nama_db
    ```
4.  **Jalankan Aplikasi**:
    ```bash
    streamlit run dashboard/main.py
    ```

## 🔐 Akun Demo

Sistem menggunakan *Role-Based Access Control* (RBAC). Pastikan login menggunakan akun yang terdaftar di database:
- **Admin**: Akses penuh.
- **Operations**: Fokus pada Peta & Sensor.
- **Marcom/Finance**: Fokus pada Analitik Pendapatan & Klien.

---
*Dikembangkan oleh Tim Marine Analytics.*
