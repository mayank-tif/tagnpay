from django.core.management.base import BaseCommand
from etl.views import etl_pipeline

class Command(BaseCommand):
    help = 'Run the ETL pipeline'

    def handle(self, *args, **kwargs):
        #session_brand_id = 1  # Replace with actual brand ID or dynamic input
        etl_pipeline()
        self.stdout.write(self.style.SUCCESS('ETL Pipeline executed successfully!'))