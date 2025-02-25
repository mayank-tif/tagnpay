from django.urls import path
from .views import *

app_name = 'RFAPIS'  # Define app_name here for namespacing

urlpatterns = [
    path('missed-call/', MissedCallAPIView.as_view(), name='missed-call-api'),
    path('generate-token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('earn-points/', EarnPointsAPIView.as_view(), name='earn-points-api'),
    path('customer-registration/', CustomerRegAPIView.as_view(), name='cust-reg-api'),
    path('get-customer-points/', GetCustomerPointsAPIView.as_view(), name='get-cust-points'),
    path('get-brands-by-points/', GetCustomerPtsBrandsAPIView.as_view(), name='get-brands-by-points'),    
    path('get-brand-denomination/', GetBrandDenominationAPIView.as_view(), name='get-brand-denomination'),
    path('issue-voucher/', RedeemPointsAPIView.as_view(), name='issue-voucher'),
    path('pending-bill/', PendingBillsAPIView.as_view(), name='pending-bill'),
    path('validate-cust-send-otp/', ValidateCustAndSendOTPAPIView.as_view(), name='validate-cust-send-otp'),
    path('verify-cust-cred/', VerifyCustLoginOTPAPIView.as_view(), name='verify-cust-cred'),
    path('generate-app-token/', GenerateAppTokenView.as_view(), name='generate-app-token'),    
]