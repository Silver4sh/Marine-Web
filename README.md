# Proyek Marine-Web

Ekosistem aplikasi MarineOS untuk operasi dan analitik maritim.

## 📂 Struktur & Cara Jalan

### 1. 📊 Dasbor Streamlit (`/streamlit`)
**Pusat Operasi & Analitik Utama.**
*   **Fitur**: Analitik Lanjutan (Korelasi, AI, Prediksi), Modul Survei, UI Responsif.
*   **Run**: `streamlit run streamlit/main.py`

### 2. 🚀 Portal Klien (`/htmx`)
**Antarmuka Klien Ringan.**
*   **Stack**: FastAPI + HTMX.
*   **Run**: `uvicorn htmx.main:app --reload`

### 3. ⚙️ Backend API (`/django`)
**Manajemen Data Pusat.**
*   **Stack**: Django.
*   **Run**: `python django/manage.py runserver`

## 🛠️ Instalasi
1.  **Env**: Atur `.env` (`DB_USER`, `DB_PASS`, `DB_HOST`, `DB_NAME`).
2.  **Install**: `pip install -r requirements.txt`
3.  **DB**: Pastikan PostgreSQL `alpha` aktif.