import hashlib
import re
import pandas as pd
from tagnpayloyalty.models import *
import requests
from django.http import JsonResponse
from django.db import transaction
import logging
from utils.globaldata_utils import global_brand_data, get_global_data_for_brand
from tagnpay.env_details import *
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def sms_data_save(sms_type, user_id, brand_id, sms_response_text, sms_response_status, bill_date, bill_amount, bill_number, location_id, message, mobileno, loyalty_id, sms_for, sms_response, sms_flag):
    try:
        if bill_amount == "" or bill_amount is None:
            bill_amount = None
        if bill_date == "" or bill_date is None:
            bill_date = None
        if sms_type == "Register" or sms_type == "Login":
            TblRegActivitySMSLogs.objects.create(
                mobileno=mobileno,
                sms_text=message,
                loyalty_id=loyalty_id,
                user_id=user_id,
                sms_response_status=sms_response_status,
                brand_id=brand_id,
                sms_response=sms_response,
                sms_response_text=sms_response_text,
                sms_for=sms_for,
                location_id=location_id,
                bill_number=bill_number,
                bill_amount=bill_amount,
                bill_date=bill_date,
            )

        elif sms_type == "Trans":
            TblTransActivitySMSLogs.objects.create(
                mobileno=mobileno,
                sms_for=sms_for,
                sms_text=message,
                user_id=user_id,
                brand_id=brand_id,
                location_id=location_id,
                sms_response_status=sms_response_status,
                sms_response=sms_response,
                sms_response_text=sms_response_text,
                bill_number=bill_number,
                bill_amount=bill_amount,
                bill_date=bill_date,
            )

        logger.info("message: Unidentified Sms flag")
    except Exception as e:
        logger.error(f"Exception occured in saving sms in table: {e}")

class SingleSMSBroadcastApi():

    @classmethod
    def smssend(cls, sms_for, brand_id, user_id, mobileno, message, sms_type, bill_date, bill_number, bill_amount, location_id, loyalty_id):

        gb_brand_data = TblSettings.objects.filter(global_brandid=brand_id)

        if len(gb_brand_data) > 0:
            sms_api_url = gb_brand_data[0].sms_api_url
            country_code = gb_brand_data[0].country_code
            config_brnd_sender_id = gb_brand_data[0].sender_id

            mobnum = str(country_code)+str(mobileno)

        # Prepare query parameters for the SMS API
        query_params = {
            'ver': '1.0',   
            'key': KX_SMS_API_KEY,
            'encrpt': '0',
            'dest': mobnum,   
            'send': config_brnd_sender_id,         
            'dlt_entity_id': '',
            'text': message  
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # If the API expects any data in the body of the POST request
        #payload = {}  # Add data if required by the API

        try:
            #response = requests.post(sms_api_url, headers=headers, params=query_params, json=payload)
            response = requests.post(sms_api_url, headers=headers, params=query_params)
            #print(response)
            sms_response = response.status_code
            sms_response_text = response.text
            if response.status_code == 200:
                sms_status = True
            else:
                sms_status = False
            
            if 'success' in sms_response_text or 'deliver' in sms_response_text or 'accepted' in sms_response_text or 'sent' in sms_response_text or 'true' in sms_response_text:
                sms_response_status = "SUCCESS"
            else:
                sms_response_status = "FAILED"
                
            sms_data_save(sms_type, user_id, brand_id, sms_response_text, sms_response_status, bill_date, bill_amount, bill_number, location_id, message, mobileno, loyalty_id, sms_for, sms_response, '0')
            
            return {
                'status': sms_status,
                'status_text': 'Success', 
                'status_code': response.status_code,
                'response': response.text
            }
    
            
        except requests.exceptions.RequestException as e:
            #return Response({'success': False, 'message': 'Request failed', 'error': str(e)})
            return {
                'status': False, 
                'status_text': 'Request failed', 
                'status_code': '',
                'response': str(e)
            }
