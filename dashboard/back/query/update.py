import pandas as pd
import streamlit as st
from sqlalchemy import text
from back.connection.conection import get_connection

def update_last_login_optimized(username, password):
    conn = get_connection()
    try:
        with conn.begin():
            update_query = text("""
                UPDATE operational.user_managements
                SET last_login = CURRENT_TIMESTAMP
                WHERE id_user = :user_id AND password = :pwd
            """)
            conn.execute(update_query, {"user_id": username, "pwd": password})
        return True
    except Exception as e:
        print(f"Update last_login error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def update_password(username, old_pass, new_pass):
    if not username or not old_pass or not new_pass:
        return False, "Semua field harus diisi"
    
    if old_pass == new_pass:
        return False, "Password baru tidak boleh sama dengan password lama"
    
    conn = None
    try:
        conn = get_connection()
        
        query = text("""
            SELECT 
                um.id_user,
                u.role,
                u.status as user_status,
                um.status as account_status
            FROM operational.user_managements um
            JOIN operational.users u ON um.id_user = u.code_user
            WHERE um.id_user = :username
                AND um.password = :password
                AND um.status = 'Active'
                AND u.status = 'Active'
                AND u.role IN ('Finance', 'Admin')
        """)
        
        df = pd.read_sql(query, conn, params={
            "username": username, 
            "password": old_pass
        })
        
        if df.empty:
            return False, "Username atau password lama salah"
        
        update_query = text("""
            UPDATE operational.user_managements
            SET password = :new_password,
            updated_at = CURRENT_TIMESTAMP
            WHERE id_user = :user_id 
                AND password = :old_password
        """)
        
        result = conn.execute(update_query, {
            "user_id": username, 
            "old_password": old_pass, 
            "new_password": new_pass.strip()
        })
        
        conn.commit()
        
        if result.rowcount > 0:
            return True, "Password berhasil diperbarui"
        else:
            return False, "Gagal memperbarui password"
            
    except Exception as e:
        if conn:
            conn.rollback()
        st.error(f"Database error: {e}")
        return False, f"Terjadi kesalahan sistem: {str(e)}"
    
    finally:
        if conn:
            conn.close()