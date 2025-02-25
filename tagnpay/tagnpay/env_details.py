import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

RFAPI_USERNAME = os.getenv('API_USERNAME')
RFAPI_PASSWORD = os.getenv('API_PASSWORD')
KX_SMS_API_KEY = os.getenv('KX_SMS_API_SECRET_KEY')
config_Registration_SMS_text = os.getenv('config_Reg_wecome_SMS_text')
config_Transaction_Pts_SMS_text = os.getenv('config_Trans_pts_SMS_text')
config_Pts_redemption_SMS_text = os.getenv('config_Pts_redemption_SMS_text')
TnPAPP_API_USERNAME = os.getenv('TnPAPP_API_USERNAME')
TnPAPP_API_PASSWORD = os.getenv('TnPAPP_API_PASSWORD')
config_login_otp_SMS_text = os.getenv('config_login_otp_SMS_text')
