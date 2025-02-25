from django.urls import path
from .views import *
from RFAPIS.views import CustomerRegAPIView

app_name = 'MAppApis'  # Define app_name here for namespacing

urlpatterns = [
    path('generate-app-token/', GenerateAppTokenView.as_view(), name='generate-app-token'),
    path('validate-cust-send-otp/', ValidateCustAndSendOTPAPIView.as_view(), name='validate-cust-send-otp'),
    path('verify-cust-cred/', VerifyCustLoginOTPAPIView.as_view(), name='verify-cust-cred'),
    path('mapp-cust-registration/', CustomerRegAPIView.as_view(), name='mapp-cust-reg-api'),
    path('get-cust-transactions-api/', GetCustTransactionsAPIView.as_view(), name='get-cust-transactions-api'),
    path('mapp-upload-cust-bill-api/', MappUploadCustBillAPIView.as_view(), name='mapp-upload-cust-bill-api'),
    path('get-brands-by-cust-points/', GetMappCustomerPtsBrandsAPIView.as_view(), name='get-brands-by-cust-points'),
    path('get-brand-denomination-by-pts/', GetMappBrandDenominationAPIView.as_view(), name='get-brand-denomination-by-pts'),
    path('mapp-redeem-points-api/', MappRedeemPointsAPIView.as_view(), name='mapp-redeem-points-api'),
    path('get-cust-details/', GetCustomerProfilewithPointsAPIView.as_view(), name='get-cust-details'),
]