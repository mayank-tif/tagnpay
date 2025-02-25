import hashlib
import re
import pandas as pd
from .models import *
import random

def get_brand_id_from_domain(request):
    brand_url = request.headers.get('X-Origin', request.META.get('HTTP_ORIGIN', request.headers.get('Origin')))
    if brand_url is None:
        return {
            "success": False,
            "status": False,
            "message": "No HTTP_ORIGIN key in request",
            }

    brand_id = None

    if brand_id is None:
        try:
            config = TblSettings.objects.filter(brand_url=brand_url).first()
            if config:
                brand_id = config.global_brandid
#                try:
#                    CacheUtils.set_url_mapping(brand_url, brand_id)
#                except CacheException as ce:
#                    logger.error(f"Error while setting brand_id to cache: url - {brand_url} , error - {ce}")
            else:
#                additional_url = TblSettings.objects.filter(auth_config__additional_brand_url__contains=brand_url).first()
#                if additional_url:
#                    brand_id = additional_url.invoice_brandid
#                    try:
#                        CacheUtils.set_url_mapping(brand_url, brand_id)
#                    except CacheException as ce:
#                        logger.error(f"Error while setting brand_id to cache: url - {brand_url} , error - {ce}")

                #else:
                    return {
                        "success": False,
                        "status": False,
                        "message": "No brand_id exists for this brand_url",
                    }
            
            return brand_id
        except Exception as e:
            return {
                "success": False,
                "status": False,
                "message": str(e),
            }
    return brand_id    


def get_brand_id_from_api_url(request):

    if request and hasattr(request, 'get_host'):
        domain_nm = request.get_host()
        scheme = request.scheme
        brand_url = f"{scheme}://{domain_nm}"
    else:
        raise ValueError("Invalid request object provided, no 'get_host' attribute")
    
    print(brand_url)

    if brand_url is None:
        return {
            "success": False,
            "status": False,
            "message": "No domain found",
            }

    brand_id = None

    if brand_id is None:
        try:
            config = TblSettings.objects.filter(brand_url=brand_url).first()
            if config:
                brand_id = config.global_brandid
#                try:
#                    CacheUtils.set_url_mapping(brand_url, brand_id)
#                except CacheException as ce:
#                    logger.error(f"Error while setting brand_id to cache: url - {brand_url} , error - {ce}")
            else:
#                additional_url = TblSettings.objects.filter(auth_config__additional_brand_url__contains=brand_url).first()
#                if additional_url:
#                    brand_id = additional_url.invoice_brandid
#                    try:
#                        CacheUtils.set_url_mapping(brand_url, brand_id)
#                    except CacheException as ce:
#                        logger.error(f"Error while setting brand_id to cache: url - {brand_url} , error - {ce}")

                #else:
                    return {
                        "success": False,
                        "status": False,
                        "message": "No brand_id exists for this brand_url",
                    }
            
            return brand_id
        except Exception as e:
            return {
                "success": False,
                "status": False,
                "message": str(e),
            }
    return brand_id    



# =================Convert password into encryption=============
def str_encrypt(password):
    sha256 = hashlib.sha256(password.encode())
    pass_enc = sha256.hexdigest()
    return pass_enc
# =============================END==============================


# ==========Validate Mobile number function===============
def mobile_number_validation(mobileno, brand_id):

   #mobileno = get_active_number(brand_id = brand_id, registered_mobile_no = mobileno)

    if pd.isnull(brand_id) or brand_id == '' or brand_id is None:
        return 'brand id should not be empty..!'

    # Fetch the config data for the brand only once
    config_data = TblSettings.objects.filter(global_brandid=brand_id, status_flag=1).values('mobile_length', 'mobile_startwith')

    if not config_data:
        return 'Some error on server side!'
    config_data = config_data[0]

    if not config_data['mobile_startwith'] or not config_data['mobile_length']:
        print("Error:-{}".format("Brand is not registered for loyalty."))
        return

    mobile_startwith = config_data['mobile_startwith']
    mobile_length = int(config_data['mobile_length'])

    regex = re.compile('[@_!#$%^&*()<>?/}{~:.+=`?,;"| ]')
    if pd.isnull(mobileno) or mobileno == '':
        return 'mobile number should not be empty..!'
    elif not mobileno.isdigit():
        return 'Please give only numbers.'
    elif not mobileno.startswith(tuple(mobile_startwith)):
        return 'mobile number should start with {}..!'.format(mobile_startwith)
    elif regex.search(mobileno) is not None:
        return 'mobile number should not contain any special character (@_!#$%^&*()<>?/}{~:.+=`?,;"| )'
    elif len(mobileno) < mobile_length:
        return 'mobile number length not less than {}..!'.format(mobile_length)
    elif len(mobileno) > mobile_length:
        return 'mobile number length not greater than {}..!'.format(mobile_length)


# =======================--END--=============================================

# ======================= Generate Transaction Id - Start ===========================

def generate_transaction_id(initials="TX"):
    # Get the current date and time with milliseconds
    now = datetime.datetime.now()
    date_part = now.strftime('%y%m%d')          # Format: YYMMDD
    time_part = now.strftime('%H%M%S%f')[:15]  # Format: HHMMSS + first 3 digits of microseconds (milliseconds)
    
    # Generate a random 4-digit number
    random_part = f"{random.randint(1000, 9999)}"

    random_part2 = f"{random.randint(100, 999)}"
    
    # Combine initials, date, time, and random number
    transaction_id = f"{initials}{date_part}{random_part2}{time_part}{random_part}"
    
    return transaction_id

# ======================= Generate Transaction Id - End ===========================