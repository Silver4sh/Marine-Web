from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db import connection

class StreamlitAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        
        # Check against legacy database
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    um.id_user,
                    u.role
                FROM operation.user_managements um
                JOIN operation.users u ON um.id_user = u.code_user
                WHERE um.id_user = %s
                    AND trim(um.password) = trim(%s)
                    AND um.status = 'Active'
                    AND u.status = 'Active'
            """
            cursor.execute(query, [username, password])
            row = cursor.fetchone()
            
            if row:
                user_id, role = row
                
                # Get or Create Django User
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    # Create a new user with no password (since we verify against external DB)
                    user = User(username=username)
                    user.is_staff = (role == 'Admin')
                    user.is_superuser = (role == 'Admin')
                    user.set_unusable_password()
                    user.save()
                
                return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
