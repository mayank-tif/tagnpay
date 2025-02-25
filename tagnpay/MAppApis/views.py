from time import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from RFAPIS.serializers import GetCustomerPtsSerializer, PendingBillSerializer, GetBrandDenominationSerializer, RedeemPointsSerializer
from RFAPIS.views import DummyUser
from django.http import HttpResponseForbidden
from django.conf import settings
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated
from tagnpayloyalty.views import earn_points_logic, register_customer, redeem_points_logic
from tagnpayloyalty.helpers import get_brand_id_from_api_url
from tagnpay.env_details import *
from tagnpayloyalty.models import TblRequestAuditLogs, LoyaltyPoints, RewardGiftvouchers, CustomerLoginOtpVerification
from django.utils.timezone import now
from django.db.models import F
from utils.token_validation_utils import *
from utils.generate_utils import GenerateOTP
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime


@method_decorator(csrf_exempt, name='dispatch')
class GenerateAppTokenView(TokenObtainPairView):
    serializer_class = GenerateAppTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        username = request.headers.get('Username')
        password = request.headers.get('Password')
        
        if (username != TnPAPP_API_USERNAME or password != TnPAPP_API_PASSWORD):
            return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer.is_valid(raise_exception=True)
        
        
        user = DummyUser(username)
        
        token = AccessToken.for_user(user)

        token['mobile_number'] = request.data.get("mobile_number")
        token['deviceid'] = request.data.get("deviceid")
        token['username'] = username

        token.set_exp(lifetime=timedelta(minutes=15))

        return Response({"access_token": str(token)}, status=status.HTTP_200_OK)
    

class ValidateCustAndSendOTPAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        validate_mobileno_and_deviceid_with_token(request)

        brand_id = get_brand_id_from_api_url(request)
        serializer = GetCustomerPtsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            msg = config_login_otp_SMS_text
            loc_id = LocationMst.objects.filter(location_code='MAPP001').values_list('location_id', flat=True).first()
            login_otp = GenerateOTP.generate_otp()
            enc_login_otp = str_encrypt(str(login_otp))
            loginotp_data = CustomerLoginOtpVerification.objects.filter(mobileno=request.data['mobile_number'],brand_id=brand_id,status_flag=1,flag='login')
            sms_msg = msg.replace("[$vrfyotp$]",str(login_otp))
            if len(loginotp_data) > 0:
                CustomerLoginOtpVerification.objects.filter(mobileno=request.data['mobile_number'],brand_id=brand_id,status_flag=1,flag='login').update(secureotp=enc_login_otp,source='MobileApp',updated_on=datetime.now(),support_remarks=login_otp)
            else:    
                CustomerLoginOtpVerification.objects.create(mobileno=request.data['mobile_number'],brand_id=brand_id,secureotp=enc_login_otp,source='MobileApp',flag='login',support_remarks=login_otp)
            
            sms_api_response = SingleSMSBroadcastApi.smssend("Login", brand_id, '0', request.data['mobile_number'], sms_msg, "Login","","","",loc_id,"")
            return Response({"message": "OTP sent successfully.","otp":login_otp}, status=status.HTTP_201_CREATED)
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_201_CREATED)
    

class VerifyCustLoginOTPAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        validate_mobileno_and_deviceid_with_token(request)

        brand_id = get_brand_id_from_api_url(request)
        serializer = VerifyCustLoginOTPSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            enc_login_otp = str_encrypt(str(request.data['otp']))
            chkloginotp_data = CustomerLoginOtpVerification.objects.filter(mobileno=request.data['mobile_number'],secureotp=enc_login_otp,brand_id=brand_id,status_flag=1,flag='login')
            if len(chkloginotp_data) > 0:
                pointsdata = LoyaltyPoints.objects.select_related('tier_id').filter(mobileno=request.data['mobile_number'],brand_id=brand_id,status_flag=1)
                if len(pointsdata) > 0:
                    customer_name = pointsdata[0].name
                    bal_points = pointsdata[0].bal_points
                    tier_name = pointsdata[0].tier_id.tier_name

                user_identifier = LoyaltyCustomers.objects.filter(mobileno=request.data['mobile_number'],brand_id=brand_id,status_flag=1).values_list('user_identifier', flat=True).first() 
                               
                user = DummyUser(CP67_APP_API_USERNAME)
                
                verify_access_token = AccessToken.for_user(user)

                verify_access_token['mobile_number'] = request.data.get("mobile_number")
                verify_access_token['login_val'] = enc_login_otp
                verify_access_token['custbndid'] = str(brand_id) + user_identifier
                

                verify_access_token.set_exp(lifetime=timedelta(days=30))

                return Response({"message": "Customer verified successfully","customer_name":customer_name,"balance_points":bal_points,"tier_name":tier_name,"verify_access_token":str(verify_access_token)}, status=status.HTTP_201_CREATED)
            else:    
                return Response({"error": "Invalid OTP!!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetCustTransactionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        validate_mobileno_and_pswd_with_token(request)

        mobile_number = request.data.get('mobile_number')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        brand_id = get_brand_id_from_api_url(request)

        # Validate mobile number
        if not mobile_number:
            return Response({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch transactions for the given mobile number
        #transactions = LoyaltyTrans.objects.select_related('location_id', 'rwrd_brand_id').all().order_by('-created_on')
        transactions = LoyaltyTrans.objects.filter(brand_id=brand_id,mobileno=mobile_number,status_flag=1).all().order_by('-created_on')

        if start_date:
            start_date = parse_datetime(start_date)
            if start_date:
                transactions = transactions.filter(bill_date__gte=start_date)

        if end_date:
            end_date = parse_datetime(end_date)
            if end_date:
                transactions = transactions.filter(bill_date__lte=end_date)
        
        if not transactions.exists():
            return Response({"error": "No transactions found for this mobile number"}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize data
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class MappUploadCustBillAPIView(APIView):

#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
        
#         validate_mobileno_and_pswd_with_token(request)
        
#         serializer = PendingBillSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Pending Bill request received successfully"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetMappCustomerPtsBrandsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        validate_mobileno_and_pswd_with_token(request)

        brand_id = get_brand_id_from_api_url(request)
        serializer = GetCustomerPtsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            points_data = LoyaltyPoints.objects.filter(mobileno=request.data['mobile_number'],brand_id=brand_id,status_flag=1)
            if len(points_data) > 0:
                bal_points = points_data[0].bal_points
            brands_data = RewardGiftvouchers.objects.select_related('rwrd_brand_id').filter(brand_id=brand_id, status_flag=1,issue_flag=0,gv_status_flag=1,gv_expiry__gte=now(),gv_points_value__lte=bal_points).annotate(BrandId=F('rwrd_brand_id__id'),BrandName=F('rwrd_brand_id__rwrd_brand_name')).values('BrandId', 'BrandName').distinct()
            if len(brands_data) > 0:
                return Response({"brands": brands_data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"brands": [{"message":"No Data found"}]}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetMappBrandDenominationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        validate_mobileno_and_pswd_with_token(request)

        brand_id = get_brand_id_from_api_url(request)
        serializer = GetBrandDenominationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            points_data = LoyaltyPoints.objects.filter(mobileno=request.data['mobile_number'],brand_id=brand_id,status_flag=1)
            if len(points_data) > 0:
                bal_points = points_data[0].bal_points
            denomination_data = RewardGiftvouchers.objects.filter(rwrd_brand_id=request.data['rwrd_brand_id'],brand_id=brand_id, status_flag=1,issue_flag=0,gv_status_flag=1,gv_expiry__gte=now(),gv_points_value__lte=bal_points).values('gv_value', 'gv_points_value').distinct()
            if len(denomination_data) > 0:
                return Response({"denominations": denomination_data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"denominations": [{"message":"No Data found"}]}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MappRedeemPointsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        validate_mobileno_and_pswd_with_token(request)
        
        brand_id = get_brand_id_from_api_url(request)
        serializer = RedeemPointsSerializer(data=request.data)
        if serializer.is_valid():
            result = redeem_points_logic(serializer.validated_data,brand_id,'API','0')
            #print(result)
            return Response({
                "message": result.data.get("message"),
                "redeemed_points": result.data.get("redeem_points",0),
                "total_points": result.data.get("total_points",0)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetCustomerProfilewithPointsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        validate_mobileno_and_pswd_with_token(request)

        brand_id = get_brand_id_from_api_url(request)
        serializer = GetCustomerPtsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            points_data = LoyaltyPoints.objects.select_related('tier_id').filter(mobileno=request.data['mobile_number'],brand_id=brand_id,status_flag=1)
            
            if len(points_data) > 0:
                bal_points = points_data[0].bal_points
                tier_name = points_data[0].tier_id.tier_name
                tot_cust_earnpoints = points_data[0].tot_cust_earnpoints
                tot_cust_redeempoints = points_data[0].tot_cust_redeempoints
                tot_cust_purchase = points_data[0].tot_cust_purchase
                tot_cust_bills = points_data[0].tot_cust_bills
                
            
            cust_data = LoyaltyCustomers.objects.filter(mobileno=request.data['mobile_number'],brand_id=brand_id,status_flag=1)
            if len(cust_data) > 0:
                customer_name = cust_data[0].firstname
                customer_gender = cust_data[0].gender
                customer_email = cust_data[0].email
                customer_loyalty_id = cust_data[0].user_identifier
            
            return Response({"mobileno": request.data['mobile_number'],'customer_name':customer_name,'customer_gender':customer_gender,'customer_email':customer_email,'customer_loyalty_id':customer_loyalty_id,'balance_points':bal_points,'tier_name':tier_name,'tot_cust_earnpoints':tot_cust_earnpoints,'tot_cust_redeempoints':tot_cust_redeempoints,'tot_cust_purchase':tot_cust_purchase,'tot_cust_bills':tot_cust_bills}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class MappUploadCustBillAPIView(APIView):
    def post(self, request, *args, **kwargs):

        validate_mobileno_and_pswd_with_token(request)

        serializer = UploadBillSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            bill = serializer.save()
            return Response(
                {
                    "message": "Bill uploaded successfully!",
                    # "data": {
                    #     "id": bill.id,
                    #     "customer": bill.customer.name,
                    #     "mobile_no": bill.customer.mobile_no,
                    #     "location": bill.location.name,
                    #     "location_id": bill.location.id,
                    #     "file_path": bill.file_path.url,
                    #     "uploaded_at": bill.uploaded_at
                    # }
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "message": "There was an error with the upload.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )