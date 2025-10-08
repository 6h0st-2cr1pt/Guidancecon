from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Show all database tables'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            self.stdout.write("\nExisting database tables:")
            self.stdout.write("------------------------")
            for table in tables:
                self.stdout.write(table[0])
                
                # Show columns for each table
                cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table[0]}'
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                for col in columns:
                    self.stdout.write(f"  - {col[0]}: {col[1]}")