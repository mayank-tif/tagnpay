from time import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
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


@method_decorator(csrf_exempt, name='dispatch')
class MissedCallAPIView(APIView):

    permission_classes = [AllowAny]

    allowed_ips = ['127.0.0.1','192.168.0.1','125.16.147.180','125.16.147.184','125.16.147.188','125.16.147.187','49.205.47.2','125.19.22.226']  # Replace with the actual IPs that are allowed

    def post(self, request, *args, **kwargs):
        # IP Restriction
        ip_address = request.META.get('REMOTE_ADDR')

        TblRequestAuditLogs.objects.create(mobileno=request.data['mobile_number'],location_id=request.data['location'],town=request.data['circle'],bill_date=request.data['date'],period=request.data['time'],source_ip=ip_address,reg_source='MissedCall',api_flag='Missed Call API')

        if ip_address not in self.allowed_ips:
            return HttpResponseForbidden("Access denied: Unauthorized IP address")

        # Deserialize and validate the incoming data
        serializer = MissedCallSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Missed call request received successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DummyUser:
    def __init__(self, username):
        self.username = username
        self.id = 1

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        username = request.headers.get('Username')
        password = request.headers.get('Password')
        
        if (username != RFAPI_USERNAME or password != RFAPI_PASSWORD) and (username != TnPAPP_API_USERNAME or password != TnPAPP_API_PASSWORD):
            return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer.is_valid(raise_exception=True)
        # If validation is successful, generate token
        #user = authenticate(username=request.data['username'], password=request.data['password'])
        #if not user:
        #    return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        # Get tokens

        user = DummyUser(username)
                
        # Generate JWT token
        token = AccessToken.for_user(user)

        token['mobile_number'] = request.data.get("mobileno")
        token['username'] = username

        return Response({"access_token": str(token)}, status=status.HTTP_200_OK)
    

class EarnPointsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        validate_mobile_number_with_token(request)
        
        brand_id = get_brand_id_from_api_url(request)
        serializer = EarnPointsSerializer(data=request.data)
        if serializer.is_valid():
            result = earn_points_logic(serializer.validated_data,brand_id,'API','0')
            #print(result)
            return Response({
                "message": result.data.get("message"),
                "earned_points": result.data.get("earn_points",0),
                "total_points": result.data.get("total_points",0)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomerRegAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        print(request.data['reg_source'])
        if request.data['reg_source'] == "MobileApp":
            validate_mobileno_and_deviceid_with_token(request)
        else:    
            validate_mobile_number_with_token(request)


        brand_id = get_brand_id_from_api_url(request)
        serializer = CustomerRegSerializer(data=request.data)
        if serializer.is_valid():
            result = register_customer(serializer.validated_data,brand_id,'0')
            #print(result)
            return Response({
                "message": result.data.get("message")
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetCustomerPointsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        validate_mobile_number_with_token(request)

        brand_id = get_brand_id_from_api_url(request)
        serializer = GetCustomerPtsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            points_data = LoyaltyPoints.objects.filter(mobileno=request.data['mobile_number'],brand_id=brand_id,status_flag=1)
            if len(points_data) > 0:
                bal_points = points_data[0].bal_points
                return Response({"mobileno": request.data['mobile_number'],'balance_points':bal_points}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetCustomerPtsBrandsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        validate_mobile_number_with_token(request)

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


class GetBrandDenominationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        validate_mobile_number_with_token(request)

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

class RedeemPointsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        validate_mobile_number_with_token(request)
        
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
    

# class PendingBillsAPIView(APIView):

#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
        
#         validate_mobile_number_with_token(request)
        
#         serializer = PendingBillSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Pending Bill request received successfully"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PendingBillsAPIView(APIView):

    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):

        validate_mobile_number_with_token(request)

        serializer = PendingBillSerializer(data=request.data, context={'request': request})
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
            login_otp = GenerateOTP.generate_otp()
            enc_login_otp = str_encrypt(str(login_otp))
            loginotp_data = CustomerLoginOtpVerification.objects.filter(mobileno=request.data['mobile_number'],brand_id=brand_id,status_flag=1,flag='login')
            if len(loginotp_data) > 0:
                CustomerLoginOtpVerification.objects.filter(mobileno=request.data['mobile_number'],brand_id=brand_id,status_flag=1,flag='login').update(secureotp=enc_login_otp,source='MobileApp',updated_on=datetime.now(),support_remarks=login_otp)
            else:    
                CustomerLoginOtpVerification.objects.create(mobileno=request.data['mobile_number'],brand_id=brand_id,secureotp=enc_login_otp,source='MobileApp',flag='login',support_remarks=login_otp)
            return Response({"message": "OTP sent successfully."}, status=status.HTTP_201_CREATED)
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
                               
                user = DummyUser(TnPAPP_API_USERNAME)
                
                verify_access_token = AccessToken.for_user(user)

                verify_access_token['mobile_number'] = request.data.get("mobile_number")
                verify_access_token['login_val'] = enc_login_otp
                verify_access_token['custbndid'] = str(brand_id) + user_identifier
                

                verify_access_token.set_exp(lifetime=timedelta(days=30))

                return Response({"message": "Customer verified successfully","customer_name":customer_name,"balance_points":bal_points,"tier_name":tier_name,"verify_access_token":str(verify_access_token)}, status=status.HTTP_201_CREATED)
            else:    
                return Response({"message": "Invalid OTP!!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


