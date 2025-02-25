from ast import Continue
from errno import EILSEQ
#from tkinter.tix import STATUS
from turtle import end_fill
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.views.generic import TemplateView
from pymysql import NULL
from tagnpayloyalty.helpers import get_brand_id_from_domain, str_encrypt, mobile_number_validation, get_brand_id_from_api_url, generate_transaction_id
from tagnpayloyalty import helpers
import pandas as pd
from rest_framework.response import Response
from .models import *
from django.urls import reverse
from datetime import datetime, timedelta
from django.core.paginator import Paginator
import matplotlib.pyplot as plt
import io
import base64
from django.db.models import Count, Sum
from utils.globaldata_utils import global_brand_data, get_global_data_for_brand
#from utils.ocr_utils import extract_text_from_image
#from utils.parser_utils import parse_bill_text
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
import os
import json
from django.contrib import messages
from django.http import JsonResponse
from django.db import connection
from django.db import transaction
import requests
from common.helpers.smshelpers import SingleSMSBroadcastApi
import urllib.parse
import plotly.express as px
import plotly.io as pio
from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tagnpay.env_details import *
from django.utils.timezone import now
from django.conf import settings
import shutil
import pymysql
import psycopg2
from utils.globaldata_utils import global_brand_data
import random
from pymongo import MongoClient
import calendar
import xml.etree.ElementTree as ET


class View_platformlogin(TemplateView):

    def get(self, request):
        msg = request.GET.get('msg', None)
        return render(request,"index.html",{'msg': msg})
    
    def post(self, request):
        brand_id = get_brand_id_from_domain(request)
        #brand_id = "10001"
        username = request.POST.get('username')
        pswd = request.POST.get('password')
        enc_pswd = str_encrypt(str(pswd))
        pswd = enc_pswd
        #print(enc_pswd)

        try:

            if pd.isnull(brand_id) or brand_id == '' or brand_id is None:
                return render(request,"index.html",{'message': 'Brand id should not be empty..!', "status": False})
            if pd.isnull(username) or username == '' or username is None:
                return render(request,"index.html",{'message': 'Username should not be empty..!', "status": False})
            if pd.isnull(pswd) or pswd == '' or pswd is None:
                return render(request,"index.html",{'message': 'Password should not be empty..!', "status": False})
            
            if username is not None and pswd is not None:
                user_dtls = MstUserLogins.objects.filter(loginname=username, securepassword=pswd,status_flag=1, brand_id=brand_id)

                if len(user_dtls) > 0:
                    request.session['brand_id'] = brand_id
                    request.session['loginid'] = user_dtls[0].id
                    request.session['loginname'] = user_dtls[0].loginname
                    request.session['roleid'] = user_dtls[0].roleid_id
                    request.session['is_active'] = True
                    request.session['loggedin_user_name'] = user_dtls[0].firstname
                    request.session['loggedin_user_email'] = user_dtls[0].email
                    #print("Hiiii")

                    global_brand_data(brand_id)

                   
                #redirect_url = "/home"
                    return redirect("/home")
                else:
                    return render(request,"index.html",{"message": "Incorrect Password!!", "status": False})
            else:
                return render(request,"index.html",{"message": "Please provide both username and password", "status": False})
        except Exception as e:
            print(e)
            return render(request,"index.html",{"message": "Please provide both username and password ({e})", "status": False})


class View_UserRegistration(TemplateView):

    def get(self, request, lcid, brid):
        
        return render(request,"CustomerRegistration/index.html")

    def post(self, request, lcid, brid):

        data = request.POST
        mobileno = data.get("mobileno")
        #print(mobileno)     
        #if (hasattr(request, 'internal_client') and request.internal_client) or pos_api:
        #    brand_id = request.data.get("brand_id")
        #else:
        #   brand_id = request.auth_data.get("brand_id")

        brand_id = get_brand_id_from_domain(request)
        #brand_id = '10001'

        #title = data.get("title")
        name = data.get("firstname")
        lastname = data.get("lastname")
        email = data.get("email")
        gender = data.get("gender")
        dob = data.get("dob")
        doa = data.get("doa")
#        address1 = data.get("address1")
#        address2 = data.get("address2")
#        town = data.get("town")
#        city = data.get("city")
#        country = data.get("country")
#        postalcode = data.get("postalcode")
#        agegroup = data.get("agegroup")
#        state = data.get("state")
#        occupation = data.get("occupation")
#        homeno = data.get("homeno")
#        adhaar_no = data.get("adhaar_no")
#        customer_type = data.get("customer_type")
#        gst = data.get("gst")
#        pan = data.get("pan")
#        profile_pic = data.get("profile_pic")
#        year_dob = data.get("year_dob")
#        month_dob = data.get("month_dob")
#        day_dob = data.get("day_dob")
#        year_doa = data.get("year_doa")
#        month_doa = data.get("month_doa")
#        day_doa = data.get("day_doa")
#        latitude = data.get("latitude")
#        longitude = data.get("longitude")
#        access_token = data.get("access_token")
        customer_id = data.get("customer_id")

        if doa == '':
            doa = '1900-01-01'

        #print(dob)

        
#        if pd.isnull(user_id) or user_id == '':
#            return Response({'message': 'user id should not be empty..!', "status": False})
    
        try: 
            TblRequestAuditLogs.objects.create(firstname=name,mobileno=mobileno,brand_id=brand_id,email_id=email,gender=gender,dob=dob,doa=doa,location_code=lcid,mall_brand_id=brid,api_flag='Registration QR Code')


            if lcid is not None:
                loc_dtls = LocationMst.objects.filter(location_code=lcid, status_flag=1, brand_id=brand_id)
                
                if len(loc_dtls) > 0:
                    loc_id = loc_dtls[0].location_id
                else:
                    return render(request, "CustomerRegistration/index.html", {'message': 'Location doesn''t match!', "status": False})        
            else:
                return render(request, "CustomerRegistration/index.html", {'message': 'Location id should not be empty..!', "status": False})


            #print(brand_id)
            if pd.isnull(brand_id) or brand_id == '':
                #return Response({'message': 'brand id should not be empty..!', "status": False})
                return render(request, "CustomerRegistration/index.html", {'message': 'brand id should not be empty..!', "status": False})

            # ============mobile number validation==================
            message = mobile_number_validation(mobileno, brand_id)
            #print(message)
            if message:
                #return Response({'message': message, "status": False})
                return render(request, "CustomerRegistration/index.html", {'message': message, "status": False})
            # ===============================END=================================
            if LoyaltyCustomers.objects.filter(mobileno=mobileno, brand_id=brand_id, status_flag=1).exists():
                #return Response({'message': f'Customer with number {mobileno} already registered', "status": False})
                return render(request, "CustomerRegistration/index.html", {'message': f'Customer with number {mobileno} already registered', "status": False})
            
            #if pos_api:
            #    store_id = data.get("store_id")
            #else:
            #    store_id = get_store_id(user_id, auth_data=request.auth_data)
            # ===================END=================================
            # ----------------------Add entry parameter log--removed-------------------
            # -------------------------------END------------------------------

            if dob != "" and dob != None:
                dobsplt = dob.split("-")
                dobday = dobsplt[2]
                dobmonth = dobsplt[1]
                dobyear = dobsplt[0]

            if doa != "" and doa != None:
                doasplt = doa.split("-")
                doaday = doasplt[2]
                doamonth = doasplt[1]
                doayear = doasplt[0]

            if brid == 0:
               LoyaltyCustomers.objects.create(firstname=name,lastname=lastname,mobileno=mobileno,brand_id=brand_id,email=email,gender=gender,dob=dob,doa=doa,location_id_id=loc_id,reg_source='QR Code',dobday=dobday,dobmonth=dobmonth,dobyear=dobyear,doaday=doaday,doamonth=doamonth,doayear=doayear)
            else:
                LoyaltyCustomers.objects.create(firstname=name,lastname=lastname,mobileno=mobileno,brand_id=brand_id,email=email,gender=gender,dob=dob,doa=doa,location_id_id=loc_id,mall_brand_id_id=brid,reg_source='QR Code',dobday=dobday,dobmonth=dobmonth,dobyear=dobyear,doaday=doaday,doamonth=doamonth,doayear=doayear)
            

            LoyaltyPoints.objects.create(name=name,mobileno=mobileno,brand_id=brand_id,bal_points=0,bal_cash_val=0)

            msg = config_Registration_SMS_text

            sms_api_response = SingleSMSBroadcastApi.smssend("Reg", brand_id, '0', mobileno, msg, "Register","","","",loc_id,"")

            #return Response({"message": "Customer registered successfully", "status": True})
            return render(request, "CustomerRegistration/index.html", {"message": "Customer registered successfully", "status": True})
        
        except Exception as e:
            #return Response({"message": "Customer is not registered", "status": True})
            return render(request, "CustomerRegistration/index.html", {"message": f"Customer not registered ({e})", "status": True})


class CustRegistrationPlatformView(TemplateView):
    def get(self, request):
        cities = CityMst.objects.all().order_by('city_name')
        states = StateMst.objects.all().order_by('states_name')
        countries = CountryMst.objects.all().order_by('country_name')
        return render(request,"pages/forms/registration-form.html",{"cities":cities,"states":states,"countries":countries})
    def post(self, request):
        data = request.POST
        mobileno = data.get("mobileno")
        name = data.get("name")
        email = data.get("email")
        gender = data.get("gender")
        dob = data.get("dob")
        doa = data.get("doa")
        address1 = data.get("address1")
        address2 = data.get("address2")
        landmark = data.get("landmark")
        district = data.get("district")
        city = data.get("city")
        state = data.get("state")
        country = data.get("country")
        zipcode = data.get("zipcode")
        reg_source = data.get("regsource")

        if dob == '':
            dob = '1900-01-01'
        if doa == '':
            doa = '1900-01-01'

        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

        loc_id = MstUserLogins.objects.filter(brand_id=brand_id, id=login_id, status_flag=1).values_list('locationid', flat=True).first()  

        cities = CityMst.objects.all().order_by('city_name')
        states = StateMst.objects.all().order_by('states_name')
        countries = CountryMst.objects.all().order_by('country_name')

        validated_data = {
            'mobileno': mobileno,
            'customer_name': name,
            'email': email,
            'gender': gender,
            'dob': dob,
            'doa': doa,
            'address1': address1,
            'address2': address2,
            'landmark': landmark,
            'district': district,
            'city': city,
            'state': state,
            'country': country,
            'zipcode': zipcode,
            'reg_source': reg_source,
            'loc_id': loc_id,
        }

        result = register_customer(validated_data,brand_id,login_id)

        return render(request,"pages/forms/registration-form.html",{'message': result.data.get("message"), "status": False, "cities":cities, "states":states, "countries":countries})


def register_customer(data,brand_id,login_id):
    mobileno = data['mobileno']
    customer_name = data['customer_name']
    email = data['email']
    gender = data['gender']
    dob = data['dob']
    doa = data['doa']
    address1 = data['address1']
    address2 = data['address2']
    landmark = data['landmark']
    district = data['district']
    city = data['city']
    state = data['state']
    country = data['country']
    zipcode = data['zipcode']
    reg_source = data['reg_source']
    loc_id = data['loc_id']
    #print(dob)

    

    try:
        TblRequestAuditLogs.objects.create(firstname=customer_name,mobileno=mobileno,brand_id=brand_id,email_id=email,gender=gender,dob=dob,doa=doa,location_id=loc_id,floor_flat=address1,building=address2,street=landmark,town=district,city=city,state=state,country=country,zipcode=zipcode,reg_source=reg_source,api_flag='Registration Platform')

        if dob != "" and dob != None:
            date_obj = datetime.strptime(dob, "%Y-%m-%d")
            dob_str = date_obj.strftime('%Y-%m-%d')
            dobsplt = dob_str.split("-")
            dobday = dobsplt[2]
            dobmonth = dobsplt[1]
            dobyear = dobsplt[0]
        else:
            dobday = ""
            dobmonth = ""
            dobyear = ""

        if doa != "" and doa != None:
            date_obj1 = datetime.strptime(doa, "%Y-%m-%d")
            doa_str = date_obj1.strftime('%Y-%m-%d')
            doasplt = doa_str.split("-")
            doaday = doasplt[2]
            doamonth = doasplt[1]
            doayear = doasplt[0]
        else:
            doaday = ""
            doamonth = ""
            doayear = ""

        if city == "":
            city=None
        if state == "":
            state=None
        if country == "":
            country = None

        msg = mobile_number_validation(mobileno, brand_id)
        #print(message)
        if msg:
            return Response({'message': msg, "status": False})
        if customer_name == None or customer_name == '':
            return Response({'message': 'Customer Name can''t be empty', "status": False})
        if not loc_id:
            return Response({'message': 'Location doesn''t match..!', "status": False})
        if pd.isnull(brand_id) or brand_id == '' or brand_id == None:
            return Response({'message': 'Brand id should not be empty..!', "status": False})
        if LoyaltyCustomers.objects.filter(mobileno=mobileno, brand_id=brand_id, status_flag=1).exists():
            return Response({'message': "Mobile number is already registered with us!!", "status": False})
        if LoyaltyCustomers.objects.filter(mobileno=mobileno, brand_id=brand_id, status_flag=0).exists():
            return Response({"message": "Mobile number is deactivated!!", "status": False})

        #msg = config_Registration_SMS_text

        gfb = global_brand_data(brand_id)
        gfb_cached_data2 = gfb.get('cached_data2', [])
        #gfb = cache.get('global_filtered_data')

        #app_templates = [item for item in gfb_cached_data2 if item['template_flag'] == 'RegPlatform']

        #print(gfb.header_name)

        #print(gfb)

        config_Platform_Registration_template_text = next(
        (template['template_text'] for template in gfb_cached_data2 if template['template_flag'] == 'RegPlatform'),
        None  # Default to None if no match is found
        )

        msg = config_Platform_Registration_template_text

        #print("Hiii")
        #print(config_Platform_Registration_template_text)
        #print("Helloo")

        gb_brand_data = TblSettings.objects.filter(global_brandid=brand_id)

        if len(gb_brand_data) > 0:
            brand_earn_points_logic = gb_brand_data[0].earn_points_logic

        tier_id = Tiers.objects.filter(brand_id=brand_id,status_flag=1,tier_type='regular',tier_logic_type=brand_earn_points_logic).order_by('tier_minimum_value').values_list('tier_id', flat=True).first()

        with transaction.atomic():
            customer_entry = LoyaltyCustomers.objects.create(firstname=customer_name,mobileno=mobileno,brand_id=brand_id,email=email,gender=gender,dob=dob,doa=doa,location_id_id=loc_id,reg_source=reg_source,dobday=dobday,dobmonth=dobmonth,dobyear=dobyear,doaday=doaday,doamonth=doamonth,doayear=doayear,address1=address1,address2=address2,landmark=landmark,district=district,city_id=city,state_id=state,country_id=country,zipcode=zipcode)

            points_entry = LoyaltyPoints.objects.create(name=customer_name,mobileno=mobileno,brand_id=brand_id,bal_points=0,bal_cash_val=0,tier_id_id=tier_id)

            sms_api_response = SingleSMSBroadcastApi.smssend("Reg", brand_id, login_id, mobileno, msg, "Register","","","",loc_id,"")    

        return Response({'message': "Customer registered successfully.", "status": False})

    except Exception as e:
        return Response({'message': f"An error occurred during validation or calculation ({e})", "status": False})



class View_HomeDashboard(TemplateView):
    
    def get(self, request):
         
        #login_id = request.session.get("loginid")
        brandid = request.session.get("brand_id")

        try:
            #user_dtls = MstUserLogins.objects.filter(id=login_id, status_flag=1, brand_id=brandid)
            
            customer_count = LoyaltyCustomers.objects.filter(brand_id=brandid, status_flag=1).count()

            locations_count = LocationMst.objects.filter(brand_id=brandid, status_flag=1).count()

            earn_points_total = LoyaltyTrans.objects.filter(brand_id=brandid, bill_trans_type="Earn", status_flag=1).aggregate(total=Sum('points'))['total']

            redeem_points_total = LoyaltyTrans.objects.filter(brand_id=brandid, bill_trans_type="Redeem", status_flag=1).aggregate(total=Sum('points'))['total']

            #if len(customer_count) > 0:
            #if len(user_dtls) > 0:
            #    loggedin_user_name = user_dtls[0].firstname
            #    loggedin_user_email = user_dtls[0].email
            
            resp_data = {'total_locations':locations_count,'total_customers':customer_count,'earn_points_total':earn_points_total,'redeem_points_total':redeem_points_total}

            return render(request,"dashboard.html",resp_data)
        except Exception as e:
                return render(request,"dashboard.html",{"message": "No data available  ({e})", "status": True})


class AddProgramSetup(TemplateView):

    def get(self, request):
        brand_id=request.session.get("brand_id")
        Progsettings = get_object_or_404(TblSettings, global_brandid=brand_id, status_flag=1)
        return render(request,"pages/forms/program_setup.html",{'Progsettings': Progsettings})
    
    def post(self, request):

        if request.method == 'POST':
            # Get data from POST request
            program_name = request.POST.get('program_name')
            mall_name = request.POST.get('mall_name')
            program_url = request.POST.get('program_url')
            program_name_sms = request.POST.get('program_name_sms')
            sender_id = request.POST.get('senderid')
            earn_pts_logic = request.POST.get('earnlogic')

            #print(sender_id)
                        
            # Get the uploaded logo file from FILES
            program_logo = request.FILES.get('program_logo')
            brand_id=request.session.get("brand_id")

            #print(brand_id)

            #print(program_logo)

            try:

                Progsettings = get_object_or_404(TblSettings, global_brandid=brand_id, status_flag=1)

                # Validate the fields (you can add custom validation as needed)
                if program_name and program_url and sender_id and program_name_sms:
                    # Handle file upload using FileSystemStorage

                    if program_logo:
                        upload_dir1 = 'media/brands/'
                        upload_dir = os.path.join(settings.MEDIA_ROOT, 'brands')
                        #print(upload_dir)
                        fs = FileSystemStorage(location=upload_dir)
                        filename = fs.save(program_logo.name, program_logo)
                        #print(filename)
                        #program_logo_filename = fs.url(upload_dir, filename)
                        program_logo_filename = os.path.join(upload_dir1, filename)
                        #print(os.path.join(upload_dir, program_logo))
                    else:
                        program_logo_filename = TblSettings.objects.filter(global_brandid=brand_id, status_flag=1).values_list('logo_img_name', flat=True).first()
                        if not program_logo_filename:
                            program_logo_filename = ""


                    Progsettings.header_name = program_name
                    Progsettings.brand_name = mall_name
                    Progsettings.brand_url = program_url
                    Progsettings.sender_id = sender_id
                    Progsettings.brand_sms = program_name_sms
                    Progsettings.logo_img_name = program_logo_filename
                    Progsettings.earn_points_logic = earn_pts_logic
                    
                    Progsettings.save()  # Save to the database

                    return render(request,"pages/forms/program_setup.html",{"Progsettings": Progsettings, "message": "Program setup details updated successfully", "status": True})
                else:
                    return render(request,"pages/forms/program_setup.html",{"Progsettings": Progsettings, "message": "Mandatory fields can't be blank.", "status": True})
            except Exception as e:
                return render(request,"pages/forms/program_setup.html",{"Progsettings": Progsettings, "message": "Error : ({e})", "status": True})


class SettingsLogicConfig(TemplateView):

    def get(self, request):
        tb = request.GET.get('tb', '')
        brand_id=request.session.get("brand_id")
        
        brands = RewardBrandsMst.objects.filter(brand_id=brand_id, status_flag=1).order_by('rwrd_brand_name')

        percentptstiers = Tiers.objects.filter(brand_id=brand_id, status_flag=1, tier_logic_type='Percent Points').values('tier_id','tier_name','tier_minimum_value','tier_maximum_value','tier_discount','tier_type','tier_logic_type').order_by('tier_minimum_value')
        pptr_data = list(percentptstiers)
        pptr_json_data = json.dumps(pptr_data)

        ptsperspendtiers = Tiers.objects.filter(brand_id=brand_id, status_flag=1, tier_logic_type='Points Per Spend').values('tier_id','tier_name','tier_minimum_value','tier_maximum_value','tier_earn_points','tier_pts_per_rs','tier_type','tier_logic_type').order_by('tier_minimum_value')
        ppstr_data = list(ptsperspendtiers)
        ppstr_json_data = json.dumps(ppstr_data)

        return render(request,"pages/forms/logic-configuration.html",{'brands':brands,'Ptsprcnttiers':pptr_json_data,'Ptsperspendtiers':ppstr_json_data,'tb':tb})



class AddTier(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/logic-configuration.html")
    def post(self, request):

        data = request.POST
        
        tier_name = data.get("tier_name")
        tier_logic_type = data.get("tier_logic_type")
        tier_min_amt = data.get("tier_min_amt")
        tier_max_amt = data.get("tier_max_amt")
        tier_percent = data.get("tier_percent")
        tier_earn_pts = data.get("tier_earn_pts")
        tier_pts_per_rs = data.get("tier_pts_per_rs")
        if tier_logic_type == "Percent Points":
            tier_type = data.get("tier_type")
        else:
            tier_type = data.get("tier_type1")
        rwrd_brand_id = data.get("selbrands")
        
        brand_id=request.session.get("brand_id")

        if tier_logic_type == "Percent Points":
            tabKeyVal = "tab1"
        elif tier_logic_type == "Points Per Spend":
            tabKeyVal = "tab2"    
        else:
            tabKeyVal = "tab1"

        #print(rwrd_brand_id)
        #print(tabKeyVal)
       
        if rwrd_brand_id == '':
            rwrd_brand_id = None

        try: 
            TblRequestAuditLogs.objects.create(tier_name=tier_name,tier_type=tier_type,tier_logic_type=tier_logic_type,tier_minimum_value=tier_min_amt,tier_maximum_value=tier_max_amt,points=tier_percent,tier_earn_points=tier_earn_pts,tier_pts_per_rs=tier_pts_per_rs,mall_brand_id=rwrd_brand_id,brand_id=brand_id,api_flag='Add Tier')
        except ValueError as e:
            #logger.error("Error saving TblRequestAuditLogs entry: %s", e)
            messages.error(request, "An error occurred while saving audit logs.")
            return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
        
        try:
            tier_min_amt = float(tier_min_amt)
            tier_max_amt = float(tier_max_amt)
        except ValueError as e:
            #logger.error("Error converting tier amounts: %s", e)
            messages.error(request, "Tier amounts must be valid numbers.")
            return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
        
        try:
            if pd.isnull(brand_id) or brand_id == '':
                #return render(request, "pages/forms/logic-configuration.html", {'message': 'brand id should not be empty..!', "status": False})
                messages.error(request, "brand id should not be empty..!")               
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
            elif not tier_name:
                #return render(request, "pages/forms/logic-configuration.html", {'message': 'Tier name is required.', "status": False})
                messages.error(request, "Tier name is required.")               
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
            elif tier_min_amt is None or tier_max_amt is None or tier_min_amt > tier_max_amt:
                #return render(request, "pages/forms/logic-configuration.html", {'message': 'Minimum amount cannot be greater than maximum amount.', "status": False})
                messages.error(request, "Minimum amount cannot be greater than maximum amount.")               
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
            elif tier_type == 'brand' and not rwrd_brand_id:
                #return render(request, "pages/forms/logic-configuration.html", {'message': 'Please select a brand if type is ''Brand''.', "status": False})
                messages.error(request, "Please select a brand if type is ''Brand''.")               
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
            elif Tiers.objects.filter(tier_name=tier_name, brand_id=brand_id, tier_logic_type=tier_logic_type, tier_type=tier_type, status_flag=1).exists():
                #return render(request, "pages/forms/logic-configuration.html", {'message': 'Tier Name already exists.', "status": False})
                messages.error(request, "Tier Name already exists.")               
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
            elif Tiers.objects.filter(tier_minimum_value__lte=tier_max_amt,tier_maximum_value__gte=tier_min_amt, brand_id=brand_id, tier_logic_type=tier_logic_type, tier_type=tier_type, status_flag=1).exists():
                #return render(request, "pages/forms/logic-configuration.html", {'message': 'The tier range overlaps with an existing tier.', "status": False})
                messages.error(request, "The tier range overlaps with an existing tier.")               
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
            elif tier_logic_type == "Percent Points":
                Tiers.objects.create(tier_name=tier_name,tier_logic_type=tier_logic_type,tier_minimum_value=tier_min_amt,tier_maximum_value=tier_max_amt,tier_discount=tier_percent,tier_type=tier_type,tier_earn_points=tier_earn_pts,tier_pts_per_rs=tier_pts_per_rs,brand_id=brand_id,rwrd_brand_id_id=rwrd_brand_id)
                messages.success(request, "Tier added successfully")               
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
            elif tier_logic_type == "Points Per Spend":
                #print("Points Pper spend tier added successfully.")
                Tiers.objects.create(tier_name=tier_name,tier_logic_type=tier_logic_type,tier_minimum_value=tier_min_amt,tier_maximum_value=tier_max_amt,tier_discount=tier_percent,tier_type=tier_type,tier_earn_points=tier_earn_pts,tier_pts_per_rs=tier_pts_per_rs,brand_id=brand_id,rwrd_brand_id_id=rwrd_brand_id)
                #return render(request, "pages/forms/logic-configuration.html", {"message2": "Tier added successfully", "status": True})
                messages.success(request, "Tier added successfully")               
                #return redirect("LogicConfig?tb=tab2")
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
            else:
                #print("Invalid Logic Type.")
                messages.error(request, "Invalid Logic type")               
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
        
        except ValueError as e:
            #logger.error("Error during validation checks: %s", e)
            messages.error(request, f"An error occurred during validation checks ({e})")
            return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)

        #except Exception as e:
        #    messages.error(request, f"Tier not added ({e})")
        #    return redirect("LogicConfig")
            #return render(request, "pages/forms/logic-configuration.html", {"message": f"Tier not added ({e})", "status": True})

class DeleteTier(TemplateView):
    def post(self, request):
        if request.method == 'POST':
            data = request.POST
            #data = json.loads(request.body)
            tier_id = data.get("tierid")
            brand_id=request.session.get("brand_id")
            login_id=request.session.get("loginid")
            #print(tier_id)
            
            TblRequestAuditLogs.objects.create(tier_id=tier_id,brand_id=brand_id,api_flag='Delete Tier')

            if tier_id:
                Tiers.objects.filter(brand_id=brand_id, tier_id=tier_id, status_flag=1).update(status_flag=0, deactivated_on=timezone.now(),deactivated_by=login_id)
                return JsonResponse({"success": True, "message": "Tier deleted successfully"})
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)
    
class GetTierDetails(TemplateView):
    def post(self, request):
        if request.method == 'POST':
            
            #data = request.POST
            #print(data)
            data = json.loads(request.body)
            #print(data)
            tier_id = data.get("tierid")
            brand_id=request.session.get("brand_id")
            #print(tier_id)
            #print(brand_id)

            TblRequestAuditLogs.objects.create(tier_id=tier_id,brand_id=brand_id,api_flag='Get Tier')
            
            tier = get_object_or_404(Tiers, tier_id=tier_id, brand_id=brand_id, status_flag=1)
            
            data = {
                "tier_id": tier.tier_id,
                "tier_name": tier.tier_name,
                "tier_minimum_value": tier.tier_minimum_value,
                "tier_maximum_value": tier.tier_maximum_value,
                "tier_type": tier.tier_type,
                "tier_logic_type": tier.tier_logic_type,
                "tier_discount": tier.tier_discount,
                "tier_earn_points": tier.tier_earn_points,
                "tier_pts_per_rs": tier.tier_pts_per_rs,
                "rwrd_brand_id": tier.rwrd_brand_id.id if tier.rwrd_brand_id else None,
            }
            print(data)
            return JsonResponse(data, safe=False)
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)
    

class EditTier(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/logic-configuration.html")
    def post(self, request):

        data = request.POST
        
        tabKeyVal = data.get("modal_tabKey")
        modal_index = data.get("modal_index")
        tier_id = data.get("modal_tierId")
        tier_name = data.get("modal_tiername")
        tier_logic_type = data.get("modal_tierlogictype")
        tier_min_amt = data.get("modal_tierMinAmt")
        tier_max_amt = data.get("modal_tierMaxAmt")
        tier_percent = data.get("modal_tierpercent")
        tier_earn_pts = data.get("modal_tierearnpts")
        tier_pts_per_rs = data.get("modal_tierptsperrs")
        tier_type = data.get("modal_tiertype")
        rwrd_brand_id = data.get("modal_rwrdbrandid")
        
        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

        #print(rwrd_brand_id)
       
        if rwrd_brand_id == '':
            rwrd_brand_id = None

        try: 

            TblRequestAuditLogs.objects.create(tier_id=tier_id,period=tabKeyVal,resource_name=modal_index,tier_name=tier_name,tier_type=tier_type,tier_logic_type=tier_logic_type,tier_minimum_value=tier_min_amt,tier_maximum_value=tier_max_amt,points=tier_percent,tier_earn_points=tier_earn_pts,tier_pts_per_rs=tier_pts_per_rs,mall_brand_id=rwrd_brand_id,brand_id=brand_id,api_flag='Edit Tier')
        except ValueError as e:
            #logger.error("Error saving TblRequestAuditLogs entry: %s", e)
            messages.error(request, "An error occurred while saving audit logs.")
            return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)

        try:    
            tier_min_amt = float(tier_min_amt)
            tier_max_amt = float(tier_max_amt)
        except ValueError as e:
            #logger.error("Error converting tier amounts: %s", e)
            messages.error(request, "Tier amounts must be valid numbers.")
            return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
        
        try:
            if pd.isnull(brand_id) or brand_id == '':
                #return render(request, "pages/forms/logic-configuration.html", {'message': 'brand id should not be empty..!', "status": False})
                messages.error(request, "brand id should not be empty..!")               
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
            elif not tier_name:
                messages.error(request, "Tier name is required.")               
                #print("A")
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
            elif tier_min_amt is None or tier_max_amt is None or tier_min_amt > tier_max_amt:
                messages.error(request, "Minimum amount cannot be greater than maximum amount.")               
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
                #print("B")
            elif tier_type == 'brand' and not rwrd_brand_id:
                messages.error(request, "Please select a brand if type is ''Brand''.")               
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
                #print("C")
            elif Tiers.objects.filter(tier_name=tier_name,brand_id=brand_id,tier_logic_type=tier_logic_type,tier_type=tier_type,status_flag=1).exclude(tier_id=tier_id).exists():
                messages.error(request, "Tier Name already exists.")               
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
                #print("D")
            elif Tiers.objects.filter(tier_minimum_value__lte=tier_max_amt,tier_maximum_value__gte=tier_min_amt,brand_id=brand_id,tier_logic_type=tier_logic_type,tier_type=tier_type,status_flag=1).exclude(tier_id=tier_id).exists():
                messages.error(request, "The tier range overlaps with an existing tier.")
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
                #print("E")
            elif tier_logic_type is not None and tier_logic_type != '':
                Tiers.objects.filter(brand_id=brand_id, tier_id=tier_id, status_flag=1).update(tier_name=tier_name,tier_logic_type=tier_logic_type,tier_minimum_value=tier_min_amt,tier_maximum_value=tier_max_amt,tier_discount=tier_percent,tier_type=tier_type,tier_earn_points=tier_earn_pts,tier_pts_per_rs=tier_pts_per_rs,rwrd_brand_id=rwrd_brand_id,updated_on=timezone.now(),updated_by=login_id)
                messages.success(request, "Tier modified successfully")               
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
            else:
                messages.error(request, "Invalid Logic type")               
                return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
                #print("F")
    
        except ValueError as e:
            #logger.error("Error during validation checks: %s", e)
            messages.error(request, "An error occurred during validation checks.")
            return redirect(reverse('LogicConfig') + '?tb='+tabKeyVal)
            
def earn_points_logic(data,brand_id,source,login_id):
    mobileno = data['mobile_number']
    bill_number = data['bill_number']
    bill_amount = data['bill_amount']
    bill_date = data['bill_date']
    if source == "API":
        #rwrd_brand = data['brand']
        #category = data['category']
        location = data['location']
    else:
        #rwrd_brand = ''
        #category = ''
        location = ''

    if source == "Platform":
        #cat_id = data['category_id']
        #rwrdbrandid = data['rwrdbrandid']
        loc_id = data['loc_id']
        bill_file = data['bill_file']
    else:
        #cat_id = ''
        #rwrdbrandid = ''
        loc_id = ''
        bill_file = ''

    try:

        TblRequestAuditLogs.objects.create(mobileno=mobileno,bill_number=bill_number,bill_amount=bill_amount,bill_date=bill_date,brand_id=brand_id,resource_name=bill_file,reg_source=source,api_flag='Bill Upload')

        msg = mobile_number_validation(mobileno, brand_id)
        #print(message)
        if msg:
            return Response({'message': msg, "status": False})
        if pd.isnull(bill_number) or bill_number == '' or bill_number == None:
            return Response({'message': 'Bill number can''t be blank..!', "status": False})
        if pd.isnull(bill_amount) or bill_amount == '' or bill_amount == None:
            return Response({'message': 'Bill amount can''t be blank..!', "status": False})
        if pd.isnull(bill_date) or bill_date == '' or bill_date == None:
            return Response({'message': 'Bill date can''t be blank..!', "status": False})
        #if source == "API":
        #    if pd.isnull(rwrd_brand) or rwrd_brand == '' or rwrd_brand == None:
        #        return Response({'message': 'Reward brand can''t be blank..!', "status": False})
        if pd.isnull(brand_id) or brand_id == '' or brand_id == None:
            return Response({'message': 'Brand id should not be empty..!', "status": False})
        if not LoyaltyCustomers.objects.filter(mobileno=mobileno, brand_id=brand_id, status_flag=1).exists():
            return Response({'message': "Mobile number is not registered with us!!", "status": False})
        if LoyaltyCustomers.objects.filter(mobileno=mobileno, brand_id=brand_id, status_flag=0).exists():
            return Response({"message": "Mobile number is deactivated!!", "status": False})
        #if not rwrdbrandid:
        #    rwrd_brand_id = RewardBrandsMst.objects.filter(rwrd_brand_identifier=rwrd_brand).values_list('id', flat=True).first()
        #else:
        #    rwrd_brand_id = rwrdbrandid
        #if not rwrd_brand_id:
        #    return Response({'message': 'Brand doesn''t match..!', "status": False})
        if not loc_id:
            location_id = LocationMst.objects.filter(location_code=location,brand_id=brand_id,status_flag=1).values_list('location_id', flat=True).first()
        else:
            location_id = loc_id
        if not location_id:
            return Response({'message': 'Location doesn''t match..!', "status": False})
        
        if LoyaltyTrans.objects.filter(bill_number=bill_number, bill_date=bill_date, location_id=location_id,bill_status="New",bill_trans_type="Earn", status_flag=1).exists():
            return Response({'message': "Bill already exists!!", "status": False})
        
        #gb_brand_data = global_brand_data(brand_id)

        #print(gb_brand_data)

        gb_brand_data = TblSettings.objects.filter(global_brandid=brand_id)

        if len(gb_brand_data) > 0:
            brand_earn_points_logic = gb_brand_data[0].earn_points_logic
        #print(brand_earn_points_logic)

        points_data = LoyaltyPoints.objects.filter(mobileno=mobileno,brand_id=brand_id,status_flag=1)

        if len(points_data) > 0:
            existing_tier_id = points_data[0].tier_id
            existing_bal_points = points_data[0].bal_points
            tier_upgrade_date = points_data[0].tier_upgrade_date
        
        if existing_tier_id is None or existing_tier_id == '' or existing_tier_id == NULL:
            existing_tier_id=0

        #print(existing_tier_id)

        total_bill_amount = LoyaltyTrans.objects.filter(mobileno=mobileno,brand_id=brand_id,status_flag=1,bill_trans_type='Earn').aggregate(total=Sum('bill_amount'))['total']

        if total_bill_amount is None:
            total_bill_amount=0

        final_total_bill_amount = float(total_bill_amount) + float(bill_amount)

        #print(final_total_bill_amount)

        #brand_tier_chk = Tiers.objects.filter(brand_id=brand_id, tier_logic_type=brand_earn_points_logic, status_flag=1, rwrd_brand_id=rwrd_brand_id, tier_minimum_value__lte=final_total_bill_amount, tier_maximum_value__gte=final_total_bill_amount)

        #if len(brand_tier_chk) > 0:
        #    tiers_data = Tiers.objects.filter(brand_id=brand_id, tier_logic_type=brand_earn_points_logic, status_flag=1, tier_type='brand', rwrd_brand_id=rwrd_brand_id, tier_minimum_value__lte=final_total_bill_amount, tier_maximum_value__gte=final_total_bill_amount)
        #else:
        tiers_data = Tiers.objects.filter(brand_id=brand_id, tier_logic_type=brand_earn_points_logic, status_flag=1, tier_type='regular', tier_minimum_value__lte=final_total_bill_amount, tier_maximum_value__gte=final_total_bill_amount)

        if len(tiers_data) > 0:
            tier_percent = tiers_data[0].tier_discount
            tier_earn_points = tiers_data[0].tier_earn_points
            tier_pts_per_rs = tiers_data[0].tier_pts_per_rs
            tier_id = tiers_data[0].tier_id

        cust_tier_id = Tiers.objects.filter(brand_id=brand_id, tier_logic_type=brand_earn_points_logic, status_flag=1, tier_type='regular', tier_minimum_value__lte=final_total_bill_amount, tier_maximum_value__gte=final_total_bill_amount).values_list('tier_id', flat=True).first()

        #print(cust_tier_id)

        earn_points=0
        if brand_earn_points_logic == "Percent Points":
            earn_points=float(bill_amount)*float(tier_percent)/100
        elif brand_earn_points_logic == "Points Per Spend":
            earn_pts_no=float(bill_amount)//float(tier_pts_per_rs)
            earn_points=float(earn_pts_no)*float(tier_earn_points)
        else:
            earn_points=0
        
        #print(earn_points)
        
        bal_points_aft_trans = existing_bal_points + earn_points

        with transaction.atomic():
            transaction_entry = LoyaltyTrans.objects.create(
                mobileno=mobileno,
                brand_id=brand_id,
                bill_number=bill_number,
                bill_amount=bill_amount,
                bill_date=bill_date,
                #rwrd_brand_id_id=rwrd_brand_id,
                location_id_id=location_id,
                points=earn_points,
                bill_status='New',
                tier_id=tier_id,
                tier_percent=tier_percent,
                tier_earn_pts=tier_earn_points,
                billamt_for_pts_issue=bill_amount,
                bal_points_bef_trans=existing_bal_points,
                bal_points_aft_trans=bal_points_aft_trans,
                bill_trans_type="Earn",
                upload_file_name=bill_file,
                trans_source=source
            )

            if int(existing_tier_id) != int(cust_tier_id):
                TierUpgradedata.objects.create(mobileno=mobileno,brand_id=brand_id,prev_tierid=existing_tier_id,new_tierid=cust_tier_id,bill_number=bill_number,bill_amount=bill_amount,bill_date=bill_date,location_id=location_id)
                tier_upgrade_date=timezone.now()

            # Update PointsMaster table
            points_master, created = LoyaltyPoints.objects.get_or_create(mobileno=mobileno,brand_id=brand_id,status_flag=1)
            points_master.bal_points = round(points_master.bal_points + earn_points, 2)
            points_master.updated_on = timezone.now()
            points_master.tier_id_id = cust_tier_id
            points_master.last_trans_date=timezone.now()
            points_master.tot_cust_purchase=final_total_bill_amount
            points_master.tot_cust_new_purchase=final_total_bill_amount
            points_master.tot_cust_bills += 1
            points_master.tot_cust_earnpoints = round(points_master.tot_cust_earnpoints + earn_points, 2)
            tier_upgrade_date=tier_upgrade_date
            points_master.save()

            #smsmsg = config_Transaction_Pts_SMS_text

            gfb = global_brand_data(brand_id)
            gfb_cached_data2 = gfb.get('cached_data2', [])
            
            config_Transaction_Earn_Pts_Template_text = next(
            (template['template_text'] for template in gfb_cached_data2 if template['template_flag'] == 'Earn'),
            None  # Default to None if no match is found
            )

            smsmsg = config_Transaction_Earn_Pts_Template_text

            smsmsg_ = smsmsg.replace("[$epts$]",str(earn_points))
            sms_msg = smsmsg_.replace("[$Blpts$]",str(points_master.bal_points))

            sms_api_response = SingleSMSBroadcastApi.smssend("Earn", brand_id, login_id, mobileno, sms_msg, "Trans",bill_date,bill_number,bill_amount,location_id,"")    
        
        #reward_brand_name = RewardBrandsMst.objects.filter(id=rwrd_brand_id).values_list('rwrd_brand_name', flat=True).first()

        if source == "API":
            return Response({'message': f"Thank you, Your bill has been processed successfully & you've earned {earn_points} points your updated Balance points are {points_master.bal_points}", "status": False,"transaction_id":data['bill_number'], "earn_points": earn_points, "total_points": points_master.bal_points})
        else:
            return Response({'message': f"Bill processed successfully and customer earned {earn_points} points against the transaction. Balance points are {points_master.bal_points}", "status": False,"transaction_id":data['bill_number'], "earn_points": earn_points, "total_points": points_master.bal_points})
        #return {
        #    "message": "Request received and Points earned successfully",
        #    "transaction_id": data['bill_number'],
        #    "earn_points": earn_points,
        #    "total_points": points_master.bal_points
        #}
    except Exception as e:
        return Response({'message': f"An error occurred during validation or calculation ({e})", "status": False})
    

class EnterBillView(TemplateView):
    def get(self, request):
        #categories = CategoryMst.objects.all().order_by('category_name')
        #brands = RewardBrandsMst.objects.all().order_by('rwrd_brand_name')
        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")
        role_id=request.session.get("roleid")
        if role_id == 1:
            locations = LocationMst.objects.filter(brand_id=brand_id,status_flag=1).order_by('location_Name')
        else:
            loc_id = MstUserLogins.objects.filter(brand_id=brand_id, id=login_id, status_flag=1).values_list('locationid', flat=True).first()
            locations = LocationMst.objects.filter(location_id=loc_id,brand_id=brand_id,status_flag=1).order_by('location_Name')
        return render(request,"pages/forms/enter-bill.html",{"locations":locations})
    def post(self, request):
        
        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")
        role_id=request.session.get("roleid")
        if role_id == 1:
            locations = LocationMst.objects.filter(brand_id=brand_id,status_flag=1).order_by('location_Name')
        else:
            loc_id = MstUserLogins.objects.filter(brand_id=brand_id, id=login_id, status_flag=1).values_list('locationid', flat=True).first()
            locations = LocationMst.objects.filter(location_id=loc_id,brand_id=brand_id,status_flag=1).order_by('location_Name')
        
        data = request.POST
        mobileno = data.get("mobile_number")
        bill_number = data.get("bill_number")
        bill_date = data.get("bill_date")
        bill_amount = data.get("bill_amount")
        #category_id = data.get("selcategory")
        #rwrd_brand_id = data.get("selbrand")
        location_id = data.get("sellocation")
        upload_bill_file = request.FILES.get("bill_file")

        if upload_bill_file:
            upload_dir1 = 'media/billscans/'

            upload_dir = os.path.join(settings.MEDIA_ROOT, 'billscans')
            fs = FileSystemStorage(location=upload_dir)
            filename = fs.save(upload_bill_file.name, upload_bill_file)
            bill_file = os.path.join(upload_dir1, filename)
        else:
            bill_file = None

        if not location_id:
            location_id = loc_id

        #categories = CategoryMst.objects.all().order_by('category_name')
        #brands = RewardBrandsMst.objects.all().order_by('rwrd_brand_name')
        
        

        validated_data = {
            'mobile_number': mobileno,
            'bill_number': bill_number,
            'bill_amount': bill_amount,
            'bill_date': bill_date,
            #'category_id': category_id,
            #'rwrdbrandid': rwrd_brand_id,
            'bill_file': bill_file,
            'loc_id': location_id,
        }

        result = earn_points_logic(validated_data,brand_id,'Platform',login_id)

        return render(request,"pages/forms/enter-bill.html",{'message': result.data.get("message"), "status": False, "locations":locations})
    
class CustomerDetailsView(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/customer-details.html",{"customerdata":'',"transdata":''})
    def post(self, request):
        #print("mobile number")
        data = request.POST
        mobileno = data.get("mobile_number")
        #print("mobile number")
        #print(mobileno)
        brand_id=request.session.get("brand_id")
        customerdata = LoyaltyCustomers.objects.select_related('location_id','mall_brand_id','city','state','country').filter(mobileno=mobileno,brand_id=brand_id,status_flag=1)
        #print(len(customerdata))
        if len(customerdata) <= 0:
            return render(request,"pages/forms/customer-details.html",{"customerdata":customerdata,"message":"No customer found."})
          
        pointsdata = LoyaltyPoints.objects.select_related('tier_id').filter(mobileno=mobileno,brand_id=brand_id,status_flag=1)
        #print(customerdata.query)
        transdata = LoyaltyTrans.objects.select_related('location_id','rwrd_brand_id').filter(mobileno=mobileno,brand_id=brand_id,status_flag=1).order_by('-created_on')
        return render(request,"pages/forms/customer-details.html",{"customerdata":customerdata,"transdata":transdata,"pointsdata":pointsdata})

class SendSMSView(TemplateView):
    def get(self, request):
        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")
        msg = config_Registration_SMS_text
        encode_msg = urllib.parse.quote_plus(msg)
        sms_api_response = SingleSMSBroadcastApi.smssend("Reg", brand_id, login_id, "919910049864", msg, "Registration","","","","","")
        return JsonResponse(sms_api_response)



""" 
def upload_bill(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("bill_image")
        if uploaded_file:
            # Save the uploaded file temporarily
            with open(f"media/billscans/{uploaded_file.name}", "wb") as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)

            # Perform OCR and parse the bill
            ocr_text = extract_text_from_image(f"media/billscans/{uploaded_file.name}")
            print(ocr_text)
            bill_details = parse_bill_text(ocr_text)

            return render(request, "pages/forms/upload_bill.html", {"bill_details": bill_details})

    return render(request, "pages/forms/upload_bill.html") 
"""

class SettingsRwrdCategoriesView(TemplateView):

    def get(self, request):
        brand_id=request.session.get("brand_id")
        
        categories = CategoryMst.objects.filter(brand_id=brand_id, status_flag=1).values('category_id','category_name','category_description','category_icon','category_img').order_by('created_on')
        category_data = list(categories)
        category_json_data = json.dumps(category_data)

        return render(request,"pages/forms/settings_rwrd_categories.html",{'rwrdcategories':category_json_data})


class DeleteRwrdCategory(TemplateView):
    def post(self, request):
        if request.method == 'POST':
            data = request.POST
            #data = json.loads(request.body)
            rwrd_cat_id = data.get("catid")
            brand_id=request.session.get("brand_id")
            login_id=request.session.get("loginid")
            #print(tier_id)
            
            TblRequestAuditLogs.objects.create(category_code=rwrd_cat_id,brand_id=brand_id,api_flag='Delete Reward Category')

            if rwrd_cat_id:
                CategoryMst.objects.filter(brand_id=brand_id, category_id=rwrd_cat_id, status_flag=1).update(status_flag=0, updated_on=timezone.now(),updated_by=login_id)
                return JsonResponse({"success": True, "message": "Reward Category deleted successfully"})
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)
    
class GetRwrdCategoryDetails(TemplateView):
    def post(self, request):
        if request.method == 'POST':
            
            #data = request.POST
            #print(data)
            data = json.loads(request.body)
            print(data)
            rwrd_cat_id = data.get("catid")
            brand_id=request.session.get("brand_id")
            #print(tier_id)
            #print(brand_id)

            TblRequestAuditLogs.objects.create(category_code=rwrd_cat_id,brand_id=brand_id,api_flag='Get Reward Category details')
            
            cat = get_object_or_404(CategoryMst, category_id=rwrd_cat_id, brand_id=brand_id, status_flag=1)
            
            data = {
                "category_id": cat.category_id,
                "category_name": cat.category_name,
                "category_description": cat.category_description,
                "category_img": cat.category_img,
                "category_icon": cat.category_icon,
            }
            #print(data)
            return JsonResponse(data, safe=False)
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)


class EditRwrdCategory(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/settings_rwrd_categories.html")
    def post(self, request):

        data = request.POST
        
        tabKeyVal = data.get("modal_tabKey")
        modal_index = data.get("modal_index")
        rwrd_category_id = data.get("modal_category_id")
        rwrd_category_name = data.get("modal_category_name")
        rwrd_category_desc = data.get("modal_category_description")
        
        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

       
        try: 

            TblRequestAuditLogs.objects.create(category_code=rwrd_category_id,period=tabKeyVal,resource_name=modal_index,location_category_name=rwrd_category_name,comments=rwrd_category_desc,brand_id=brand_id,api_flag='Edit Reward Category')
        except ValueError as e:
            #logger.error("Error saving TblRequestAuditLogs entry: %s", e)
            messages.error(request, "An error occurred while saving audit logs.")
            return redirect(reverse('RwrdCategories'))

        try:
            if pd.isnull(brand_id) or brand_id == '':
                #return render(request, "pages/forms/logic-configuration.html", {'message': 'brand id should not be empty..!', "status": False})
                messages.error(request, "brand id should not be empty..!")               
                return redirect(reverse('RwrdCategories'))
            elif not rwrd_category_name:
                messages.error(request, "Reward Category name is required.")               
                #print("A")
                return redirect(reverse('RwrdCategories'))
            elif CategoryMst.objects.filter(category_name=rwrd_category_name,brand_id=brand_id,status_flag=1).exclude(category_id=rwrd_category_id).exists():
                messages.error(request, "Reward Category name already exists.")               
                return redirect(reverse('RwrdCategories'))
                #print("D")
            else:
                CategoryMst.objects.filter(brand_id=brand_id, category_id=rwrd_category_id, status_flag=1).update(category_name=rwrd_category_name,category_description=rwrd_category_desc,updated_on=timezone.now(),updated_by=login_id)
                messages.success(request, "Reward Category modified successfully")               
                return redirect(reverse('RwrdCategories'))
            
    
        except ValueError as e:
            #logger.error("Error during validation checks: %s", e)
            messages.error(request, "An error occurred during validation checks.")
            return redirect(reverse('RwrdCategories'))

#UPLOAD_PROGRESS = {"total": 0, "completed": 0}


class ImportRwrdCategory(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/settings_rwrd_categories.html")
    def post(self, request):

        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

        if request.method == 'POST' and request.FILES['categoryfile']:
            categoryfile = request.FILES['categoryfile']
            rejected_records = []
            success_count = 0
            
            upload_dir1 = 'media/categories_files/'

            upload_dir = os.path.join(settings.MEDIA_ROOT, 'categories_files')
            fs = FileSystemStorage(location=upload_dir)
            filename = fs.save(categoryfile.name, categoryfile)
            categoryfile_filename = os.path.join(upload_dir, filename)
            with open(categoryfile_filename, 'wb') as f:
                for chunk in categoryfile.chunks():
                    f.write(chunk)

            #print(categoryfile_filename)

            if categoryfile.name.endswith('.csv'):
                data = pd.read_csv(categoryfile_filename)
            elif categoryfile.name.endswith('.xlsx'):
                data = pd.read_excel(categoryfile_filename)
            else:
                return JsonResponse({'error': 'Invalid file format. Only CSV and Excel files are allowed.'}, status=400)
            
            data = data.fillna('')

            for _, row in data.iterrows():
                category_name = row.get('category_name', '').strip()  # Assuming 'Category' is the column name
                category_description = row.get('category_description', '').strip()

                if not category_name:
                    rejected_records.append({'row': row.to_dict(), 'reason': 'Blank category value'})
                    continue
                # Check for duplicates
                elif CategoryMst.objects.filter(category_name=category_name).exists():
                    rejected_records.append({'row': row.to_dict(), 'reason': f'Duplicate category: {category_name}'})
                    continue
                else:
                # Save valid records to the database
                    CategoryMst.objects.create(category_name=category_name,category_description=category_description,category_file_name=categoryfile,brand_id=brand_id,user_id=login_id)
                    success_count += 1
            
            rejected_count = len(rejected_records)

            return JsonResponse({'rejected_records': rejected_records,'success_count':success_count,'rejected_count':rejected_count}, status=200)

        #except Exception as e:
        #    return JsonResponse({'error': str(e)}, status=500)

        return render(request,"pages/forms/settings_rwrd_categories.html")
        #return redirect(reverse('RwrdCategories') + '?tb=import')
    


class SettingsRwrdBrandsView(TemplateView):

    def get(self, request):
        brand_id=request.session.get("brand_id")
        
        rwrdbrands = RewardBrandsMst.objects.select_related('category_id').filter(brand_id=brand_id, status_flag=1).values('id','rwrd_brand_name','rwrd_brand_descr','rwrd_brand_floor','rwrd_brand_shopno','category_id','category_id__category_name').order_by('created_on')
        #print(rwrdbrands.query)
        rwrd_brands_data = list(rwrdbrands)
        rwrd_brands_json_data = json.dumps(rwrd_brands_data)

        categoriesdta = CategoryMst.objects.filter(brand_id=brand_id, status_flag=1).values('category_id','category_name').order_by('category_name')

        return render(request,"pages/forms/settings_rwrd_brands.html",{'rwrdbrands':rwrd_brands_json_data,"categoriesdta":categoriesdta})
    

class DeleteRwrdBrand(TemplateView):
    def post(self, request):
        if request.method == 'POST':
            data = request.POST
            #data = json.loads(request.body)
            rwrd_brnd_id = data.get("rbrndid")
            brand_id=request.session.get("brand_id")
            login_id=request.session.get("loginid")
            #print(tier_id)
            
            TblRequestAuditLogs.objects.create(mall_brand_id=rwrd_brnd_id,brand_id=brand_id,api_flag='Delete Reward Brand')

            if rwrd_brnd_id:
                RewardBrandsMst.objects.filter(brand_id=brand_id, id=rwrd_brnd_id, status_flag=1).update(status_flag=0, updated_on=timezone.now(),updated_by=login_id)
                return JsonResponse({"success": True, "message": "Reward Brand deleted successfully"})
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)
    
class GetRwrdBrandDetails(TemplateView):
    def post(self, request):
        if request.method == 'POST':
            
            #data = request.POST
            #print(data)
            data = json.loads(request.body)
            #print(data)
            rwrd_brnd_id = data.get("rbrndid")
            brand_id=request.session.get("brand_id")
            #print(rwrd_brnd_id)
            #print(brand_id)

            TblRequestAuditLogs.objects.create(mall_brand_id=rwrd_brnd_id,brand_id=brand_id,api_flag='Get Reward Brand details')
            
            brnd = get_object_or_404(RewardBrandsMst, id=rwrd_brnd_id, brand_id=brand_id, status_flag=1)
            
            data = {
                "rwrd_brand_id": brnd.id,
                "rwrd_brand_name": brnd.rwrd_brand_name,
                "rwrd_brand_description": brnd.rwrd_brand_descr,
                "rwrd_brand_floor": brnd.rwrd_brand_floor,
                "rwrd_brand_shopno": brnd.rwrd_brand_shopno,
                "rwrd_category_id": brnd.category_id_id,
                "rwrd_brand_identifier": brnd.rwrd_brand_identifier,
                "rwrd_brand_logo": brnd.rwrd_brand_logo,
            }
            #print(data)
            return JsonResponse(data, safe=False)
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)


class EditRwrdBrand(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/settings_rwrd_brands.html")
    def post(self, request):

        data = request.POST
        
        tabKeyVal = data.get("modal_tabKey")
        modal_index = data.get("modal_index")
        rwrd_brand_id = data.get("modal_brand_id")
        rwrd_brand_name = data.get("modal_brand_name")
        rwrd_brand_desc = data.get("modal_brand_description")
        rwrd_brand_floor = data.get("modal_brand_floor")
        rwrd_brand_shopno = data.get("modal_brand_shopno")
        rwrd_brand_catid = data.get("modal_rwrdcategory")
        rwrd_brand_identifier = data.get("modal_brand_identifier")
        rwrd_brand_logo = request.FILES.get("modal_brand_logo")
        
        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

       
        try: 
            TblRequestAuditLogs.objects.create(mall_brand_id=rwrd_brand_id,period=tabKeyVal,resource_name=modal_index,rwrd_brand_name=rwrd_brand_name,comments=rwrd_brand_desc,type=rwrd_brand_floor,location_qrcode=rwrd_brand_shopno,category_code=rwrd_brand_catid,brand_id=brand_id,api_flag='Edit Reward Brand')
        except ValueError as e:
            #logger.error("Error saving TblRequestAuditLogs entry: %s", e)
            messages.error(request, "An error occurred while saving audit logs.")
            return redirect(reverse('RwrdBrands'))

        try:
            if pd.isnull(brand_id) or brand_id == '':
                messages.error(request, "brand id should not be empty..!")               
                return redirect(reverse('RwrdBrands'))
            elif not rwrd_brand_name:
                messages.error(request, "Reward Brand name is required.")               
                return redirect(reverse('RwrdBrands'))
            elif RewardBrandsMst.objects.filter(rwrd_brand_name=rwrd_brand_name,brand_id=brand_id,status_flag=1).exclude(id=rwrd_brand_id).exists():
                messages.error(request, "Reward brand name already exists.")               
                return redirect(reverse('RwrdBrands'))
            else:
                if rwrd_brand_logo:
                    upload_dir1 = 'media/reward_brands/'
                    upload_dir = os.path.join(settings.MEDIA_ROOT, 'reward_brands')
                    fs = FileSystemStorage(location=upload_dir)
                    filename = fs.save(rwrd_brand_logo.name, rwrd_brand_logo)
                    rwrd_brand_logo_filename = os.path.join(upload_dir1, filename)
                else:
                    rwrd_brand_logo_filename = RewardBrandsMst.objects.filter(brand_id=brand_id, id=rwrd_brand_id, status_flag=1).values_list('rwrd_brand_logo', flat=True).first()
                    if not rwrd_brand_logo_filename:
                        rwrd_brand_logo_filename = ""

                RewardBrandsMst.objects.filter(brand_id=brand_id, id=rwrd_brand_id, status_flag=1).update(rwrd_brand_name=rwrd_brand_name,rwrd_brand_descr=rwrd_brand_desc,rwrd_brand_floor=rwrd_brand_floor,rwrd_brand_shopno=rwrd_brand_shopno,rwrd_brand_identifier=rwrd_brand_identifier,category_id_id=rwrd_brand_catid,updated_on=timezone.now(),updated_by=login_id,rwrd_brand_logo=rwrd_brand_logo_filename)
                messages.success(request, "Reward Brand modified successfully")               
                return redirect(reverse('RwrdBrands'))
            
    
        except ValueError as e:
            #logger.error("Error during validation checks: %s", e)
            messages.error(request, "An error occurred during validation checks.")
            return redirect(reverse('RwrdBrands'))

class ImportRwrdBrand(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/settings_rwrd_brands.html")
    def post(self, request):

        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

        if request.method == 'POST' and request.FILES['brandfile']:
            brandfile = request.FILES['brandfile']
            rejected_records = []
            success_count = 0
            
            upload_dir1 = 'media/brand_files/'
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'brand_files')
            fs = FileSystemStorage(location=upload_dir)
            filename = fs.save(brandfile.name, brandfile)
            brandfile_filename = os.path.join(upload_dir, filename)
            with open(brandfile_filename, 'wb') as f:
                for chunk in brandfile.chunks():
                    f.write(chunk)

            #print(categoryfile_filename)

            if brandfile.name.endswith('.csv'):
                data = pd.read_csv(brandfile_filename)
            elif brandfile.name.endswith('.xlsx'):
                data = pd.read_excel(brandfile_filename)
            else:
                return JsonResponse({'error': 'Invalid file format. Only CSV and Excel files are allowed.'}, status=400)

            data = data.fillna('')

            for _, row in data.iterrows():
                rwrd_brand_name = row.get('brand_name', '').strip()  # Assuming 'Category' is the column name
                rwrd_brand_description = row.get('brand_description', '').strip()
                rwrd_brand_floor = row.get('brand_floor', '').strip()
                rwrd_brand_shopno = row.get('brand_shopno', '').strip()
                rwrd_brand_category = row.get('brand_category', '').strip()
                rwrd_brand_identifier = row.get('brand_name_on_bill', '').strip()

                #if isinstance(rwrd_brand_floor, str):
                #    rwrd_brand_floor = rwrd_brand_floor.strip()
                #if isinstance(rwrd_brand_shopno, str):
                #    rwrd_brand_shopno = rwrd_brand_shopno.strip()

                print(rwrd_brand_floor)
                print(rwrd_brand_shopno)

                rwrd_category_id = CategoryMst.objects.filter(category_name=rwrd_brand_category,brand_id=brand_id,status_flag=1).values_list('category_id', flat=True).first()

                if not rwrd_brand_name:
                    rejected_records.append({'row': row.to_dict(), 'reason': 'Blank reward brand name'})
                    continue
                # Check for duplicates
                elif RewardBrandsMst.objects.filter(rwrd_brand_name=rwrd_brand_name,brand_id=brand_id,status_flag=1).exists():
                    rejected_records.append({'row': row.to_dict(), 'reason': f'Duplicate reward brand: {rwrd_brand_name}'})
                    continue
                elif not CategoryMst.objects.filter(category_name=rwrd_brand_category,brand_id=brand_id,status_flag=1).exists():
                    rejected_records.append({'row': row.to_dict(), 'reason': f'Category not found: {rwrd_brand_category}'})
                    continue
                else:
                # Save valid records to the database
                    RewardBrandsMst.objects.create(rwrd_brand_name=rwrd_brand_name,rwrd_brand_descr=rwrd_brand_description,rwrd_brand_floor=rwrd_brand_floor,rwrd_brand_shopno=rwrd_brand_shopno,category_id_id=rwrd_category_id,rwrd_brand_identifier=rwrd_brand_identifier,brand_file_name=brandfile,brand_id=brand_id,user_id=login_id)
                    success_count += 1
            
            rejected_count = len(rejected_records)

            return JsonResponse({'rejected_records': rejected_records,'success_count':success_count,'rejected_count':rejected_count}, status=200)

        #except Exception as e:
        #    return JsonResponse({'error': str(e)}, status=500)

        return render(request,"pages/forms/settings_rwrd_brands.html")
    

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO 8601 string
        return super().default(obj)

class SettingsRwrdGVsView(TemplateView):

    def get(self, request):
        brand_id=request.session.get("brand_id")
        
        rwrdgvs = RewardGiftvouchersMst.objects.select_related('rwrd_brand_id').filter(brand_id=brand_id, status_flag=1).values('id','gv_title','gv_description','gv_value','gv_points_value','gv_expiry','gv_type','gv_mode','rwrd_brand_id__rwrd_brand_name').order_by('created_on')
        #print(rwrdgvs.query)
        rwrd_gvs_data = list(rwrdgvs)
        rwrd_gvs_json_data = json.dumps(rwrd_gvs_data, cls=DateTimeEncoder)

        categoriesdta = CategoryMst.objects.filter(brand_id=brand_id, status_flag=1).values('category_id','category_name').order_by('category_name')

        brandsdta = RewardBrandsMst.objects.filter(brand_id=brand_id, status_flag=1).values('id','rwrd_brand_name').order_by('rwrd_brand_name')

        return render(request,"pages/forms/settings_rwrd_gvs.html",{'rwrdgvs':rwrd_gvs_json_data,"brandsdta":brandsdta,"categoriesdta":categoriesdta})
    

class DeleteRwrdGV(TemplateView):
    def post(self, request):
        if request.method == 'POST':
            data = request.POST
            #data = json.loads(request.body)
            rwrd_gv_id = data.get("rgvid")
            brand_id=request.session.get("brand_id")
            login_id=request.session.get("loginid")
            #print(tier_id)
            
            TblRequestAuditLogs.objects.create(voucher_code=rwrd_gv_id,brand_id=brand_id,api_flag='Delete Reward Mst GV')

            if rwrd_gv_id:
                RewardGiftvouchersMst.objects.filter(brand_id=brand_id, id=rwrd_gv_id, status_flag=1).update(status_flag=0, updated_on=timezone.now(),updated_by=login_id)
                return JsonResponse({"success": True, "message": "Reward Gift Voucher deleted successfully"})
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)
    
class GetRwrdGVDetails(TemplateView):
    def post(self, request):
        if request.method == 'POST':
            
            #data = request.POST
            #print(data)
            data = json.loads(request.body)
            #print(data)
            rwrd_gv_id = data.get("rgvid")
            brand_id=request.session.get("brand_id")
            #print(rwrd_brnd_id)
            #print(brand_id)

            TblRequestAuditLogs.objects.create(voucher_code=rwrd_gv_id,brand_id=brand_id,api_flag='Get Reward GV details')
            
            gv = get_object_or_404(RewardGiftvouchersMst, id=rwrd_gv_id, brand_id=brand_id, status_flag=1)
            
            data = {
                "rwrd_gv_id": gv.id,
                "rwrd_gv_title": gv.gv_title,
                "rwrd_gv_description": gv.gv_description,
                "rwrd_gv_value": gv.gv_value,
                "rwrd_gv_points_value": gv.gv_points_value,
                "rwrd_gv_type": gv.gv_type,
                "rwrd_gv_mode": gv.gv_mode,
                "rwrd_gv_tnc": gv.gv_tnc,
                "rwrd_brand_id": gv.rwrd_brand_id_id,
                "rwrd_gv_identifier": gv.gv_identifier,
            }
            #print(data)
            return JsonResponse(data, safe=False)
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)


class EditRwrdGV(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/settings_rwrd_gvs.html")
    def post(self, request):

        data = request.POST
        
        tabKeyVal = data.get("modal_tabKey")
        modal_index = data.get("modal_index")
        rwrd_gv_id = data.get("modal_gv_id")
        rwrd_gv_title = data.get("modal_gv_title")
        rwrd_gv_desc = data.get("modal_gv_description")
        rwrd_gv_type = data.get("modal_gv_type")
        rwrd_gv_mode = data.get("modal_gv_mode")
        rwrd_gv_value = data.get("modal_gv_value")
        rwrd_gv_points_value = data.get("modal_gv_pts_value")
        rwrd_gv_tnc = data.get("modal_gv_tnc")
        rwrd_brand_id = data.get("modal_rwrd_brand_id")
        rwrd_gv_identifier = data.get("modal_gv_identifier")
        
        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

       
        try: 
            TblRequestAuditLogs.objects.create(mall_brand_id=rwrd_brand_id,period=tabKeyVal,resource_name=modal_index,rwrd_brand_name=rwrd_gv_title,points_desc=rwrd_gv_desc,type=rwrd_gv_type,offer_value_type=rwrd_gv_mode,comments=rwrd_gv_tnc,offer_value=rwrd_gv_value,points=rwrd_gv_points_value,page_source=rwrd_gv_identifier,brand_id=brand_id,api_flag='Edit Reward GV')
        except ValueError as e:
            #logger.error("Error saving TblRequestAuditLogs entry: %s", e)
            messages.error(request, "An error occurred while saving audit logs.")
            return redirect(reverse('RwrdGVs'))

        try:
            if pd.isnull(brand_id) or brand_id == '':
                messages.error(request, "GV id should not be empty..!")               
                return redirect(reverse('RwrdGVs'))
            elif not rwrd_gv_title:
                messages.error(request, "Reward GV title is required.")               
                return redirect(reverse('RwrdGVs'))
            elif RewardGiftvouchersMst.objects.filter(gv_title=rwrd_gv_title,brand_id=brand_id,status_flag=1).exclude(id=rwrd_gv_id).exists():
                messages.error(request, "Reward GV title already exists.")               
                return redirect(reverse('RwrdGVs'))
            else:
                RewardGiftvouchersMst.objects.filter(brand_id=brand_id, id=rwrd_gv_id, status_flag=1).update(gv_title=rwrd_gv_title,gv_description=rwrd_gv_desc,gv_type=rwrd_gv_type,gv_mode=rwrd_gv_mode,gv_tnc=rwrd_gv_tnc,gv_value=rwrd_gv_value,gv_points_value=rwrd_gv_points_value,gv_identifier=rwrd_gv_identifier,rwrd_brand_id_id=rwrd_brand_id,updated_on=timezone.now(),updated_by=login_id)
                messages.success(request, "Reward GV modified successfully")               
                return redirect(reverse('RwrdGVs'))
            
    
        except ValueError as e:
            #logger.error("Error during validation checks: %s", e)
            messages.error(request, "An error occurred during validation checks.")
            return redirect(reverse('RwrdGVs'))

class ImportRwrdGV(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/settings_rwrd_gvs.html")
    def post(self, request):

        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

        if request.method == 'POST' and request.FILES['gvfile']:
            gvfile = request.FILES['gvfile']
            rejected_records = []
            success_count = 0
            
            upload_dir1 = '/media/gv_files/'
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'gv_files')
            fs = FileSystemStorage(location=upload_dir)
            filename = fs.save(gvfile.name, gvfile)
            gvfile_filename = os.path.join(upload_dir, filename)
            with open(gvfile_filename, 'wb') as f:
                for chunk in gvfile.chunks():
                    f.write(chunk)

            #print(categoryfile_filename)

            if gvfile.name.endswith('.csv'):
                data = pd.read_csv(gvfile_filename)
            elif gvfile.name.endswith('.xlsx'):
                data = pd.read_excel(gvfile_filename)
            else:
                return JsonResponse({'error': 'Invalid file format. Only CSV and Excel files are allowed.'}, status=400)

            data = data.fillna('')

            for _, row in data.iterrows():
                rwrd_brand_gv_code = row.get('gv_code', '').strip()  # Assuming 'Category' is the column name
                rwrd_gv_value = row.get('gv_value', '')
                rwrd_gv_points_value = row.get('gv_points_value', '')
                rwrd_gv_mode = row.get('gv_mode', '').strip()
                rwrd_gv_type = row.get('gv_type', '').strip()
                rwrd_brand_name = row.get('gv_brand', '').strip()
                rwrd_gv_exp = row.get('gv_expiry', '')

                try:
                    rwrd_gv_expiry = datetime.strptime(rwrd_gv_exp, "%d-%m-%Y").date()
                except ValueError:
                    return JsonResponse({"error": "Invalid date format. Use DD-MM-YYYY."})
                
                rwrd_brand_id = RewardBrandsMst.objects.filter(rwrd_brand_name=rwrd_brand_name,brand_id=brand_id,status_flag=1).values_list('id', flat=True).first()

                if not rwrd_brand_name:
                    rejected_records.append({'row': row.to_dict(), 'reason': 'Blank reward brand name'})
                    continue
                # Check for duplicates
                elif RewardGiftvouchers.objects.filter(brand_gv_code=rwrd_brand_gv_code,brand_id=brand_id,status_flag=1).exists():
                    rejected_records.append({'row': row.to_dict(), 'reason': f'Duplicate reward GV code: {rwrd_brand_gv_code}'})
                    continue
                elif not RewardBrandsMst.objects.filter(rwrd_brand_name=rwrd_brand_name,brand_id=brand_id,status_flag=1).exists():
                    rejected_records.append({'row': row.to_dict(), 'reason': f'Category not found: {rwrd_brand_name}'})
                    continue
                else:
                # Save valid records to the database
                    RewardGiftvouchers.objects.create(brand_gv_code=rwrd_brand_gv_code,gv_value=rwrd_gv_value,gv_points_value=rwrd_gv_points_value,gv_type=rwrd_gv_type,gv_mode=rwrd_gv_mode,gv_expiry=rwrd_gv_expiry,rwrd_brand_id_id=rwrd_brand_id,issue_flag=1,gv_file_name=gvfile,brand_id=brand_id,user_id=login_id)
                    success_count += 1
            
            rejected_count = len(rejected_records)

            return JsonResponse({'rejected_records': rejected_records,'success_count':success_count,'rejected_count':rejected_count}, status=200)

        #except Exception as e:
        #    return JsonResponse({'error': str(e)}, status=500)

        return render(request,"pages/forms/settings_rwrd_gvs.html")
    

def GetBrandsByCategoryView(request):
    if request.method == "POST":
        category_id = request.POST.get('category_id')

        brand_id=request.session.get("brand_id")

        if not category_id:
            return JsonResponse({'error': 'Category ID is required'}, status=400)

        brands = RewardBrandsMst.objects.filter(category_id=category_id,brand_id=brand_id, status_flag=1).values('id', 'rwrd_brand_name')
        return JsonResponse(list(brands), safe=False)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def GetBrandDenominationView(request):
    if request.method == "POST":
        rwrd_brand_id = request.POST.get('brand_id')
        flag = request.POST.get('flag')

        brand_id=request.session.get("brand_id")

        #today = now().date()

        if not rwrd_brand_id:
            return JsonResponse({'error': 'Reward Brand ID is required'}, status=400)

        if flag == "RD":
            denominations = RewardGiftvouchers.objects.filter(rwrd_brand_id=rwrd_brand_id,brand_id=brand_id, status_flag=1,issue_flag=0,gv_expiry__gte=now()).values('gv_value','gv_points_value').distinct()
        else:
            denominations = RewardGiftvouchers.objects.filter(rwrd_brand_id=rwrd_brand_id,brand_id=brand_id, status_flag=1,issue_flag=1,gv_expiry__gte=now()).values('gv_value','gv_points_value').distinct()
        return JsonResponse(list(denominations), safe=False)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def GetCustomerBalPointsView(request):
    if request.method == "POST":
        mobileno = request.POST.get('mobileno')
        brand_id=request.session.get("brand_id")
        print(mobileno)
        if not mobileno:
            return JsonResponse({'error': 'Mobile Number is required'}, status=400)

        bal_points = LoyaltyPoints.objects.filter(mobileno=mobileno,brand_id=brand_id, status_flag=1).values_list('bal_points', flat=True).first()
        #print(bal_points)
        return JsonResponse({'bal_points': round(bal_points,2)}, safe=False)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


class AssignRwrdGVsToRewardsDesk(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/settings_rwrd_gvs.html")
    def post(self, request):

        data = request.POST
        
        category_id = data.get("selcategory")
        rwrd_brand_id = data.get("selbrand")
        rwrd_gv_points_value = data.get("seldenomination")
        total_rwrd_gvs = data.get("total_vouchers")
        total_gv_value = data.get("total_gv_value")
        
        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

        
       
        try: 
            TblRequestAuditLogs.objects.create(mall_brand_id=rwrd_brand_id,category_code=category_id,points=rwrd_gv_points_value,points_desc=total_rwrd_gvs,offer_value=total_gv_value,brand_id=brand_id,api_flag='Assign GV to Rewards Desk')
        except ValueError as e:
            #logger.error("Error saving TblRequestAuditLogs entry: %s", e)
            messages.error(request, "An error occurred while saving audit logs.")
            return redirect(reverse('RwrdGVs') + '?tb=assign')

        available_vouchers = RewardGiftvouchers.objects.filter(rwrd_brand_id=rwrd_brand_id,gv_points_value=rwrd_gv_points_value,brand_id=brand_id, status_flag=1,issue_flag=1)

        try:
            if pd.isnull(brand_id) or brand_id == '':
                messages.error(request, "Brand id should not be empty..!")               
                return redirect(reverse('RwrdGVs') + '?tb=assign')
            elif available_vouchers.count() < int(total_rwrd_gvs):
                messages.error(request, "Insufficient vouchers in stock.")               
                return redirect(reverse('RwrdGVs') + '?tb=assign')
            else:
                AssignedGiftVouchers.objects.create(category_id_id=category_id,rwrd_brand_id_id=rwrd_brand_id,gv_points_value=rwrd_gv_points_value,tot_gvs=total_rwrd_gvs,tot_gvs_value=total_gv_value,user_id=login_id,brand_id=brand_id)
                
                #gvs_to_update = available_vouchers[:int(total_rwrd_gvs)]

                #gvs_to_update.update(issue_flag=0,gv_assigned_on=timezone.now(),gv_assigned_by=login_id)

                gvs_to_update_ids = list(available_vouchers.values_list('id', flat=True).order_by('created_on')[:int(total_rwrd_gvs)])
                RewardGiftvouchers.objects.filter(id__in=gvs_to_update_ids).update(issue_flag=0,gv_assigned_on=timezone.now(),gv_assigned_by=login_id)
                
                
                messages.success(request, "GVs assigned to Rewards desk successfully")
                return redirect(reverse('RwrdGVs') + '?tb=assign')
            
    
        except ValueError as e:
            #logger.error("Error during validation checks: %s", e)
            messages.error(request, "An error occurred during validation checks.")
            return redirect(reverse('RwrdGVs') + '?tb=assign')



class RedeemPointsView(TemplateView):
    def get(self, request):

        brand_id=request.session.get("brand_id")

        return render(request,"pages/forms/redeem_points.html",{'otp_sent':''})

    def post(self, request):

        data = request.POST
        
        mobileno = data.get("mobile_number")
        redeem_points = data.get("redeem_points")
        redeem_otp = data.get("otp")
        ref_bill_number = data.get("ref_bill_number")
                        
        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

        loc_id = MstUserLogins.objects.filter(brand_id=brand_id, id=login_id, status_flag=1).values_list('locationid', flat=True).first()  

        if 'btnsendotp' in request.POST:
            redeem_flag = "sendotp"
        elif 'btnredeem' in request.POST:
            redeem_flag = "redeem"
        

        validated_data = {
            'mobile_number': mobileno,
            'redeem_points': redeem_points,
            'redeem_otp': redeem_otp,
            'ref_bill_number': ref_bill_number,
            'loc_id': loc_id,
            'redeem_flag': redeem_flag,
        }

        result = redeem_points_logic(validated_data,brand_id,'Platform',login_id)

        if result.data.get("type") == "redeem":
            return render(request,"pages/forms/redeem_points.html",{'message': result.data.get("message"), 'show_otp_fields': result.data.get("show_otp_fields"), 'otp_sent': result.data.get("otp_sent"), "status": False})
        else:
            return render(request,"pages/forms/redeem_points.html",{'message': result.data.get("message"), 'show_otp_fields': result.data.get("show_otp_fields"), 'otp_sent': result.data.get("otp_sent"), 'mobileno':mobileno, 'redeem_points':redeem_points, 'existing_bal_points':result.data.get("existing_bal_points"), "status": False})

def redeem_points_logic(data,brand_id,source,login_id):
    mobileno = data['mobile_number']
    redeem_points = data['redeem_points']
    otp_pswd = data['redeem_otp']
    ref_bill_number = data['ref_bill_number']
    if source == "API":
        location = data['location']
    else:
        location = ''

    if source == "Platform":
        #cat_id = data['category_id']
        loc_id = data['loc_id']
        redeem_flag = data['redeem_flag']
    else:
        #cat_id = ''
        loc_id = ''
        redeem_flag = ''
    
    try:

        TblRequestAuditLogs.objects.create(mobileno=mobileno,points=redeem_points,otp=otp_pswd,bill_number=ref_bill_number,period=redeem_flag,reg_source=source,api_flag='Redem Points')

        msg = mobile_number_validation(mobileno, brand_id)
        #print(message)
        if msg:
            return Response({'message': msg, "status": False})
        if pd.isnull(brand_id) or brand_id == '' or brand_id == None:
            return Response({'message': 'Brand id should not be empty..!', "status": False})
        if not LoyaltyCustomers.objects.filter(mobileno=mobileno, brand_id=brand_id, status_flag=1).exists():
            return Response({'message': "Mobile number is not registered with us!!", "status": False})
        if LoyaltyCustomers.objects.filter(mobileno=mobileno, brand_id=brand_id, status_flag=0).exists():
            return Response({"message": "Mobile number is deactivated!!", "status": False})
        if not loc_id:
            location_id = LocationMst.objects.filter(location_code=location,brand_id=brand_id,status_flag=1).values_list('location_id', flat=True).first()
        else:
            location_id = loc_id
        if not location_id:
            return Response({'message': 'Location doesn''t match..!', "status": False})
        
        gfb = global_brand_data(brand_id)
        gfb_cached_data1 = gfb.get('cached_data1', [])

        config_redeem_rs_per_point = gfb_cached_data1[0].redeem_rs_per_point
        config_minimum_points_redeem = gfb_cached_data1[0].minimum_points_redeem
        config_maximum_points_redeem = gfb_cached_data1[0].maximum_points_redeem

        print(config_redeem_rs_per_point)
        
        redeem_points_val = float(redeem_points) * int(config_redeem_rs_per_point)
        
        points_data = LoyaltyPoints.objects.filter(mobileno=mobileno,brand_id=brand_id,status_flag=1)

        if len(points_data) > 0:
            existing_bal_points = points_data[0].bal_points
        
        if float(existing_bal_points) < float(redeem_points):
            return Response({'message': 'Insufficient points in customer account!', "status": False,"otp_sent": '',"show_otp_fields": '',"existing_bal_points":existing_bal_points,"type":"redeemotp"})

        if float(redeem_points) < float(config_minimum_points_redeem) or float(redeem_points) > float(config_maximum_points_redeem):
            return Response({'message': 'Mimimum/Maximum points criteria doesn''t match!', "status": False,"otp_sent": '',"show_otp_fields": '',"existing_bal_points":existing_bal_points,"type":"redeemotp"})
        
        if redeem_flag == "sendotp":
            redeeem_pts_otp = random.randint(100000, 999999)
            redeemotp_data = OtpVerficationDetails.objects.filter(mobileno=mobileno,brand_id=brand_id,status_flag=1,flag=2)

            if len(redeemotp_data) > 0:
                updateotp_data = OtpVerficationDetails.objects.filter(mobileno=mobileno,brand_id=brand_id,status_flag=1,flag=2).update(status_flag=4, updated_on=timezone.now(),updated_by=login_id)
            
            enc_redeem_pts_otp = str_encrypt(str(redeeem_pts_otp))

            gfb_cached_data2 = gfb.get('cached_data2', [])

            config_Redeemed_Pts_OTP_Template_text = next(
            (template['template_text'] for template in gfb_cached_data2 if template['template_flag'] == 'RedeemOTP'),
            None  # Default to None if no match is found
            )

            OtpVerficationDetails.objects.create(mobileno=mobileno,brand_id=brand_id,status_flag=1,flag=2,points=redeem_points,secureotp=enc_redeem_pts_otp,user_id=login_id,location_id=loc_id,source=source)

            msg = config_Redeemed_Pts_OTP_Template_text

            sms_msg = msg.replace("[$vrfyotp$]",str(redeeem_pts_otp))
            sms_api_response = SingleSMSBroadcastApi.smssend("RedeemOTP", brand_id, '0', mobileno, sms_msg, "Trans","","","",loc_id,"")

            otp_sent = True
            show_otp_fields = True

            return Response({"message": "OTP sent successfully on customer's mobile.", "status": False,"otp_sent": otp_sent,"show_otp_fields": show_otp_fields,"existing_bal_points":existing_bal_points,"type":"redeemotp"})
        
        elif redeem_flag == "redeem":
            
            if not otp_pswd:
                return Response({'message': 'OTP can''t be blank!', "status": False,"otp_sent": otp_sent,"show_otp_fields": show_otp_fields,"existing_bal_points":existing_bal_points,"type":"redeemotp"})
            if not ref_bill_number:
                return Response({'message': 'Reference bill number can''t be blank!', "status": False,"otp_sent": otp_sent,"show_otp_fields": show_otp_fields,"existing_bal_points":existing_bal_points,"type":"redeemotp"})

            secure_redeem_pts_otp = str_encrypt(str(otp_pswd))

            redeemotpverify_data = OtpVerficationDetails.objects.filter(mobileno=mobileno,brand_id=brand_id,status_flag=1,flag=2,points=redeem_points,secureotp=secure_redeem_pts_otp)
            if len(redeemotpverify_data) > 0:
                show_otp_fields = True
                bal_points_aft_trans = existing_bal_points - float(redeem_points)
                
                with transaction.atomic():
                    
                    #redeem_trans_id = generate_transaction_id("CP")

                    updateotp_data = OtpVerficationDetails.objects.filter(mobileno=mobileno,brand_id=brand_id,status_flag=1,flag=2,points=redeem_points,secureotp=secure_redeem_pts_otp).update(status_flag=2, updated_on=timezone.now(),updated_by=login_id)
                    
                    transaction_entry = LoyaltyTrans.objects.create(
                        mobileno=mobileno,
                        brand_id=brand_id,
                        bill_number=ref_bill_number,
                        bill_date=timezone.now(),
                        location_id_id=location_id,
                        points=redeem_points,
                        bill_status='New',
                        bal_points_bef_trans=existing_bal_points,
                        bal_points_aft_trans=bal_points_aft_trans,
                        bill_trans_type="Redeem",
                        trans_source=source,
                        user_id=login_id    
                    )

                    
                    # Update PointsMaster table
                    points_master, created = LoyaltyPoints.objects.get_or_create(mobileno=mobileno,brand_id=brand_id,status_flag=1)
                    points_master.bal_points = round(points_master.bal_points - float(redeem_points), 2)
                    points_master.updated_on = timezone.now()
                    points_master.last_trans_date=timezone.now()
                    points_master.tot_cust_redeempoints = round(points_master.tot_cust_redeempoints + float(redeem_points), 2)
                    points_master.save()

                    gfb_cached_data2 = gfb.get('cached_data2', [])

                    config_Redeemed_Pts_Template_text = next(
                    (template['template_text'] for template in gfb_cached_data2 if template['template_flag'] == 'Redeem'),
                    None  # Default to None if no match is found
                    )

                    smsmsg = config_Redeemed_Pts_Template_text

                    smsmsg_ = smsmsg.replace("[$rdpts$]",str(redeem_points))
                    sms_msg = smsmsg_.replace("[$Blpts$]",str(points_master.bal_points))

                    sms_api_response = SingleSMSBroadcastApi.smssend("Redeem", brand_id, login_id, mobileno, sms_msg, "Trans",timezone.now(),ref_bill_number,'0',location_id,"")    
                
                #reward_brand_name = RewardBrandsMst.objects.filter(id=rwrd_brand_id).values_list('rwrd_brand_name', flat=True).first()

                if source == "API":
                    return Response({'message': f"{redeem_points} points redeemed from customer account. Balance points are {points_master.bal_points}", "status": False,"transaction_id":ref_bill_number, "redeem_points": redeem_points, "total_points": points_master.bal_points,"type":"redeem"})
                else:
                    return Response({'message': f"{redeem_points} points redeemed from customer account. Balance points are {points_master.bal_points}", "status": False,"transaction_id":ref_bill_number, "redeem_points": redeem_points, "total_points": points_master.bal_points,"type":"redeem"})
            else:
                show_otp_fields = True
                otp_sent = True
                return Response({'message': f"Invalid OTP!! Please try again.", "status": False, "show_otp_fields": show_otp_fields, "otp_sent":otp_sent,"existing_bal_points":existing_bal_points,"type":"redeemotp"})
    except Exception as e:
        return Response({'message': f"An error occurred during validation or calculation ({e})", "status": False})


class IssueVoucherView(TemplateView):
    def get(self, request):

        brand_id=request.session.get("brand_id")

        categoriesdta = CategoryMst.objects.filter(brand_id=brand_id, status_flag=1).values('category_id','category_name').order_by('category_name')

        brandsdta = RewardBrandsMst.objects.filter(brand_id=brand_id, status_flag=1).values('id','rwrd_brand_name').order_by('rwrd_brand_name')

        return render(request,"pages/forms/issue_voucher.html",{"brandsdta":brandsdta,"categoriesdta":categoriesdta})

    def post(self, request):

        data = request.POST
        
        mobileno = data.get("mobile_number")
        category_id = data.get("selcategory")
        rwrd_brand_id = data.get("selbrand")
        rwrd_gv_points_value = data.get("seldenomination")
        gv_qty = data.get("gv_qty")
                
        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

        categoriesdta = CategoryMst.objects.filter(brand_id=brand_id, status_flag=1).values('category_id','category_name').order_by('category_name')
        brandsdta = RewardBrandsMst.objects.filter(brand_id=brand_id, status_flag=1).values('id','rwrd_brand_name').order_by('rwrd_brand_name')

        loc_id = MstUserLogins.objects.filter(brand_id=brand_id, id=login_id, status_flag=1).values_list('locationid', flat=True).first()  

        validated_data = {
            'mobile_number': mobileno,
            'category_id': category_id,
            'rwrdbrandid': rwrd_brand_id,
            'gv_points_value': rwrd_gv_points_value,
            'gv_qty': gv_qty,
            'loc_id': loc_id,
        }

        result = redeem_points_logic(validated_data,brand_id,'Platform',login_id)

        return render(request,"pages/forms/issue_voucher.html",{'message': result.data.get("message"), "status": False, "categoriesdta":categoriesdta, "brandsdta":brandsdta})


class RewardBrandSearchView(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/brand-details.html",{"rwrdbranddata":''})
    def post(self, request):
        data = request.POST
        rwrd_brand = data.get("rwrdbrand_name")
        brand_id=request.session.get("brand_id")
        rwrdbranddata = RewardBrandsMst.objects.select_related('category_id').filter(rwrd_brand_name__contains=rwrd_brand,brand_id=brand_id,status_flag=1)
        return render(request,"pages/forms/brand-details.html",{"rwrdbranddata":rwrdbranddata,"message":"success"})


class SettingsLocationMstView(TemplateView):

    def get(self, request):
        brand_id=request.session.get("brand_id")
        
        locations = LocationMst.objects.filter(brand_id=brand_id,status_flag=1).values('location_id','location_Name','location_address','location_phonenumber','location_emailid','location_code').order_by('created_on')
        locations_data = list(locations)
        locations_json_data = json.dumps(locations_data)

        return render(request,"pages/forms/settings_locations.html",{'locationmst':locations_json_data})
    

class DeleteLocation(TemplateView):
    def post(self, request):
        if request.method == 'POST':
            data = request.POST
            #data = json.loads(request.body)
            locid = data.get("locid")
            brand_id=request.session.get("brand_id")
            login_id=request.session.get("loginid")
            #print(tier_id)
            
            TblRequestAuditLogs.objects.create(location_id=locid,brand_id=brand_id,api_flag='Delete Location')

            if locid:
                LocationMst.objects.filter(brand_id=brand_id, location_id=locid, status_flag=1).update(status_flag=0, updated_on=timezone.now(),updated_by=login_id)
                return JsonResponse({"success": True, "message": "Location deleted successfully"})
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)
    
class GetLocationDetails(TemplateView):
    def post(self, request):
        if request.method == 'POST':
            
            #data = request.POST
            #print(data)
            data = json.loads(request.body)
            #print(data)
            locid = data.get("locid")
            brand_id=request.session.get("brand_id")
            
            TblRequestAuditLogs.objects.create(location_id=locid,brand_id=brand_id,api_flag='Get Location details')
            
            loc = get_object_or_404(LocationMst, location_id=locid, brand_id=brand_id, status_flag=1)
            
            data = {
                "location_id": loc.location_id,
                "location_name": loc.location_Name,
                "location_address": loc.location_address,
                "location_phonenumber": loc.location_phonenumber,
                "location_email": loc.location_emailid,
                "location_code": loc.location_code,
            }
            print(data)
            return JsonResponse(data, safe=False)
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)


class EditLocation(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/settings_locations.html")
    def post(self, request):

        data = request.POST
        
        tabKeyVal = data.get("modal_tabKey")
        modal_index = data.get("modal_index")
        location_id = data.get("modal_location_id")
        location_name = data.get("modal_location_name")
        location_address = data.get("modal_location_address")
        location_phonenumber = data.get("modal_location_phoneno")
        location_emailid = data.get("modal_location_email")
        location_code = data.get("modal_location_code")
        
        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

        try:
            TblRequestAuditLogs.objects.create(location_id=location_id,period=tabKeyVal,resource_name=modal_index,location_name=location_name,comments=location_address,homeno=location_phonenumber,email_id=location_emailid,location_code=location_code,brand_id=brand_id,api_flag='Edit Location')
        except ValueError as e:
            #logger.error("Error saving TblRequestAuditLogs entry: %s", e)
            messages.error(request, "An error occurred while saving audit logs.")
            return redirect(reverse('LocationMaster'))

        try:
            if pd.isnull(brand_id) or brand_id == '':
                messages.error(request, "brand id should not be empty..!")               
                return redirect(reverse('LocationMaster'))
            elif not location_name:
                messages.error(request, "Location name is required.")               
                return redirect(reverse('LocationMaster'))
            elif LocationMst.objects.filter(location_Name=location_name,brand_id=brand_id,status_flag=1).exclude(location_id=location_id).exists():
                messages.error(request, "Location name already exists.")               
                return redirect(reverse('LocationMaster'))

            LocationMst.objects.filter(brand_id=brand_id, location_id=location_id, status_flag=1).update(location_Name=location_name,location_address=location_address,location_phonenumber=location_phonenumber,location_emailid=location_emailid,location_code=location_code,updated_on=timezone.now(),updated_by=login_id)
            messages.success(request, "Location modified successfully")               
            return redirect(reverse('LocationMaster'))
            
        except ValueError as e:
            #logger.error("Error during validation checks: %s", e)
            messages.error(request, "An error occurred during validation checks.")
            return redirect(reverse('LocationMaster'))

class ImportLocationMst(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/settings_locations.html")
    def post(self, request):

        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

        if request.method == 'POST' and request.FILES['locationfile']:
            locationfile = request.FILES['locationfile']
            rejected_records = []
            success_count = 0

            upload_dir1 = 'media/location_files/'
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'location_files')
            fs = FileSystemStorage(location=upload_dir)
            filename = fs.save(locationfile.name, locationfile)
            locationfile_filename = os.path.join(upload_dir, filename)
            with open(locationfile_filename, 'wb') as f:
                for chunk in locationfile.chunks():
                    f.write(chunk)

            try:
        
                #print(categoryfile_filename)

                if locationfile.name.endswith('.csv'):
                    data = pd.read_csv(locationfile_filename)
                elif locationfile.name.endswith('.xlsx'):
                    data = pd.read_excel(locationfile_filename)
                else:
                    return JsonResponse({'error': 'Invalid file format. Only CSV and Excel files are allowed.'}, status=400)

                data = data.fillna('')

                for _, row in data.iterrows():
                    location_name = row.get('location_name', '').strip()  
                    location_address = row.get('location_address', '').strip()
                    location_phonenumber = row.get('location_phonenumber')
                    location_emailid = row.get('location_emailid', '').strip()
                    location_code = row.get('location_code', '').strip()
                    #rwrd_brand_identifier = row.get('brand_name_on_bill', '').strip()

                    #if isinstance(rwrd_brand_floor, str):
                    #    rwrd_brand_floor = rwrd_brand_floor.strip()
                    #if isinstance(rwrd_brand_shopno, str):
                    #    rwrd_brand_shopno = rwrd_brand_shopno.strip()

                    #print(location_phonenumber)
                    #print(location_code)

                    #rwrd_category_id = CategoryMst.objects.filter(category_name=rwrd_brand_category,brand_id=brand_id,status_flag=1).values_list('category_id', flat=True).first()

                    if not location_code:
                        rejected_records.append({'row': row.to_dict(), 'reason': 'Blank location code'})
                        continue
                    elif not location_name:
                        rejected_records.append({'row': row.to_dict(), 'reason': 'Blank location name'})
                        continue
                    # Check for duplicates
                    elif LocationMst.objects.filter(location_Name=location_name,brand_id=brand_id,status_flag=1).exists():
                        rejected_records.append({'row': row.to_dict(), 'reason': f'Duplicate location: {location_name}'})
                        continue
                    elif LocationMst.objects.filter(location_code=location_code,brand_id=brand_id,status_flag=1).exists():
                        rejected_records.append({'row': row.to_dict(), 'reason': f'Duplicate location code: {location_code}'})
                        continue
                    else:
                    # Save valid records to the database
                        LocationMst.objects.create(location_Name=location_name,location_address=location_address,location_phonenumber=location_phonenumber,location_emailid=location_emailid,location_code=location_code,location_file_name=locationfile,brand_id=brand_id,user_id=login_id)
                        success_count += 1
                
                rejected_count = len(rejected_records)

                return JsonResponse({'rejected_records': rejected_records,'success_count':success_count,'rejected_count':rejected_count}, status=200)

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

        return render(request,"pages/forms/settings_locations.html")
    


class SettingsSMSConfigureView(TemplateView):

    def get(self, request):
        brand_id=request.session.get("brand_id")
        
        templatetypes = TemplateFlagsMst.objects.all().values('template_type').distinct()
        templatecategories = TemplateFlagsMst.objects.all().values('template_category').distinct()

        templatesdta = Templates.objects.select_related('template_flag_id').filter(brand_id=brand_id,status_flag=1).values('id','template_name','template_flag','template_text','template_flag_id__template_type','template_flag_id__template_category').order_by('created_on')
        templates_data = list(templatesdta)
        templates_json_data = json.dumps(templates_data)

        return render(request,"pages/forms/settings_sms_configure.html",{'templatesdata':templates_json_data,'templatetypes':templatetypes,'templatecategories':templatecategories})
    

def GetTemplateCategoryByTypeView(request):
    if request.method == "POST":
        template_type = request.POST.get('template_type')

        brand_id=request.session.get("brand_id")

        if not template_type:
            return JsonResponse({'error': 'Template Type is required'}, status=400)

        templatecategories = TemplateFlagsMst.objects.filter(template_type=template_type, status_flag=1).values('template_category').distinct()
        return JsonResponse(list(templatecategories), safe=False)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def GetTemplateFlagByTypeCatView(request):
    if request.method == "POST":
        template_type = request.POST.get('template_type')
        template_cat = request.POST.get('template_cat')

        brand_id=request.session.get("brand_id")

        if not template_type:
            return JsonResponse({'error': 'Template Type is required'}, status=400)
        if not template_cat:
            return JsonResponse({'error': 'Template Category is required'}, status=400)

        templateflags = TemplateFlagsMst.objects.filter(template_type=template_type, template_category=template_cat, status_flag=1).values('id','template_flag','template_flag_description').distinct()
        return JsonResponse(list(templateflags), safe=False)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


class AddTemplateView(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/settings_sms_configure.html")
    def post(self, request):

        data = request.POST
        
        template_type = data.get("seltemplatetype")
        template_category = data.get("seltemplatecat")
        template_flag_id = data.get("seltemplateflag")
        template_id = data.get("templateid")
        template_text = data.get("templatetext")
                
        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

        #print(rwrd_brand_id)
        
        try: 
            TblRequestAuditLogs.objects.create(type=template_type,category_code=template_category,tier_id=template_flag_id,item_code=template_id,comments=template_text,brand_id=brand_id,api_flag='Add Template')
        except ValueError as e:
            #logger.error("Error saving TblRequestAuditLogs entry: %s", e)
            messages.error(request, "An error occurred while saving audit logs.")
            return redirect(reverse('SMSConfig'))
        
        try:
            if pd.isnull(brand_id) or brand_id == '':
                messages.error(request, "brand id should not be empty..!")               
                return redirect(reverse('SMSConfig'))
            elif not template_type:
                messages.error(request, "Template type is required.")               
                return redirect(reverse('SMSConfig'))
            elif not template_category:
                messages.error(request, "Template category is required.")               
                return redirect(reverse('SMSConfig'))
            elif not template_flag_id:
                messages.error(request, "Template Flag is required.")               
                return redirect(reverse('SMSConfig'))
            elif not template_text:
                messages.error(request, "Template text is required.")               
                return redirect(reverse('SMSConfig'))
            elif Templates.objects.filter(template_flag_id_id=template_flag_id,brand_id=brand_id,status_flag=1).exists():
                messages.error(request, "Template already exist with given flag.")               
                return redirect(reverse('SMSConfig'))
            else:
                tmpldtls = TemplateFlagsMst.objects.filter(id=template_flag_id)
                if len(tmpldtls) > 0:
                    template_flag = tmpldtls[0].template_flag
                    template_flag_desc = tmpldtls[0].template_flag_description

                Templates.objects.create(template_name=template_flag_desc,template_id=template_id,template_flag=template_flag,template_flag_id_id=template_flag_id,template_text=template_text,brand_id=brand_id,user_id=login_id)
                messages.error(request, "Template added successfully.")               
                return redirect(reverse('SMSConfig'))
        
        except ValueError as e:
            #logger.error("Error during validation checks: %s", e)
            messages.error(request, f"An error occurred during validation checks ({e})")
            return redirect(reverse('SMSConfig'))

class DeleteTemplate(TemplateView):
    def post(self, request):
        if request.method == 'POST':
            data = request.POST
            #data = json.loads(request.body)
            templateid = data.get("templateid")
            brand_id=request.session.get("brand_id")
            login_id=request.session.get("loginid")
            #print(tier_id)
            
            TblRequestAuditLogs.objects.create(location_id=templateid,brand_id=brand_id,api_flag='Delete Template')

            if templateid:
                Templates.objects.filter(brand_id=brand_id, id=templateid, status_flag=1).update(status_flag=0, updated_on=timezone.now(),updated_by=login_id)
                return JsonResponse({"success": True, "message": "Template deleted successfully"})
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)
    

class GetTemplateDetailsView(TemplateView):
    def post(self, request):
        if request.method == 'POST':
            
            #data = request.POST
            #print(data)
            data = json.loads(request.body)
            print(data)
            templateid = data.get("templateid")
            brand_id=request.session.get("brand_id")
            
            TblRequestAuditLogs.objects.create(location_id=templateid,brand_id=brand_id,api_flag='Get Template details')
            
            tmplt = get_object_or_404(Templates, id=templateid, brand_id=brand_id, status_flag=1)
            
            tmplt_flag = TemplateFlagsMst.objects.all().filter(id=tmplt.template_flag_id,status_flag=1)
            
            if len(tmplt_flag) > 0:
                template_type = tmplt_flag[0].template_type
                template_category = tmplt_flag[0].template_category
                
            
            data = {
                "id": tmplt.id,
                "template_name": tmplt.template_name,
                "template_type": template_type,
                "template_category": template_category,
                "template_flag_id": tmplt.template_flag_id_id,
                "template_id": tmplt.template_id,
                "template_text": tmplt.template_text,
            }
            print(data)
            return JsonResponse(data, safe=False)
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)



class EditTemplate(TemplateView):
    def get(self, request):
        return render(request,"pages/forms/settings_sms_configure.html")
    def post(self, request):

        data = request.POST
        
        tabKeyVal = data.get("modal_tabKey")
        modal_index = data.get("modal_index")
        tmplt_id = data.get("modal_tmplt_id")
        template_type = data.get("modal_template_type")
        template_category = data.get("modal_template_category")
        template_flag_id = data.get("modal_template_flag")
        template_id = data.get("modal_templateid")
        template_text = data.get("modal_templatetext")
        
        brand_id=request.session.get("brand_id")
        login_id=request.session.get("loginid")

        try:
            TblRequestAuditLogs.objects.create(location_id=tmplt_id,period=tabKeyVal,resource_name=modal_index,type=template_type,comments=template_text,category_code=template_category,tier_id=template_flag_id,location_code=template_id,brand_id=brand_id,api_flag='Edit Template')
        except ValueError as e:
            #logger.error("Error saving TblRequestAuditLogs entry: %s", e)
            messages.error(request, "An error occurred while saving audit logs.")
            return redirect(reverse('SMSConfig'))

        try:
            if pd.isnull(brand_id) or brand_id == '':
                messages.error(request, "brand id should not be empty..!")               
                return redirect(reverse('SMSConfig'))
            elif not template_type:
                messages.error(request, "Template type is required.")               
                return redirect(reverse('SMSConfig'))
            elif not template_category:
                messages.error(request, "Template Category is required.")
                return redirect(reverse('SMSConfig'))
            elif not template_flag_id:
                messages.error(request, "Template Flag is required.")
                return redirect(reverse('SMSConfig'))
            elif not template_text:
                messages.error(request, "Template text is required.")
                return redirect(reverse('SMSConfig'))
            elif Templates.objects.filter(template_flag_id_id=template_flag_id,brand_id=brand_id,status_flag=1).exclude(template_flag_id_id=template_flag_id).exists():
                messages.error(request, "Template already exist with given flag.")               
                return redirect(reverse('SMSConfig'))
            else:
                tmpldtls = TemplateFlagsMst.objects.filter(id=template_flag_id)
                if len(tmpldtls) > 0:
                    template_flag = tmpldtls[0].template_flag
                    template_flag_desc = tmpldtls[0].template_flag_description

                Templates.objects.filter(brand_id=brand_id, template_flag_id_id=template_flag_id, status_flag=1).update(template_name=template_flag_desc,template_id=template_id,template_flag=template_flag,template_flag_id_id=template_flag_id,template_text=template_text,updated_on=timezone.now(),updated_by=login_id)
                messages.error(request, "Template modified successfully.")               
                return redirect(reverse('SMSConfig'))
            
        except ValueError as e:
            #logger.error("Error during validation checks: %s", e)
            messages.error(request, "An error occurred during validation checks.")
            return redirect(reverse('SMSConfig'))


class RedeemCouponView(TemplateView):
    def get(self, request):
        brand_id=request.session.get("brand_id")
        return render(request,"pages/forms/redeem_coupon.html",{'coupondata':''})