from sqlalchemy import text
from back.connection.conection import get_engine, get_connection
import pandas as pd
import streamlit as st
from back.query.queries import run_query

# --- READ ---
def get_all_users():
    """List all users with their roles and status."""
    query = """
    SELECT 
        u.code_user,
        um.id_user as username,
        u.role,
        u.status as user_status,
        um.status as account_status,
        um.last_login
    FROM operational.users u
    JOIN operational.user_managements um ON u.code_user = um.id_user
    ORDER BY u.code_user ASC
    """
    return run_query(query)

# --- CREATE ---
def create_new_user(username, password, role):
    """
    Creates a new user in both 'users' and 'user_managements' tables.
    Transaction is used to ensure atomicity.
    """
    engine = get_engine()
    if not engine:
        return False, "Database connection failed."

    try:
        with engine.begin() as conn:
            # 1. Check if user exists
            check_q = text("SELECT 1 FROM operational.users WHERE code_user = :username")
            res = conn.execute(check_q, {"username": username}).fetchone()
            if res:
                return False, f"User '{username}' already exists."

            # 2. Insert into operational.users
            insert_user = text("""
                INSERT INTO operational.users (code_user, role, status)
                VALUES (:username, :role, 'Active')
            """)
            conn.execute(insert_user, {"username": username, "role": role})

            # 3. Insert into operational.user_managements
            insert_auth = text("""
                INSERT INTO operational.user_managements (id_user, password, status)
                VALUES (:username, :password, 'Active')
            """)
            conn.execute(insert_auth, {"username": username, "password": password})
            
            return True, "User created successfully."
    except Exception as e:
        return False, f"Error creating user: {e}"

# --- UPDATE ---
def update_user_status(username, new_status):
    """Toggle user active/inactive status."""
    engine = get_engine()
    if not engine: return False
    
    try:
        with engine.begin() as conn:
            q1 = text("UPDATE operational.users SET status = :status WHERE code_user = :username")
            conn.execute(q1, {"status": new_status, "username": username})
            
            q2 = text("UPDATE operational.user_managements SET status = :status WHERE id_user = :username")
            conn.execute(q2, {"status": new_status, "username": username})
            return True
    except Exception as e:
        print(f"Error updating status: {e}")
        return False

def update_user_role(username, new_role):
    """Update user role."""
    engine = get_engine()
    if not engine: return False
    
    try:
        with engine.begin() as conn:
            q = text("UPDATE operational.users SET role = :role WHERE code_user = :username")
            conn.execute(q, {"role": new_role, "username": username})
            return True
    except Exception as e:
        print(f"Error updating role: {e}")
        return False

# --- DELETE ---
def delete_user(username):
    """Delete a user from the system."""
    engine = get_engine()
    if not engine: return False
    
    try:
        with engine.begin() as conn:
            q1 = text("DELETE FROM operational.user_managements WHERE id_user = :username")
            conn.execute(q1, {"username": username})
            
            q2 = text("DELETE FROM operational.users WHERE code_user = :username")
            conn.execute(q2, {"username": username})
            return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False
