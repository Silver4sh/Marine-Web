import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marine_project.settings')
django.setup()

from django.db import connection

def check_tables():
    with connection.cursor() as cursor:
        cursor.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema IN ('operation', 'log', 'audit', 'rockworks', 'survey');")
        rows = cursor.fetchall()
        print(f"Found {len(rows)} tables in target schemas.")
        for row in rows:
            print(f"{row[0]}.{row[1]}")

    print("\nIntrospection:")
    table_names = connection.introspection.table_names()
    print(f"Django sees {len(table_names)} tables: {table_names}")

check_tables()
