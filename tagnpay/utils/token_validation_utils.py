from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from django.urls import resolve
from tagnpayloyalty.helpers import get_brand_id_from_api_url
from tagnpayloyalty.models import LoyaltyCustomers, CustomerLoginOtpVerification
from rest_framework import status
from rest_framework.exceptions import APIException

class UnauthorizedValidationError(APIException):
    status_code = 401
    default_detail = "Unauthorized request due to validation error."
    default_code = "unauthorized_validation_error"

def validate_mobile_number_with_token(request):
    """
    Utility function to validate mobile number from JWT and request body.
    Raises exceptions if validation fails.
    """

    current_url_name = resolve(request.path_info).url_name
    #print(current_url_name)
    # Extract mobile number from request body
    body_mobile_number = request.data.get('mobile_number')
    if current_url_name == "cust-reg-api":
        body_mobile_number = request.data.get('mobileno')

    #print(body_mobile_number)
    if not body_mobile_number:
        raise ValidationError({"error":"Mobile number is required in the request body."})

    # Extract JWT token from headers
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise AuthenticationFailed({'error':'JWT token not provided or invalid.'})

    token = auth_header.split(' ')[1]  # Extract the token after 'Bearer'
    jwt_authenticator = JWTAuthentication()
    validated_token = jwt_authenticator.get_validated_token(token)

    # Compare mobile numbers
    token_mobile_number = validated_token.get('mobile_number')
    #print(token_mobile_number)
    if str(body_mobile_number) != str(token_mobile_number):
        raise ValidationError({'error':'Mobile number does not match with Token.'})


def validate_mobileno_and_deviceid_with_token(request):
    """
    Utility function to validate mobile number from JWT and request body.
    Raises exceptions if validation fails.
    """

    current_url_name = resolve(request.path_info).url_name
    #print(current_url_name)
    # Extract mobile number from request body
    body_mobile_number = request.data.get('mobile_number')
    body_deviceid = request.data.get('deviceid')
    if current_url_name == "mapp-cust-reg-api":
        body_mobile_number = request.data.get('mobileno')

    #print(body_mobile_number)
    if not body_mobile_number:
        raise ValidationError({"error":"Mobile number is required in the request body."})
    if not body_deviceid:
        raise ValidationError({"error":"Deviceid is required in the request body."})

    # Extract JWT token from headers
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise AuthenticationFailed({'error':'JWT token not provided or invalid.'})

    token = auth_header.split(' ')[1]  # Extract the token after 'Bearer'
    jwt_authenticator = JWTAuthentication()
    validated_token = jwt_authenticator.get_validated_token(token)

    # Compare mobile numbers
    token_mobile_number = validated_token.get('mobile_number')
    token_deviceid = validated_token.get('deviceid')
    #print(token_mobile_number)
    if str(body_mobile_number) != str(token_mobile_number):
        raise UnauthorizedValidationError({'error':'Mobile number does not match with Token.'})

    if str(body_deviceid) != str(token_deviceid):
        raise UnauthorizedValidationError({'error':'Deviceid does not match with Token.'})
    

def validate_mobileno_and_pswd_with_token(request):
    
    brand_id = get_brand_id_from_api_url(request)

    current_url_name = resolve(request.path_info).url_name
    #print(current_url_name)
    # Extract mobile number from request body
    body_mobile_number = request.data.get('mobile_number')


    #print(body_mobile_number)
    if not body_mobile_number:
        raise ValidationError({"error":"Mobile number is required in the request body."})
    
    # Extract JWT token from headers
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise AuthenticationFailed({'error':'JWT token not provided or invalid.'})

    token = auth_header.split(' ')[1]  # Extract the token after 'Bearer'
    jwt_authenticator = JWTAuthentication()
    validated_token = jwt_authenticator.get_validated_token(token)

    # Compare mobile numbers
    token_mobile_number = validated_token.get('mobile_number')
    token_login_val = validated_token.get('login_val')
    #print(token_mobile_number)
    if str(body_mobile_number) != str(token_mobile_number):
        raise UnauthorizedValidationError({'error':'Mobile number does not match with Token.'})

    loginotp = CustomerLoginOtpVerification.objects.filter(mobileno=body_mobile_number,brand_id=brand_id,status_flag=1,flag='login').values_list('secureotp', flat=True).first()

    if str(token_login_val) != str(loginotp):
        raise UnauthorizedValidationError({'error':'Token values does not match.'})
