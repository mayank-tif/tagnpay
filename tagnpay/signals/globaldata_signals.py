from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from tagnpayloyalty.models import TblSettings

@receiver(post_save, sender=TblSettings)
def invalidate_cache_on_save(sender, instance, **kwargs):

    # Invalidate cache for the specific brand associated with the instance
    cache_key = f'gb_data_brand_{instance.global_brandid}'
    cache.delete(cache_key)

@receiver(post_delete, sender=TblSettings)
def invalidate_cache_on_delete(sender, instance, **kwargs):

    # Invalidate cache for the specific brand associated with the instance
    cache_key = f'gb_data_brand_{instance.global_brandid}'
    cache.delete(cache_key)