from django.db import connection

tables = ['bookings', 'users', 'labs', 'items', 'maintenance', 'bhp', 'sops']
with connection.cursor() as cursor:
    for table in tables:
        try:
            cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM {table}) + 1, 1), false);")
            print(f'Fixed {table}')
        except Exception as e:
            print(f'Failed {table}: {e}')
