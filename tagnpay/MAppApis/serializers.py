# serializers.py
from rest_framework import serializers
from tagnpayloyalty.models import LoyaltyCustomers, MissedcallRequests, LocationMst, LoyaltyPoints, RewardBrandsMst, PendingBills, TblRequestAuditLogs, LoyaltyTrans
from datetime import datetime
from tagnpayloyalty.helpers import get_brand_id_from_api_url, str_encrypt, mobile_number_validation
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from tagnpay.env_details import *
from common.helpers.smshelpers import SingleSMSBroadcastApi
from rest_framework.exceptions import ValidationError


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
            raise serializers.ValidationError({"error": str(msg)})
        if not LoyaltyCustomers.objects.filter(mobileno=validated_data['mobile_number'], brand_id=brand_id, status_flag=1).exists():
            raise serializers.ValidationError({"error": str("Mobile number is not registered with us!!")})
        if LoyaltyCustomers.objects.filter(mobileno=validated_data['mobile_number'], brand_id=brand_id, status_flag=0).exists():
            raise serializers.ValidationError({"error": str("Mobile number is deactivated!!")})
        
        return validated_data


class TransactionSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='rwrd_brand_id.rwrd_brand_name', read_only=True)
    location_name = serializers.CharField(source='location_id.location_Name', read_only=True)

    class Meta:
        model = LoyaltyTrans
        fields = ['mobileno','bill_number', 'bill_amount', 'bill_date', 'brand_name','location_name','points','bill_trans_type','bal_points_aft_trans']


class UploadBillSerializer(serializers.ModelSerializer):
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
