from db.connection import get_engine, run_query
from sqlalchemy import text

def get_all_users():
    return run_query("SELECT u.code_user, um.id_user as username, u.role, u.status as user_status, um.status as account_status, um.last_login FROM operation.users u JOIN operation.user_managements um ON u.code_user = um.id_user ORDER BY u.code_user ASC")

def create_new_user(username, password, role):
    try:
        with get_engine().begin() as conn:
            if conn.execute(text("SELECT 1 FROM operation.users WHERE code_user = :u"), {"u": username}).fetchone(): return False, "Pengguna sudah ada."
            conn.execute(text("INSERT INTO operation.users (code_user, role, status) VALUES (:u, :r, 'Active')"), {"u": username, "r": role})
            conn.execute(text("INSERT INTO operation.user_managements (id_user, password, status) VALUES (:u, :p, 'Active')"), {"u": username, "p": password})
            return True, "Berhasil dibuat."
    except Exception as e: return False, str(e)

def update_user_status(username, new_status):
    try:
        with get_engine().begin() as conn:
            conn.execute(text("UPDATE operation.users SET status = :s WHERE code_user = :u"), {"s": new_status, "u": username})
            conn.execute(text("UPDATE operation.user_managements SET status = :s WHERE id_user = :u"), {"s": new_status, "u": username})
            return True
    except: return False

def update_user_role(username, new_role):
    try:
        with get_engine().begin() as conn:
            conn.execute(text("UPDATE operation.users SET role = :r WHERE code_user = :u"), {"r": new_role, "u": username})
            return True
    except: return False

def delete_user(username):
    try:
        with get_engine().begin() as conn:
            conn.execute(text("DELETE FROM operation.user_managements WHERE id_user = :u"), {"u": username})
            conn.execute(text("DELETE FROM operation.users WHERE code_user = :u"), {"u": username})
            return True
    except: return False

def update_last_login_optimized(username, password):
    try:
        with get_engine().begin() as conn:
            conn.execute(text("UPDATE operation.user_managements SET last_login = CURRENT_TIMESTAMP WHERE id_user = :u AND password = :p"), {"u": username, "p": password})
            return True
    except: return False

def update_password(username, old_pass, new_pass):
    if old_pass == new_pass: return False, "Kata sandi identik"
    try:
        with get_engine().begin() as conn:
            res = conn.execute(text("SELECT 1 FROM operation.user_managements WHERE id_user = :u AND password = :p"), {"u": username, "p": old_pass}).fetchone()
            if not res: return False, "Kredensial salah"
            conn.execute(text("UPDATE operation.user_managements SET password = :np, updated_at = CURRENT_TIMESTAMP WHERE id_user = :u"), {"np": new_pass.strip(), "u": username})
            return True, "Berhasil"
    except Exception as e: return False, str(e)
