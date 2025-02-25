from django.core.cache import cache
from tagnpayloyalty.models import TblSettings, Templates

CACHE_TIMEOUT = 36000  # Cache timeout in seconds (10 minutes=600)

def global_brand_data(session_brand_id):
    
    cache_key = f'gb_data_brand_{session_brand_id}'
    
    # Check if the data is already cached
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        # Fetch data from the database, filtering by brand ID
        cached_data1 = TblSettings.objects.filter(global_brandid=session_brand_id)  # Adjust your filter accordingly
        cached_data2 = Templates.objects.filter(brand_id=session_brand_id,status_flag=1).values('id','template_flag','template_text')  # Adjust your filter accordingly
        
        cached_data = {'cached_data1': cached_data1, 'cached_data2': list(cached_data2)}

        # Cache the fetched data
        cache.set(cache_key, cached_data, CACHE_TIMEOUT)
    
    return cached_data

def get_global_data_for_brand(session_brand_id):

    cache_key = f'gb_data_brand_{session_brand_id}'
    return cache.get(cache_key)