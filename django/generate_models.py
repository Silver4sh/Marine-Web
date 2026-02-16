import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marine_project.settings')
django.setup()

with open('dashboard/models.py', 'w', encoding='utf-8') as f:
    call_command('inspectdb', stdout=f)

print("Models generated successfully.")
