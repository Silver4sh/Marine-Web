"""
Test koneksi database berdasarkan file .env
Jalankan: python test_connection.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "marine_db")

print("=" * 55)
print("  Database Connection Test")
print("=" * 55)
print(f"  Host  : {DB_HOST}:{DB_PORT}")
print(f"  User  : {DB_USER}")
print(f"  DB    : {DB_NAME}")
print(f"  Pass  : {'*' * len(DB_PASS)} ({len(DB_PASS)} karakter)")
print()

try:
    import psycopg2

    conn = psycopg2.connect(
        host=DB_HOST, port=int(DB_PORT),
        dbname=DB_NAME, user=DB_USER,
        password=DB_PASS, connect_timeout=5,
    )
    cur = conn.cursor()

    # 1. Version
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    print(f"[OK]  Terhubung ke PostgreSQL")
    print(f"      {version[:65]}")
    print()

    # 2. Schema check — setiap tabel di-check tersendiri agar tidak terganggu abort
    tables_to_check = [
        ("operation", "users"),
        ("operation", "vessels"),
        ("operation", "clients"),
        ("operation", "orders"),
        ("operation", "payments"),
        ("operation", "sites"),
        ("operation", "user_managements"),
        ("buoy",      "buoys"),
        ("buoy",      "buoy_sensor_histories"),
        ("audit",     "audit_logs"),
        ("log",       "surveis"),
        ("log",       "vibrocore_logs"),
        ("survey",    "daily_report_survey_activity"),  # mungkin tidak ada
    ]

    print("  Tabel check:")
    all_ok = True
    for schema, table in tables_to_check:
        try:
            conn2 = psycopg2.connect(
                host=DB_HOST, port=int(DB_PORT), dbname=DB_NAME,
                user=DB_USER, password=DB_PASS, connect_timeout=5
            )
            c2 = conn2.cursor()
            c2.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
            count = c2.fetchone()[0]
            c2.close(); conn2.close()
            print(f"    [OK]  {schema}.{table:40s} ({count} rows)")
        except psycopg2.errors.UndefinedTable:
            print(f"    [!!]  {schema}.{table:40s} — tabel tidak ditemukan")
            all_ok = False
        except Exception as te:
            print(f"    [!!]  {schema}.{table:40s} — {te}")
            all_ok = False

    cur.close(); conn.close()
    print()
    print("=" * 55)
    if all_ok:
        print("  HASIL: Semua tabel OK, siap jalankan aplikasi!")
    else:
        print("  HASIL: Koneksi OK, tapi ada tabel yang belum ada.")
        print("         Pastikan database/table.sql sudah dijalankan.")
    print("         streamlit run main.py")
    print("=" * 55)

except psycopg2.OperationalError as e:
    err = str(e).strip()
    print(f"[FAIL] Koneksi GAGAL: {err}")
    print()
    if "password authentication" in err:
        print("  -> Password salah. Update DB_PASS di file .env")
    elif "does not exist" in err:
        print(f"  -> Database '{DB_NAME}' belum ada. Buat dulu di pgAdmin.")
    elif "refused" in err or "could not connect" in err:
        print(f"  -> PostgreSQL tidak aktif di port {DB_PORT}.")

except ImportError:
    print("[FAIL] psycopg2 tidak terinstall: pip install psycopg2-binary")

except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
