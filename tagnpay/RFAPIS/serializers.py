# serializers.py
from rest_framework import serializers
from tagnpayloyalty.models import LoyaltyCustomers, MissedcallRequests, LocationMst, LoyaltyPoints, RewardBrandsMst, PendingBills, TblRequestAuditLogs
from datetime import datetime
from tagnpayloyalty.helpers import get_brand_id_from_api_url, str_encrypt, mobile_number_validation
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from tagnpay.env_details import *
from common.helpers.smshelpers import SingleSMSBroadcastApi
from rest_framework.exceptions import ValidationError


class MissedCallSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15)
    circle = serializers.CharField(max_length=100)
    location = serializers.CharField(max_length=100)
    date = serializers.DateField(default=datetime.today)  # Auto-fill today's date if not provided
    time = serializers.TimeField(default=datetime.now().time)  # Auto-fill current time if not provided

    def create(self, validated_data):

        request = self.context.get('request')
        
        #print(self.validated_data)

        brand_id = get_brand_id_from_api_url(request)

        message = mobile_number_validation(validated_data['mobile_number'], brand_id)
        #print(message)
        if message:
            #return Response({'message': message, "status": False})
            raise serializers.ValidationError({"error":message})

        if validated_data['location'] is not None:
            loc_dtls = LocationMst.objects.filter(location_code=validated_data['location'], status_flag=1, brand_id=brand_id)
            
            if len(loc_dtls) > 0:
                loc_id = loc_dtls[0].location_id
        
        # Log the missed call for the customer
        missed_call = MissedcallRequests.objects.create(
            mobileno=validated_data['mobile_number'],
            circle=validated_data['circle'],
            location=validated_data['location'],
            received_date=validated_data['date'],
            received_time=validated_data['time'],
            brand_id=brand_id
        )
        
        # Register the customer if not already registered
        customer, created = LoyaltyCustomers.objects.get_or_create(
            mobileno=validated_data['mobile_number'],
            brand_id=brand_id,
            defaults={"reg_source":"Missed Call","location_id_id":loc_id}
        )

        customerpoint, pointcreated = LoyaltyPoints.objects.get_or_create(
            mobileno=validated_data['mobile_number'],
            brand_id=brand_id,
            defaults={"bal_points":"0","bal_cash_val":"0"}
        )

        if created:
            print("Customer created!")
            msg = config_Registration_SMS_text
            sms_api_response = SingleSMSBroadcastApi.smssend("Reg", brand_id, '0', validated_data['mobile_number'], msg, "Register","","","",loc_id,"")  
        else:
            print("Customer already exists!")

        return missed_call


class CustomTokenObtainPairSerializer(serializers.Serializer):
    #username = serializers.CharField()
    #password = serializers.CharField()
    mobileno = serializers.CharField()

    def validate(self, attrs):

        request = self.context.get('request')

        brand_id = get_brand_id_from_api_url(request)

        #username = attrs.get('username')
        #password = attrs.get('password')
        mobileno = attrs.get('mobileno')

        message = mobile_number_validation(mobileno, brand_id)
        #print(message)
        if message:
            #return Response({'message': message, "status": False})
            raise serializers.ValidationError({"error":message})

        #print(brand_id)

        # Validate username and password against environment variables
        #if username != RFAPI_USERNAME or password != RFAPI_PASSWORD:
        #    raise AuthenticationFailed('Invalid username or password.')

        # Validate mobile number against CustomerMaster
        #if not LoyaltyCustomers.objects.filter(mobileno=mobileno,brand_id=brand_id,status_flag=1).exists():
        #    raise AuthenticationFailed('Mobile number not registered.')
        
        return attrs
    
    
class EarnPointsSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15)
    bill_number = serializers.CharField(max_length=30)
    bill_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    bill_date = serializers.DateField()
    brand = serializers.CharField(max_length=100)
    category = serializers.CharField(max_length=100)
    location = serializers.CharField(max_length=100)


class CustomerRegSerializer(serializers.Serializer):
    mobileno = serializers.CharField(max_length=15)
    customer_name = serializers.CharField(max_length=50)
    email = serializers.EmailField(max_length=100,required=False, allow_blank=True)
    gender = serializers.CharField(max_length=20,required=False, allow_blank=True)
    dob = serializers.DateField(required=False, allow_null=True, input_formats=['%Y-%m-%d', '%d-%m-%Y'])
    doa = serializers.DateField(required=False, allow_null=True, input_formats=['%Y-%m-%d', '%d-%m-%Y'])
    address1 = serializers.CharField(max_length=100,required=False, allow_blank=True)
    address2 = serializers.CharField(max_length=100,required=False, allow_blank=True)
    landmark = serializers.CharField(max_length=100,required=False, allow_blank=True)
    district = serializers.CharField(max_length=100,required=False, allow_blank=True)
    city = serializers.CharField(max_length=100,required=False, allow_blank=True)
    state = serializers.CharField(max_length=50,required=False, allow_blank=True)
    country = serializers.CharField(max_length=50,required=False, allow_blank=True)
    zipcode = serializers.CharField(max_length=10,required=False, allow_blank=True)
    reg_source = serializers.CharField(max_length=50)
    loc_id = serializers.CharField(max_length=50)

    def to_internal_value(self, data):
        # Convert empty strings to None for dob and doa
        data = data.copy()
        if data.get('dob') == "":
            data['dob'] = None
        if data.get('doa') == "":
            data['doa'] = None
        return super().to_internal_value(data)

    def validate_dob(self, value):
        # Custom validation for Date of Birth
        if value and value.year < 1900:
            raise serializers.ValidationError("Date of birth cannot be before 1900.")
        return value

    def validate_doa(self, value):
        # Custom validation for Date of Anniversary
        if value and value.year < 1900:
            raise serializers.ValidationError("Date of anniversary cannot be before 1900.")
        return value

    def validate(self, data):
        
        location_code = data.get('loc_id')
        try:
            location_obj = LocationMst.objects.get(location_code=location_code)
        except LocationMst.DoesNotExist:
            raise serializers.ValidationError({'location': f"Location '{location_code}' does not exist."})
        
        # Replace location name with the corresponding ID
        data['loc_id'] = location_obj.location_id
        return data


class GetCustomerPtsSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15)
    
    def validate(self, validated_data):

        request = self.context.get('request')
        
        brand_id = get_brand_id_from_api_url(request)
        #print(brand_id)
        msg = mobile_number_validation(validated_data['mobile_number'], brand_id)
        #print(msg)
        if msg:
            raise serializers.ValidationError({"error": str(msg)})
        if not LoyaltyCustomers.objects.filter(mobileno=validated_data['mobile_number'], brand_id=brand_id, status_flag=1).exists():
            raise serializers.ValidationError({"error": str("Mobile number is not registered with us!!")})
        if LoyaltyCustomers.objects.filter(mobileno=validated_data['mobile_number'], brand_id=brand_id, status_flag=0).exists():
            raise serializers.ValidationError({"error": str("Mobile number is deactivated!!")})
        
        return validated_data
    

class GetBrandDenominationSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15)
    rwrd_brand_id = serializers.IntegerField()

    def validate(self, validated_data):

        request = self.context.get('request')
        
        brand_id = get_brand_id_from_api_url(request)
        #print(brand_id)
        msg = mobile_number_validation(validated_data['mobile_number'], brand_id)
        #print(msg)
        if msg:
            raise serializers.ValidationError({"error":msg})
        if not LoyaltyCustomers.objects.filter(mobileno=validated_data['mobile_number'], brand_id=brand_id, status_flag=1).exists():
            raise serializers.ValidationError({"error":"Mobile number is not registered with us!!"})
        if LoyaltyCustomers.objects.filter(mobileno=validated_data['mobile_number'], brand_id=brand_id, status_flag=0).exists():
            raise serializers.ValidationError({"error":"Mobile number is deactivated!!"})
        if validated_data['rwrd_brand_id'] == '' or validated_data['rwrd_brand_id'] is None:
            raise serializers.ValidationError({"error":"Brand Id is required!!"})
        if not RewardBrandsMst.objects.filter(id=validated_data['rwrd_brand_id'], brand_id=brand_id, status_flag=1).exists():
            raise serializers.ValidationError({"error":"Brand doesn't exist!!"})
        
        return validated_data
        

class RedeemPointsSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15)
    gv_points_value = serializers.IntegerField()
    rwrdbrandid = serializers.IntegerField()
    gv_qty = serializers.IntegerField()
    location = serializers.CharField(max_length=100)


# class PendingBillSerializer(serializers.Serializer):
#     mobile_number = serializers.CharField(max_length=15,required=True, allow_blank=False)
#     upload_file_name = serializers.CharField(max_length=100,required=True, allow_blank=False)
#     location = serializers.CharField(max_length=100,required=True, allow_blank=False)
    
#     #def validate_mobile_number(self, value):
#     #    if not value.strip():
#     #        raise serializers.ValidationError("Input data cannot be blank")
#     #    return value

#     def create(self, validated_data):

#         request = self.context.get('request')
        
#         brand_id = get_brand_id_from_api_url(request)
#         #print(brand_id)
        
#         TblRequestAuditLogs.objects.create(mobileno=validated_data['mobile_number'],location_id=validated_data['location'],comments=validated_data['upload_file_name'],reg_source='WhatsApp',api_flag='Pending Bills API')

#         msg = mobile_number_validation(validated_data['mobile_number'], brand_id)
#         #print(msg)


#         if msg:
#             raise serializers.ValidationError({"error":msg})
#         if not LoyaltyCustomers.objects.filter(mobileno=validated_data['mobile_number'], brand_id=brand_id, status_flag=1).exists():
#             raise serializers.ValidationError({"error":"Mobile number is not registered with us!!"})
#         if LoyaltyCustomers.objects.filter(mobileno=validated_data['mobile_number'], brand_id=brand_id, status_flag=0).exists():
#             raise serializers.ValidationError({"error":"Mobile number is deactivated!!"})
#         if validated_data['location'] is not None:
#             loc_dtls = LocationMst.objects.filter(location_code=validated_data['location'], status_flag=1, brand_id=brand_id)
#             if len(loc_dtls) > 0:
#                 loc_id = loc_dtls[0].location_id
#             else:
#                 raise serializers.ValidationError({"error":"Location doesn't exist!!"})
        
#         pending_bill = PendingBills.objects.create(
#             mobileno=validated_data['mobile_number'],
#             location_id_id=loc_id,
#             upload_file_name=validated_data['upload_file_name'],
#             brand_id=brand_id
#         )
        
#         return pending_bill        


class PendingBillSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(write_only=True)
    location = serializers.CharField(write_only=True)
    location_id = serializers.IntegerField(read_only=True)
    upload_file_name = serializers.FileField(write_only=True)

    class Meta:
         model = PendingBills
         fields = ['id', 'mobile_number', 'upload_file_name', 'location', 'location_id']
         read_only_fields = ['id']

    def create(self, validated_data):
        request = self.context.get('request')
        brand_id = get_brand_id_from_api_url(request)
        print(brand_id)

        msg = mobile_number_validation(validated_data['mobile_number'], brand_id)
        #print(msg)


        if msg:
            raise serializers.ValidationError({"error":msg})
        if not LoyaltyCustomers.objects.filter(mobileno=validated_data['mobile_number'], brand_id=brand_id, status_flag=1).exists():
            raise serializers.ValidationError({"error":"Mobile number is not registered with us!!"})
        if LoyaltyCustomers.objects.filter(mobileno=validated_data['mobile_number'], brand_id=brand_id, status_flag=0).exists():
            raise serializers.ValidationError({"error":"Mobile number is deactivated!!"})
        loc_dtls = LocationMst.objects.filter(location_code=validated_data['location'], status_flag=1, brand_id=brand_id)
        if len(loc_dtls) > 0:
            loc_id = loc_dtls[0].location_id
        else:
            raise serializers.ValidationError({"error":"Location doesn't exist!!"})
        if not validated_data['upload_file_name'].name.endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            raise serializers.ValidationError("Only PDF, JPG, and PNG files are allowed.")
        # Restrict file size to 5 MB
        max_size = 5 * 1024 * 1024  # 5 MB
        if validated_data['upload_file_name'].size > max_size:
            raise serializers.ValidationError("File size must not exceed 5 MB.")

        bill = PendingBills.objects.create(mobileno=validated_data['mobile_number'], location_id_id=loc_id, brand_id=brand_id,upload_file_name=validated_data['upload_file_name'])
        return bill




class GenerateAppTokenSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15,required=True, allow_blank=False)
    deviceid = serializers.CharField(max_length=250,required=True, allow_blank=False)

    def validate(self, attrs):

        request = self.context.get('request')

        brand_id = get_brand_id_from_api_url(request)

        mobile_number = attrs.get('mobile_number')
        deviceid = attrs.get('deviceid')

        message = mobile_number_validation(mobile_number, brand_id)
        #print(message)
        if message:
            raise serializers.ValidationError({"error": str(message)})

        return attrs

    
class VerifyCustLoginOTPSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15,required=True, allow_blank=False)
    otp = serializers.CharField(max_length=8,required=True, allow_blank=False)
    
    def validate(self, validated_data):

        request = self.context.get('request')
        
        brand_id = get_brand_id_from_api_url(request)
        #print(brand_id)
        msg = mobile_number_validation(validated_data['mobile_number'], brand_id)
        #print(msg)
        if msg:
            raise serializers.ValidationError({"error": msg})
        if not LoyaltyCustomers.objects.filter(mobileno=validated_data['mobile_number'], brand_id=brand_id, status_flag=1).exists():
            raise serializers.ValidationError({"error": "Mobile number is not registered with us!!"})
        if LoyaltyCustomers.objects.filter(mobileno=validated_data['mobile_number'], brand_id=brand_id, status_flag=0).exists():
            raise serializers.ValidationError({"error": "Mobile number is deactivated!!"})
        
        return validated_data
