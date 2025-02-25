from django.db import models
from django.utils import timezone
from django.db.models import Max
import string
import secrets
import math
import datetime
import logging
logger = logging.getLogger(__name__)

# Create your models here.

class MstRole(models.Model):
    id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=20)
    role_code = models.CharField(max_length=20, unique=True)
    updated_on = models.DateTimeField()
    #brand_id = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)

    def __str__(self):
        return self.role_name


class CountryMst(models.Model):
    country_id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=50)
    country_code = models.CharField(max_length=50, null=True)
    created_on = models.DateTimeField(default=datetime.datetime.now)
    status_flag = models.IntegerField(default=1)
    user_id = models.IntegerField()
    brand_id = models.IntegerField(null=True)
    updated_by = models.CharField(max_length=50, null=True)
    updated_on = models.DateTimeField(null=True)
    support_remark = models.TextField(max_length=500, null=True)

    def __str__(self):
        return self.country_name


class ZoneMst(models.Model):
    zone_id = models.AutoField(primary_key=True)
    zone_name = models.CharField(max_length=50)
    zone_description = models.CharField(max_length=50)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    user_id = models.IntegerField()
    brand_id = models.IntegerField(null=True)
    updated_by = models.IntegerField(null=True)
    updated_on = models.DateTimeField(null=True)
    support_remark = models.TextField(max_length=500, null=True)
    country_id = models.ForeignKey(CountryMst, on_delete=models.CASCADE)

    def __str__(self):
        return self.zone_name


class StateMst(models.Model):
    states_id = models.AutoField(primary_key=True)
    states_name = models.CharField(max_length=50)
    states_code = models.CharField(max_length=50, null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    country_id = models.ForeignKey(CountryMst, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    brand_id = models.IntegerField(null=True)
    updated_by = models.IntegerField(null=True)
    updated_on = models.DateTimeField(null=True)
    support_remark = models.TextField(max_length=500, null=True)

    def __str__(self):
        return self.states_name


class CityMst(models.Model):
    city_id = models.AutoField(primary_key=True)
    city_name = models.CharField(max_length=50)
    city_code = models.CharField(max_length=50, null=True)
    state_id = models.ForeignKey(StateMst, on_delete=models.CASCADE, null=True)
    country_id = models.ForeignKey(CountryMst, on_delete=models.CASCADE)
    zone_id = models.ForeignKey(ZoneMst, on_delete=models.CASCADE, null=True)
    user_id = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    brand_id = models.IntegerField(null=True)
    updated_by = models.IntegerField(null=True)
    updated_on = models.DateTimeField(null=True)
    support_remark = models.TextField(max_length=500, null=True)

    def __str__(self):
        return self.city_name


class DistrictsMst(models.Model):
    district_id = models.AutoField(primary_key=True)
    district_name = models.CharField(max_length=50)
    district_code = models.CharField(max_length=50)
    zone_id = models.ForeignKey(ZoneMst, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    updated_by = models.IntegerField()
    updated_on = models.DateTimeField()
    support_remark = models.TextField(max_length=500)

    def __str__(self):
        return self.district_name

class LocationClassMst(models.Model):
    loc_class_id = models.AutoField(primary_key=True)
    loc_class_name = models.CharField(max_length=50)
    loc_class_descr = models.CharField(max_length=50)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    user_id = models.IntegerField()
    brand_id = models.IntegerField(null=True)
    updated_by = models.IntegerField(null=True)
    updated_on = models.DateTimeField(null=True)
    support_remark = models.TextField(max_length=500, null=True)

    def __str__(self):
        return self.loc_class_name

class LocationCategoryMst(models.Model):
    loc_category_id = models.AutoField(primary_key=True)
    loc_category_name = models.CharField(max_length=50)
    loc_category_val = models.CharField(max_length=50)
    loc_category_description = models.CharField(max_length=50)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    user_id = models.IntegerField()
    brand_id = models.IntegerField(null=True)
    updated_by = models.IntegerField(null=True)
    updated_on = models.DateTimeField(null=True)
    support_remark = models.TextField(max_length=500, null=True)

    def __str__(self):
        return self.loc_category_name


class CompanyMst(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_code = models.CharField(max_length=10, null=True)
    company_name = models.CharField(max_length=200)
    company_description = models.TextField(max_length=500, null=True)
    company_address = models.TextField(max_length=500, null=True)
    company_location = models.CharField(max_length=100, null=True)
    company_city = models.CharField(max_length=100, null=True)
    company_zip = models.CharField(max_length=100, null=True)
    company_state = models.CharField(max_length=100, null=True)
    company_country = models.CharField(max_length=100, null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    user_id = models.IntegerField()
    brand_id = models.IntegerField(null=True)
    updated_by = models.IntegerField(null=True)
    updated_on = models.DateTimeField(null=True)
    support_remarks = models.TextField(max_length=500, null=True)

    def __int__(self):
        return self.company_id

class LocationMst(models.Model):
    class Meta:
        unique_together = (('brand_id', 'location_code'))

    location_id = models.AutoField(primary_key=True)
    location_Name = models.CharField(max_length=100)
    brand_id = models.IntegerField(null=True)
    location_mgr = models.CharField(max_length=100, null=True)
    location_address = models.TextField(max_length=500, null=True)
    location_location = models.CharField(max_length=200, null=True)
    location_city = models.IntegerField(null=True)
    location_state = models.IntegerField(null=True)
    location_country = models.IntegerField(null=True)
    location_zone = models.IntegerField(null=True)
    location_zip = models.IntegerField(null=True)
    location_mobnumber = models.BigIntegerField(null=True)
    location_phonenumber = models.BigIntegerField(null=True)
    location_emailid = models.EmailField(max_length=50, null=True)
    location_code = models.CharField(max_length=50,null=True)
    company_id = models.IntegerField(null=True)
    location_district = models.IntegerField(null=True)
    pan_no = models.CharField(max_length=50, null=True)
    gst_no = models.CharField(max_length=50, null=True)
    adhaar_no = models.CharField(max_length=50, null=True)
    location_commission = models.IntegerField(null=True)
    location_class = models.IntegerField(null=True)
    location_long = models.CharField(max_length=100, null=True)
    location_lat = models.CharField(max_length=100, null=True)
    location_category = models.CharField(max_length=100, null=True)
    live_location_status = models.IntegerField(null=True)
    live_location_date = models.DateTimeField(null=True)
    deactivated_on = models.DateTimeField(null=True)
    deactivated_by = models.IntegerField(null=True)
    default_passcode = models.TextField(max_length=500, null=True)
    user_id = models.IntegerField(null=True)
    updated_by = models.IntegerField(null=True)
    status_flag = models.IntegerField(default=1)
    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(null=True)
    status_flag = models.IntegerField(default=1)
    support_remarks = models.TextField(max_length=500, null=True)
    sales_executive_id = models.IntegerField(null=True)
    sales_executive_name = models.CharField(max_length=100, null=True)
    sales_executive_number = models.BigIntegerField(null=True)
    location_file_name = models.CharField(max_length=100, null=True)

    def __int__(self):
        return self.location_id
    

class CategoryMst(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=150, null=True)
    category_description = models.TextField(max_length=500, null=True)
    category_icon = models.TextField(max_length=500, null=True)
    category_img = models.TextField(max_length=500, null=True)
    category_file_name = models.TextField(max_length=250, null=True)
    user_id = models.IntegerField(null=True)
    brand_id = models.IntegerField(null=True)
    updated_on = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)

    def __int__(self):
        return self.category_id


class RewardBrandsMst(models.Model):
    id = models.AutoField(primary_key=True)
    rwrd_brand_name = models.CharField(max_length=100, null=True)
    rwrd_brand_product_code = models.CharField(max_length=100, null=True)
    rwrd_brand_descr = models.TextField(max_length=1000, null=True)
    company_name = models.CharField(max_length=100, null=True)
    licensee_name = models.CharField(max_length=100, null=True)
    contact_person = models.CharField(max_length=100, null=True)
    contact_number = models.BigIntegerField(null=True)
    rwrd_brand_floor = models.TextField(max_length=500, null=True)
    rwrd_brand_shopno = models.CharField(max_length=100, null=True)
    rwrd_brand_city = models.IntegerField(null=True)
    rwrd_brand_zip = models.IntegerField(null=True)
    rwrd_brand_state = models.IntegerField(null=True)
    rwrd_brand_country = models.IntegerField(null=True)
    category_id = models.ForeignKey(CategoryMst, on_delete=models.CASCADE, blank=True, null=True, db_column='category_id')
    agreement_date = models.DateTimeField(null=True)
    rwrd_brand_logo = models.CharField(max_length=100, null=True)
    rwrd_brand_image_url = models.TextField(max_length=500, null=True, blank=True)
    category_list = models.JSONField(null=True)
    websiteurl = models.CharField(max_length=100, null=True)
    user_id = models.IntegerField(null=True)
    brand_id = models.IntegerField(null=True)
    updated_on = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    rwrd_brand_identifier = models.CharField(max_length=250, null=True)
    brand_file_name = models.TextField(max_length=250, null=True)

    def __int__(self):
        return self.brand_id

class MstUserLogins(models.Model):
    class Meta:
        unique_together = (('loginname', 'brand_id'),)

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=10, null=True)
    firstname = models.CharField(max_length=100, null=True)
    middlename = models.CharField(max_length=50, null=True)
    lastname = models.CharField(max_length=100, null=True)
    brand_id = models.IntegerField(null=True)
    address = models.CharField(max_length=250, null=True)
    email = models.CharField(max_length=50, null=True)
    loginname = models.CharField(max_length=20)
    securepassword = models.CharField(max_length=200, null=True)
    roleid = models.ForeignKey(MstRole, on_delete=models.CASCADE, null=True)
    cityid = models.IntegerField(null=True)
    stateid = models.IntegerField(null=True)
    created_by = models.CharField(max_length=100, null=True)
    countryid = models.CharField(max_length=50, null=True)
    districtid = models.IntegerField(null=True)
    zipcode = models.CharField(max_length=8, null=True)
    phonenumber = models.CharField(max_length=20, null=True)
    mobilenumber = models.CharField(max_length=15, null=True)
    companyid = models.IntegerField(null=True)
    locationid = models.IntegerField(null=True)
    deactivated_by = models.IntegerField(null=True)
    updated_by = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    mask_flag = models.IntegerField(null=True)
    deactivated_on = models.DateTimeField(null=True)
    updated_on = models.DateTimeField(null=True)
    updated_type = models.CharField(max_length=50, null=True)
    last_log_id = models.IntegerField(null=True)
    tech_remarks = models.TextField(max_length=500, null=True)
    profile_pic = models.CharField(max_length=100, null=True)
    additional_info = models.JSONField(null=True)

    def __str__(self):
        return self.loginname


class Tiers(models.Model):
    tier_id = models.AutoField(primary_key=True)
    tier_name = models.CharField(max_length=50, null=True)
    tier_minimum_value = models.IntegerField(null=True)
    tier_maximum_value = models.IntegerField(null=True)
    tier_discount = models.FloatField(null=True)
    tier_type = models.CharField(max_length=20, null=True)
    tier_earn_points = models.FloatField(null=True)
    tier_pts_per_rs = models.FloatField(null=True)
    tier_logic_type = models.CharField(max_length=20, null=True)
    customer_type = models.CharField(max_length=50, null=True)
    rwrd_brand_id = models.ForeignKey(RewardBrandsMst, on_delete=models.CASCADE, blank=True, null=True, db_column='rwrd_brand_id')
    brand_id = models.IntegerField(null=True)
    user_id = models.IntegerField(null=True)
    tier_offer_id = models.IntegerField(null=True)
    tier_configured_on = models.CharField(max_length=50, null=True)
    tier_offer_sms_text = models.TextField(max_length=1000, null=True)
    tier_offer_vld = models.CharField(max_length=50, null=True)
    deactivated_by = models.IntegerField(null=True)
    deactivated_on = models.DateTimeField(null=True)
    updated_on = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now, null=True)
    status_flag = models.IntegerField(default=1)
    

    def tier_logs(self):
        try:
            max_logid = TiersLogs.objects.aggregate(Max('logid'))
            if max_logid['logid__max'] is None:
                logid = 1
            else:
                # logid = max_logid['logid__max'] + 1
                logid = max_logid['logid__max']
            # if (self.status_flag!=0):
            TiersLogs.objects.update_or_create(
                tier_id=self.tier_id,
                logid=logid,
                logactivity="After Update",
                tier_name=self.tier_name,
                tier_minimum_value=self.tier_minimum_value,
                tier_maximum_value=self.tier_maximum_value,
                tier_discount=self.tier_discount,
                tier_type=self.tier_type,
                tier_earn_points=self.tier_earn_points,
                tier_per_rs=self.tier_per_rs,
                customer_type=self.customer_type,
                rwrd_brand_id = self.rwrd_brand_id,
                brand_id=self.brand_id,
                user_id=self.user_id,
                tier_logic_type=self.tier_logic_type,
                tier_offer_id=self.tier_offer_id,
                tier_configured_on=self.tier_configured_on,
                tier_offer_sms_text=self.tier_offer_sms_text,
                tier_offer_vld=self.tier_offer_vld,
                deactivated_on=self.deactivated_on,
                deactivated_by=self.deactivated_by,
                updated_by=self.updated_by,
                updated_on=self.updated_on,
                created_on=self.created_on                
            )
        except:
            pass

    def __int__(self):
        return self.tier_id
        #return "tier name: " + str(self.tier_name) + ",-----Tier logic type: " + str(self.tier_logic_type) + "---Brand id: " + str(self.brand_id)

    def save(self, *args, **kwargs):
        self.tier_logs()
        super(Tiers, self).save(*args, **kwargs)


class TiersLogs(models.Model):
    id = models.AutoField(primary_key=True)
    tier_id = models.IntegerField(null=True)
    logid = models.IntegerField(null=True)
    logactivity = models.CharField(max_length=50)
    tier_name = models.CharField(max_length=50, null=True)
    tier_minimum_value = models.IntegerField(null=True)
    tier_maximum_value = models.IntegerField(null=True)
    tier_discount = models.FloatField(null=True)
    tier_type = models.CharField(max_length=20, null=True)
    tier_earn_points = models.FloatField(null=True)
    tier_per_rs = models.FloatField(null=True)
    customer_type = models.CharField(max_length=50, null=True)
    rwrd_brand_id = models.IntegerField(null=True)
    brand_id = models.IntegerField(null=True)
    user_id = models.IntegerField(null=True)
    tier_logic_type = models.CharField(max_length=20, null=True)
    tier_offer_id = models.CharField(max_length=18, null=True)
    tier_configured_on = models.CharField(max_length=50, null=True)
    tier_offer_sms_text = models.TextField(max_length=1000, null=True)
    tier_offer_vld = models.CharField(max_length=50, null=True)
    deactivated_by = models.IntegerField(null=True)
    deactivated_on = models.DateTimeField(null=True)
    updated_on = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now, null=True)
    status_flag = models.IntegerField(default=1)
    

    def __str__(self):
        return "Tier name: " + self.tier_name + ",--------Tier Logic type: " + self.tier_logic_type


def user__identifier():
    num = 10
    no = LoyaltyCustomers.objects.aggregate(Max('id'))
    alpha_numb = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for x in range(num))
    if no['id__max'] == None:
        return alpha_numb + str(1)
    else:
        id = no['id__max'] + 1
        return alpha_numb + str(id)


def uniquenum_user():
    num = 10
    alpha_numb = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for x in range(num))
    return alpha_numb.upper()


class LoyaltyCustomers(models.Model):
    class Meta:
        unique_together = (('mobileno', 'brand_id'),)

    id = models.AutoField(primary_key=True)
    mobileno = models.BigIntegerField()
    brand_id = models.IntegerField(null=True)
    user_id = models.CharField(max_length=50)
    homeno = models.CharField(max_length=50, null=True)
    title = models.CharField(max_length=10, null=True)
    firstname = models.CharField(max_length=50, null=True)
    lastname = models.CharField(max_length=50, null=True)
    gender = models.CharField(max_length=10, null=True)
    dob = models.DateField(null=True)
    doa = models.DateField(null=True)
    age = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=150, null=True)
    address1 = models.CharField(max_length=200, null=True)
    address2 = models.CharField(max_length=200, null=True)
    town = models.CharField(max_length=50, null=True)
    country = models.ForeignKey(CountryMst, on_delete=models.CASCADE, null=True, blank=True, db_column='country')
    city = models.ForeignKey(CityMst, on_delete=models.CASCADE, null=True, blank=True, db_column='city')
    district = models.CharField(max_length=50, null=True)
    state = models.ForeignKey(StateMst, on_delete=models.CASCADE, null=True, blank=True, db_column='state')
    zipcode = models.CharField(max_length=10, null=True)
    uniquenum = models.CharField(max_length=50, default=uniquenum_user)
    dobday = models.CharField(max_length=2, null=True)
    dobmonth = models.CharField(max_length=2, null=True)
    dobyear = models.CharField(max_length=4, null=True)
    doaday = models.CharField(max_length=2, null=True)
    doamonth = models.CharField(max_length=2, null=True)
    doayear = models.CharField(max_length=4, null=True)
    occupation = models.CharField(max_length=255, null=True)
    member_type = models.CharField(max_length=50, default="New")
    location_id = models.ForeignKey(LocationMst, on_delete=models.CASCADE, null=True, db_column='location_id')
    #location = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    created_month = models.IntegerField(blank=True, null=True)
    created_year = models.IntegerField(blank=True, null=True)
    upload_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    data_source = models.IntegerField(default=0)
    reg_source = models.CharField(max_length=50, null=True)
    genuine_flag = models.IntegerField(null=True)
    user_id_old = models.IntegerField(null=True)
    store_id_old = models.IntegerField(null=True)
    tech_remarks = models.TextField(max_length=500, null=True)
    profile_updatedon = models.DateTimeField(null=True)
    user_identifier = models.CharField(max_length=40, default=user__identifier, unique=True)
    customer_type = models.CharField(max_length=20, null=True)
    customer_segment = models.CharField(max_length=50, null=True)
    customer_subsegment = models.CharField(max_length=50, null=True)
    customer_group = models.CharField(max_length=50, null=True)
    customer_id = models.CharField(max_length=50, null=True, unique=True)
    adhaar_card_num = models.TextField(null=True)
    gst_num = models.CharField(max_length=50, null=True)
    pan_num = models.TextField(null=True)
    latitude = models.CharField(max_length=50, null=True)
    longitude = models.CharField(max_length=50, null=True)
    access_token = models.TextField(null=True)
    device_id = models.CharField(max_length=32, null=True)
    user_category = models.CharField(max_length=255, null=True)
    profile_pic = models.CharField(max_length=100, null=True)
    is_kyc_done = models.IntegerField(default=0)
    kyc_method = models.CharField(max_length=50, null=True)
    approval_date = models.DateTimeField(null=True)
    upload_transaction_id = models.CharField(max_length=50, null=True, blank=True)
    masked_adhaar_card_num = models.CharField(max_length = 20,null=True)
    masked_pan_num = models.CharField(max_length=20, null=True)
    metadata_json = models.JSONField(null=True)
    approver_by = models.IntegerField(null=True)
    vpa_id = models.CharField(max_length=256, null=True)
    ifsc = models.CharField(max_length=20, null=True)
    account_no = models.CharField(max_length=256, null=True)
    landmark = models.CharField(max_length=100, null=True)
    mall_brand_id = models.ForeignKey(RewardBrandsMst, on_delete=models.CASCADE, blank=True, null=True, db_column='mall_brand_id')
    #mall_brand = models.IntegerField(null=True)

    def __int__(self):
        return self.mobileno

class LoyaltyPoints(models.Model):
    class Meta:
        unique_together = (('mobileno', 'brand_id'),)

    id = models.AutoField(primary_key=True)
    mobileno = models.BigIntegerField()
    brand_id = models.IntegerField(null=True)
    user_id = models.CharField(max_length=100)
    store_id = models.CharField(max_length=100)
    name = models.CharField(null=True, max_length=50)
    bal_points = models.FloatField(default=0)
    bal_cash_val = models.FloatField(default=0)
    created_On = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    customer_id = models.CharField(max_length=50, null=True, unique=True)
    last_trans_date = models.DateTimeField(null=True)
    status_flag = models.IntegerField(default=1)
    tier_id = models.ForeignKey(Tiers, on_delete=models.CASCADE, blank=True, null=True, db_column='tier_id')
    tot_expired_points = models.FloatField(default=0)
    tot_bonus_points = models.FloatField(default=0)
    prev_bal_points = models.FloatField(default=0)
    prev_loyalty_purchase = models.FloatField(default=0)
    bal_points_bkp = models.FloatField(null=True)
    bal_cash_val_bkp = models.FloatField(default=0)
    tot_bonuspoints_bkp = models.FloatField(default=0)
    tot_expiredpoints_bkp = models.FloatField(default=0)
    tier_id_bkp = models.IntegerField(null=True)
    tech_remarks = models.TextField(null=True, max_length=500)
    tot_cust_bills = models.IntegerField(default=0)
    tot_cust_purchase = models.FloatField(default=0)
    tot_cust_new_purchase = models.FloatField(default=0)
    tot_cust_earnpoints = models.FloatField(default=0)
    tot_cust_redeempoints = models.FloatField(default=0)
    prev_cust_earnpoints = models.FloatField(default=0)
    prev_cust_redeempoints = models.FloatField(default=0)
    prev_cust_bonuspoints = models.FloatField(default=0)
    prev_cust_expiredpoints = models.FloatField(default=0)
    tier_reset_date = models.DateTimeField(null=True)
    tier_upgrade_date = models.DateTimeField(null=True)

    def __int__(self):
        return self.mobileno


class TblSettings(models.Model):
    class PointIssuedOn(models.IntegerChoices):
        bill_amount_withtax = 1
        bill_amount_withouttax = 2
        fresh_item_withtax = 3
        fresh_item_withouttax = 4
        fresh_bill_withtax = 5  # no discount bill with tax
        fresh_bill_withouttax = 6  # no discount bill without tax

    class LoyaltyEnableOn(models.IntegerChoices):
        total_purchase = 1  # old and new purchase
        new_purchase = 2

    class SmsSentStatus(models.IntegerChoices):
        enable = 1
        disable = 2

    class MobileMask(models.IntegerChoices):
        enable = 1
        disable = 0

    id = models.AutoField(primary_key=True)
    header_name = models.CharField(max_length=100, null=True)
    user_id = models.TextField(max_length=10)
    brand_name = models.CharField(max_length=100, null=True)
    global_brandid = models.CharField(max_length=20, unique=True)
    brand_sms = models.CharField(max_length=100, null=True)
    brand_url = models.CharField(max_length=100, null=True)
    card_url = models.CharField(max_length=100, null=True)  # common file url for download mobile app according to OS
    coupon_redemption_type = models.CharField(max_length=20, null=True)
    earn_points_logic = models.CharField(max_length=25, null=True)
    voucher_redemption_type = models.CharField(max_length=20, null=True)
    static_coupon_redemption_type = models.CharField(max_length=20, null=True)
    #logo_img_name = models.ImageField(upload_to= lambda instance,filename:FileUtils.get_upload_file_path(instance,filename,FilePathConstant.TblConfigSetting.LOGO_IMG), null=True)
    logo_img_name = models.ImageField(upload_to=f'media/brands/', null=True, blank=True)
    sender_id = models.CharField(max_length=10, null=True)
    approver_mob_no = models.BigIntegerField(null=True)
    sender_id_length = models.IntegerField(null=True)
    shortcode_keyword = models.CharField(max_length=15, null=True)
    otp_validity = models.CharField(max_length=5, null=True)
    active_passive_val = models.IntegerField(null=True)
    fraud_purchase_val = models.IntegerField(null=True)
    fraud_visits_val = models.IntegerField(null=True)
    fraud_redeem_points_val = models.IntegerField(null=True)
    fraud_avg_trans_val = models.IntegerField(null=True)
    country_code = models.CharField(max_length=5, null=True)
    mobileno_mask = models.IntegerField(choices=MobileMask.choices, default=1)
    point_issuedon = models.IntegerField(choices=PointIssuedOn.choices,
                                         null=True)  # bill_amount_withtax / bill_amount_withouttax, fresh_item_withtax / fresh_item_withouttax / fresh_bill_withtax / fresh_bill_withouttax
    mobile_startwith = models.CharField(max_length=15, null=True)
    mobile_length = models.CharField(max_length=5, null=True)
    instance_logic = models.CharField(max_length=20, null=True)
    redeem_logic = models.CharField(max_length=20, null=True)
    loyalty_db_id = models.IntegerField(null=True)
    loyalty_enabled_on = models.IntegerField(choices=LoyaltyEnableOn.choices, null=True)  # total_purchase/new_purchase
    sms_sent_status = models.IntegerField(choices=SmsSentStatus.choices, default=1)
    campaign_price = models.CharField(max_length=10, null=True)
    sms_api_url = models.TextField(max_length=300, null=True)  # ===API to send sms to users==========
    sms_api_url_trans = models.TextField(max_length=300, null=True)  # ===API to send sms to users==========
    sms_api_uid = models.CharField(max_length=20, null=True)
    sms_api_pswd = models.CharField(max_length=50, null=True)
    analytics_url = models.CharField(max_length=100, null=True)
    brand_image1 = models.CharField(max_length=50, null=True)
    brand_image2 = models.CharField(max_length=50, null=True)
    brand_image3 = models.CharField(max_length=50, null=True)
    brand_image4 = models.CharField(max_length=50, null=True)
    brand_image5 = models.CharField(max_length=50, null=True)
    brand_image6 = models.CharField(max_length=50, null=True)
    redeem_rs_per_point = models.CharField(max_length=10, null=True)
    minimum_points_redeem = models.CharField(max_length=10, null=True)
    maximum_points_redeem = models.CharField(max_length=10, null=True)
    redeem_voucher_value = models.CharField(max_length=10, null=True)

    reg_offer_status = models.CharField(max_length=50, null=True, blank=True)
    reg_offer = models.CharField(max_length=20, null=True, blank=True)  # points/offer

    reg_offer_id = models.CharField(max_length=10, null=True, blank=True)
    reg_offer_text = models.CharField(max_length=500, null=True, blank=True)
    reg_offer_validity = models.CharField(max_length=5, null=True, blank=True)

    reg_bonus_points = models.CharField(max_length=10, null=True, blank=True)
    reg_points_offer_id = models.CharField(max_length=10, null=True, blank=True)
    reg_points_sms_id = models.CharField(max_length=10, null=True, blank=True)
    reg_points_sms_text = models.TextField(max_length=500, null=True, blank=True)
    reg_point_validity = models.CharField(max_length=10, null=True, blank=True)  # in days
    reg_points_sms_status = models.CharField(max_length=20, null=True, blank=True)  # yes/no

    reg_sms_text = models.TextField(max_length=500, null=True, blank=True)

    bday_offer_status = models.CharField(max_length=10, null=True)
    bday_offer = models.CharField(max_length=20, null=True)  # points/offer

    bday_offer_id = models.CharField(max_length=10, null=True)
    bday_offer_text = models.CharField(max_length=500, null=True)
    bday_offer_prior_days = models.IntegerField(null=True)
    bday_offer_post_days = models.IntegerField(null=True)

    bday_bonus_points = models.FloatField(max_length=10, null=True)
    bday_points_offer_id = models.IntegerField(null=True)
    bday_points_sms_id = models.IntegerField(null=True)
    bday_points_sms_text = models.TextField(max_length=500, null=True)
    bday_points_prior_days = models.CharField(max_length=10, null=True)
    bday_points_post_days = models.CharField(max_length=10, null=True)
    bday_points_sms_status = models.CharField(max_length=20, null=True)  # yes/no

    wa_offer_status = models.CharField(max_length=10, null=True)
    wa_offer = models.CharField(max_length=50, null=True)  # points/offer

    wa_offer_id = models.IntegerField(null=True)
    wa_offer_text = models.CharField(max_length=500, null=True)
    wa_offer_prior_days = models.IntegerField(null=True)
    wa_offer_post_days = models.IntegerField(null=True)

    wa_bonus_points = models.FloatField(max_length=10, null=True)
    wa_points_offer_id = models.IntegerField(null=True)
    wa_points_sms_id = models.IntegerField(null=True)
    wa_points_sms_text = models.TextField(max_length=500, null=True)
    wa_points_prior_days = models.IntegerField(null=True)
    wa_points_post_days = models.IntegerField(null=True)
    wa_points_sms_status = models.CharField(max_length=10, null=True)  # yes/no

    fb_offer_status = models.CharField(max_length=10, null=True)
    fb_offer = models.CharField(max_length=20, null=True)  # points/offer

    fb_offer_id = models.IntegerField(null=True)
    fb_offer_text = models.CharField(max_length=500, null=True)
    fb_offer_validity = models.IntegerField(null=True)

    fb_points_offer_id = models.IntegerField(null=True)
    fb_bonus_points = models.FloatField(max_length=10, null=True)
    fb_points_sms_id = models.IntegerField(null=True)
    fb_points_sms_text = models.TextField(max_length=500, null=True)
    fb_point_validity = models.IntegerField(null=True)  # in days
    fb_points_sms_status = models.CharField(max_length=20, null=True)  # yes/no
    # ===================Update Program==============================
    #config_update_profile_brand_logo = models.ImageField(upload_to=lambda instance, filename: FileUtils.get_upload_file_path(instance, filename,FilePathConstant.TblConfigSetting.CONFIG_UPDATE_PROFILE_BRAND_LOGO), null=True, blank=True)
    config_update_profile_brand_logo = models.CharField(max_length=100, null=True)
    
    #config_update_profile_brand_image = models.ImageField(
    #    upload_to=lambda instance,filename:FileUtils.get_upload_file_path(instance,filename,FilePathConstant.TblConfigSetting.CONFIG_UPDATE_PROFILE_BRAND_IMAGE), null=True, blank=True)
    config_update_profile_brand_image = models.CharField(max_length=100, null=True)
    config_profile_update_offer_status = models.CharField(max_length=10, null=True)
    config_profile_update_offer = models.CharField(max_length=20, null=True)  # points/offer

    config_profile_update_offer_id = models.CharField(max_length=10, null=True)
    config_profile_update_offer_text = models.CharField(max_length=500, null=True)
    config_profile_update_offer_validity = models.CharField(max_length=10, null=True)

    config_profile_update_bonus_points = models.CharField(max_length=10, null=True)
    config_profile_update_points_offer_id = models.CharField(max_length=10, null=True)
    config_profile_update_points_sms_id = models.CharField(max_length=10, null=True)
    config_profile_update_points_sms_text = models.TextField(max_length=500, null=True)
    config_profile_update_point_validity = models.CharField(max_length=10, null=True)
    config_profile_update_points_sms_status = models.CharField(max_length=20, null=True)  # yes/no
    # ========================END==============================
    # ================Referral fields=================================
    config_referral_referee_count = models.IntegerField(null=True, blank=True)
    #config_referral_image = models.ImageField(upload_to=lambda instance,filename:FileUtils.get_upload_file_path(instance,filename,FilePathConstant.TblConfigSetting.CONFIG_REFERAL_IMAGE),
    #                                          null=True, blank=True)
    config_referral_image = models.CharField(max_length=100, null=True)

    config_referral_referee_offer_status = models.CharField(max_length=10, null=True, blank=True)
    config_referral_referee_offer = models.CharField(max_length=20, null=True, blank=True)  # points/offer

    config_referral_referee_offer_id = models.CharField(max_length=10, null=True, blank=True)
    config_referral_referee_offer_text = models.CharField(max_length=500, null=True, blank=True)
    config_referral_referee_offer_validity = models.CharField(max_length=10, null=True, blank=True)

    config_referral_referee_bonus_points = models.CharField(max_length=10, null=True, blank=True)
    config_referral_referee_points_offer_id = models.CharField(max_length=10, null=True, blank=True)
    config_referral_referee_points_sms_id = models.CharField(max_length=10, null=True, blank=True)
    config_referral_referee_points_sms_text = models.TextField(max_length=500, null=True, blank=True)
    config_referral_referee_point_validity = models.CharField(max_length=10, null=True, blank=True)
    config_referral_referee_points_sms_status = models.CharField(max_length=20, null=True, blank=True)  # yes/no

    config_referral_referrer_offer_status = models.CharField(max_length=10, null=True, blank=True)
    config_referral_referrer_offer = models.CharField(max_length=20, null=True, blank=True)  # points/offer

    config_referral_referrer_offer_id = models.CharField(max_length=10, null=True, blank=True)
    config_referral_referrer_offer_text = models.CharField(max_length=500, null=True, blank=True)
    config_referral_referrer_offer_validity = models.CharField(max_length=10, null=True, blank=True)

    config_referral_referrer_bonus_points = models.CharField(max_length=10, null=True, blank=True)
    config_referral_referrer_points_offer_id = models.CharField(max_length=10, null=True, blank=True)
    config_referral_referrer_points_sms_id = models.CharField(max_length=10, null=True, blank=True)
    config_referral_referrer_points_sms_text = models.TextField(max_length=500, null=True, blank=True)
    config_referral_referrer_point_validity = models.CharField(max_length=10, null=True, blank=True)
    config_referral_referrer_points_sms_status = models.CharField(max_length=20, null=True, blank=True)  # yes/no
    # # ================END=================================

    reg_sms_text = models.TextField(max_length=500, null=True)

#    mobile_app_icon = models.ImageField(upload_to=lambda instance,filename:FileUtils.get_upload_file_path(instance,filename,FilePathConstant.TblConfigSetting.MOBILE_APP_ICON), null=True,
#                                        blank=True, storage=PublicImageStorage())
#    mobile_app_logo = models.ImageField(upload_to=lambda instance,filename:FileUtils.get_upload_file_path(instance,filename,FilePathConstant.TblConfigSetting.MOBILE_APP_LOGO), null=True,
#                                        blank=True, storage=PublicImageStorage())
#    mobile_app_card = models.ImageField(upload_to=lambda instance,filename:FileUtils.get_upload_file_path(instance,filename,FilePathConstant.TblConfigSetting.MOBILE_APP_CARD), null=True,
#                                        blank=True, storage=PublicImageStorage())
#    mobile_app_card_thumb = models.ImageField(upload_to=lambda instance,filename:FileUtils.get_upload_file_path(instance,filename,FilePathConstant.TblConfigSetting.MOBILE_APP_CARD_THUMB),
#                                              null=True, blank=True, storage=PublicImageStorage())
#    mobile_app_home1_img = models.ImageField(upload_to=lambda instance,filename:FileUtils.get_upload_file_path(instance,filename,FilePathConstant.TblConfigSetting.MOBILE_APP_HOME1_IMG), null=True,
#                                             blank=True, storage=PublicImageStorage())
#    mobile_app_home2_img = models.ImageField(upload_to=lambda instance,filename:FileUtils.get_upload_file_path(instance,filename,FilePathConstant.TblConfigSetting.MOBILE_APP_HOME2_IMG), null=True,
#                                             blank=True, storage=PublicImageStorage())
#    mobile_app_home3_img = models.ImageField(upload_to=lambda instance,filename:FileUtils.get_upload_file_path(instance,filename,FilePathConstant.TblConfigSetting.MOBILE_APP_HOME3_IMG), null=True,
#                                             blank=True, storage=PublicImageStorage())
#    mobile_app_splash1_img = models.ImageField(upload_to=lambda instance,filename:FileUtils.get_upload_file_path(instance,filename,FilePathConstant.TblConfigSetting.MOBILE_APP_SPLASH1_IMG),
#                                               null=True, blank=True, storage=PublicImageStorage())
#    mobile_app_splash2_img = models.ImageField(upload_to=lambda instance,filename:FileUtils.get_upload_file_path(instance,filename,FilePathConstant.TblConfigSetting.MOBILE_APP_SPLASH2_IMG),
#                                               null=True, blank=True, storage=PublicImageStorage())
#    mobile_app_splash3_img = models.ImageField(upload_to=lambda instance,filename:FileUtils.get_upload_file_path(instance,filename,FilePathConstant.TblConfigSetting.MOBILE_APP_SPLASH3_IMG),
#                                               null=True, blank=True, storage=PublicImageStorage())
    
    mobile_app_icon = models.TextField(max_length=150, null=True)
    mobile_app_logo = models.TextField(max_length=150, null=True)
    mobile_app_card = models.TextField(max_length=150, null=True)
    mobile_app_card_thumb = models.TextField(max_length=150, null=True)
    mobile_app_home1_img = models.TextField(max_length=150, null=True)
    mobile_app_home2_img = models.TextField(max_length=150, null=True)
    mobile_app_home3_img = models.TextField(max_length=150, null=True)
    mobile_app_splash1_img = models.TextField(max_length=150, null=True)
    mobile_app_splash2_img = models.TextField(max_length=150, null=True)
    mobile_app_splash3_img = models.TextField(max_length=150, null=True)
    
    created_on = models.DateTimeField(max_length=50, default=timezone.now)
    updated_on = models.DateTimeField(max_length=50, null=True)
    status_flag = models.IntegerField(null=True, default=1)
    mapp_apk_url = models.TextField(max_length=200, null=True)
    mapp_ios_url = models.TextField(max_length=200, null=True)
    mapp_others_url = models.TextField(max_length=200, null=True)
    
    sms_api_url2 = models.TextField(max_length=500, null=True)
    redeem_voucher_validity = models.CharField(max_length=50, null=True)
    brand_helpdesk_emailid = models.CharField(max_length=250, null=True)
    
    config_pushnotification_key = models.CharField(max_length=200, null=True)
    config_discount_type = models.CharField(max_length=200, null=True)
    # FOR BRAND LEVEL AUTH SETTINGS

    # sample json
    # {"whitelistedIPs":{'ip_addresses':['127.0.0.1'], 'subnets':[]}, "expiry":{'days':0, 'minutes':0}}

    def __int__(self):
        return self.id

    #def save(self, *args, **kwargs):
    #    self.mst_gif()
    #    super(TblSettings, self).save(*args, **kwargs)

class TblRequestAuditLogs(models.Model):
    id = models.AutoField(primary_key=True)
    mobileno = models.CharField(max_length=50, null=True)
    apiuserid = models.CharField(max_length=50, null=True)
    apipswd = models.CharField(max_length=256, null=True)
    api_flag = models.CharField(max_length=100, null=True)  #
    points = models.CharField(max_length=50, null=True)
    tier_minimum_value = models.IntegerField(null=True)
    tier_maximum_value = models.IntegerField(null=True)
    points_desc = models.TextField(max_length=500, null=True)
    title = models.CharField(max_length=50, null=True)
    homeno = models.CharField(max_length=50, null=True)
    firstname = models.CharField(max_length=50, null=True)
    lastname = models.CharField(max_length=50, null=True)
    email_id = models.CharField(max_length=50, null=True)
    gender = models.CharField(max_length=50, null=True)
    age = models.CharField(max_length=10, null=True)
    dobday = models.CharField(max_length=50, null=True)
    dobmonth = models.CharField(max_length=50, null=True)
    dobyear = models.CharField(max_length=50, null=True)
    doaday = models.CharField(max_length=50, null=True)
    doamonth = models.CharField(max_length=50, null=True)
    doayear = models.CharField(max_length=50, null=True)
    floor_flat = models.CharField(max_length=50, null=True)
    building = models.CharField(max_length=50, null=True)
    street = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    zone = models.CharField(max_length=50, null=True)
    town = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    occupation = models.CharField(max_length=50, null=True)
    bill_number = models.CharField(max_length=50, null=True)
    bill_amount = models.CharField(max_length=50, null=True)
    bill_date = models.DateTimeField(null=True)
    otp = models.CharField(max_length=250, null=True)
    period = models.CharField(max_length=50, null=True)
    location_code = models.CharField(max_length=50, null=True)
    location_class_name = models.CharField(max_length=50, null=True)
    location_category_name = models.CharField(max_length=50, null=True)
    resource_name = models.CharField(max_length=250, null=True)
    voucher_code = models.CharField(max_length=50, null=True)
    coupon_code = models.CharField(max_length=50, null=True)
    reference_bill_number = models.CharField(max_length=50, null=True)
    redeem_points = models.CharField(max_length=50, null=True)
    user_id = models.CharField(max_length=50, null=True)
    brand_id = models.IntegerField(null=True)
    user_password = models.CharField(max_length=50, null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    dob = models.CharField(max_length=200, null=True)
    doa = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    occassion = models.CharField(max_length=100, null=True)
    comments = models.CharField(max_length=100, null=True)
    highpriority = models.CharField(max_length=100, null=True)
    countrycode = models.CharField(max_length=100, null=True)
    pay_amount = models.TextField(max_length=500, null=True)
    login_location_id = models.CharField(max_length=50, null=True)
    login_user_id = models.CharField(max_length=50, null=True)
    response_flag = models.CharField(max_length=250, null=True)
    page_source = models.CharField(max_length=100, null=True)
    static_unique_status = models.TextField(max_length=500, null=True)
    static_unique_redemption_count = models.CharField(max_length=50, null=True)
    item_code = models.TextField(max_length=500, null=True)
    category_code = models.TextField(max_length=500, null=True)
    offer_value = models.TextField(max_length=500, null=True)
    offer_value_type = models.TextField(max_length=500, null=True)
    transaction_id = models.TextField(max_length=500, null=True)
    customer_code = models.TextField(max_length=500, null=True)
    customer_area = models.TextField(max_length=500, null=True)
    customer_state = models.CharField(max_length=100, null=True)
    customer_address = models.TextField(max_length=500, null=True)
    reverse_points = models.TextField(max_length=500, null=True)
    reg_source = models.CharField(max_length=100, null=True)
    location_id = models.CharField(max_length=200, null=True)
    type = models.CharField(max_length=200, null=True)
    bal_cash_val = models.TextField(max_length=500, null=True)
    location_name = models.CharField(max_length=100, null=True)
    location_mgr = models.CharField(max_length=100, null=True)
    location_qrcode = models.CharField(max_length=100, null=True)
    mall_brand_id = models.CharField(max_length=200, null=True)
    tier_name = models.CharField(max_length=200, null=True)
    tier_type = models.CharField(max_length=200, null=True)
    tier_logic_type = models.CharField(max_length=200, null=True)
    tier_earn_points = models.FloatField(null=True)
    tier_pts_per_rs = models.FloatField(null=True)
    tier_id = models.CharField(max_length=20, null=True)
    rwrd_brand_name = models.CharField(max_length=200, null=True)
    source_ip = models.CharField(max_length=50, null=True)
        
    def __str__(self):
        return self.api_flag


class TblResponseAuditLogs(models.Model):
    id = models.AutoField(primary_key=True)
    mobileno = models.CharField(max_length=50, null=True)
    apiuserid = models.CharField(max_length=50, null=True)
    apipswd = models.CharField(max_length=256, null=True)
    api_flag = models.CharField(max_length=100, null=True)  #
    points = models.CharField(max_length=50, null=True)
    tier_minimum_value = models.IntegerField(null=True)
    tier_maximum_value = models.IntegerField(null=True)
    points_desc = models.TextField(max_length=500, null=True)
    title = models.CharField(max_length=50, null=True)
    homeno = models.CharField(max_length=50, null=True)
    firstname = models.CharField(max_length=50, null=True)
    lastname = models.CharField(max_length=50, null=True)
    email_id = models.CharField(max_length=50, null=True)
    gender = models.CharField(max_length=50, null=True)
    age = models.CharField(max_length=10, null=True)
    dobday = models.CharField(max_length=50, null=True)
    dobmonth = models.CharField(max_length=50, null=True)
    dobyear = models.CharField(max_length=50, null=True)
    doaday = models.CharField(max_length=50, null=True)
    doamonth = models.CharField(max_length=50, null=True)
    doayear = models.CharField(max_length=50, null=True)
    floor_flat = models.CharField(max_length=50, null=True)
    building = models.CharField(max_length=50, null=True)
    street = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    zone = models.CharField(max_length=50, null=True)
    town = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    occupation = models.CharField(max_length=50, null=True)
    bill_number = models.CharField(max_length=50, null=True)
    bill_amount = models.CharField(max_length=50, null=True)
    bill_date = models.DateTimeField(null=True)
    otp = models.CharField(max_length=250, null=True)
    period = models.CharField(max_length=50, null=True)
    location_code = models.CharField(max_length=50, null=True)
    location_class_name = models.CharField(max_length=50, null=True)
    location_category_name = models.CharField(max_length=50, null=True)
    resource_name = models.CharField(max_length=50, null=True)
    voucher_code = models.CharField(max_length=50, null=True)
    coupon_code = models.CharField(max_length=50, null=True)
    reference_bill_number = models.CharField(max_length=50, null=True)
    redeem_points = models.CharField(max_length=50, null=True)
    user_id = models.CharField(max_length=50, null=True)
    brand_id = models.IntegerField(null=True)
    user_password = models.CharField(max_length=50, null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    dob = models.CharField(max_length=200, null=True)
    doa = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    occassion = models.CharField(max_length=100, null=True)
    comments = models.CharField(max_length=100, null=True)
    highpriority = models.CharField(max_length=100, null=True)
    countrycode = models.CharField(max_length=100, null=True)
    pay_amount = models.TextField(max_length=500, null=True)
    login_location_id = models.CharField(max_length=50, null=True)
    login_user_id = models.CharField(max_length=50, null=True)
    response_flag = models.CharField(max_length=250, null=True)
    page_source = models.CharField(max_length=100, null=True)
    static_unique_status = models.TextField(max_length=500, null=True)
    static_unique_redemption_count = models.CharField(max_length=50, null=True)
    item_code = models.TextField(max_length=500, null=True)
    category_code = models.TextField(max_length=500, null=True)
    offer_value = models.TextField(max_length=500, null=True)
    offer_value_type = models.TextField(max_length=500, null=True)
    transaction_id = models.TextField(max_length=500, null=True)
    customer_code = models.TextField(max_length=500, null=True)
    customer_area = models.TextField(max_length=500, null=True)
    customer_state = models.CharField(max_length=100, null=True)
    customer_address = models.TextField(max_length=500, null=True)
    reverse_points = models.TextField(max_length=500, null=True)
    reg_source = models.CharField(max_length=100, null=True)
    location_id = models.CharField(max_length=200, null=True)
    mall_brand_id = models.CharField(max_length=200, null=True)
    type = models.CharField(max_length=200, null=True)
    bal_cash_val = models.TextField(max_length=500, null=True)
    location_name = models.CharField(max_length=100, null=True)
    location_mgr = models.CharField(max_length=100, null=True)
    location_qrcode = models.CharField(max_length=100, null=True)
    tier_name = models.CharField(max_length=200, null=True)
    tier_type = models.CharField(max_length=200, null=True)
    tier_logic_type = models.CharField(max_length=200, null=True)
    tier_earn_points = models.FloatField(null=True)
    tier_pts_per_rs = models.FloatField(null=True)
    tier_id = models.CharField(max_length=20, null=True)
    rwrd_brand_name = models.CharField(max_length=200, null=True)
    response_flag = models.TextField(max_length=500, null=True)

    def __str__(self):
        return self.api_flag


class MissedcallRequests(models.Model):
    id = models.AutoField
    mobileno = models.BigIntegerField()
    circle = models.CharField(max_length=100, null=True)
    location = models.CharField(max_length=100, null=True)
    received_date = models.DateField(null=True)
    received_time = models.TimeField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    brand_id = models.IntegerField(null=True)

    def __int__(self):
        return self.id
    

class LoyaltyTrans(models.Model):
    BILL_TRANS_TYPE = [
        ('Earn', 'Earn'),
        ('Burn', 'Burn'),
        ('Reverse', 'Reverse')
    ]

    class Meta:
        unique_together = (('mobileno', 'bill_number', 'bill_date', 'location_id', 'bill_status'),)

    id = models.BigAutoField(primary_key=True)
    brand_id = models.IntegerField(null=True)
    mobileno = models.BigIntegerField()
    bill_amount = models.FloatField(null=True)
    bill_amount_wo_tax = models.FloatField(null=True)
    points = models.CharField(max_length=50, null=True)
    bill_number = models.CharField(max_length=50)
    bill_discount = models.FloatField(null=True)
    bill_date = models.DateTimeField(null=True)
    bill_month = models.IntegerField(null=True)
    bill_year = models.IntegerField(null=True)
    user_id = models.IntegerField(null=True)
    location_id = models.ForeignKey(LocationMst, on_delete=models.CASCADE, blank=True, null=True, db_column='location_id')
    rwrd_brand_id = models.ForeignKey(RewardBrandsMst, on_delete=models.CASCADE, blank=True, null=True, db_column='rwrd_brand_id')
    remarks = models.CharField(max_length=100, null=True)
    advance_amt = models.CharField(max_length=50, null=True)
    adjustbill_no = models.CharField(max_length=50, null=True)
    bill_type = models.CharField(max_length=50, null=True)
    billamt_for_pts_issue = models.FloatField(null=True)
    payment_mode = models.CharField(max_length=50, null=True)
    bill_status = models.CharField(max_length=50, default="New")
    bill_tax = models.FloatField(null=True)
    customer_id = models.CharField(max_length=50, null=True)
    redemption_against_code = models.CharField(max_length=50, null=True)
    trans_type = models.CharField(max_length=50, null=True)
    bill_trans_type = models.CharField(max_length=50, null=True, choices=BILL_TRANS_TYPE)
    bill_data_type = models.CharField(max_length=50, default="New")
    bal_points_bef_trans = models.CharField(max_length=50, null=True)
    bal_points_aft_trans = models.CharField(max_length=50, null=True)
    bonus_points = models.FloatField(null=True)
    tier_id = models.IntegerField(null=True)
    tier_percent = models.FloatField(null=True)
    tier_earn_pts = models.FloatField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    trans_source = models.CharField(max_length=30, null=True)
    data_source = models.IntegerField(default=0)
    status_flag = models.IntegerField(default=1)
    transaction_id = models.CharField(max_length=200, null=True)
    points_expired_on = models.DateTimeField(null=True)
    bill_processed_flag = models.IntegerField(null=True)
    redemption_flag = models.TextField(max_length=50, null=True)
    upload_file_name = models.CharField(max_length=100, null=True)
    upload_on = models.DateTimeField(default=timezone.now)
    upload_trans_id = models.CharField(max_length=50, null=True, blank=True)
    updated_on = models.DateTimeField(default=timezone.now)
    qty = models.IntegerField(null=True)
    voucher_value = models.IntegerField(null=True)
    #point_type = models.CharField(max_length=100, default=Constants.PointTypes.DEFAULT.value)
    metadata_json = models.JSONField(null=True)


    def __int__(self):
        return self.mobileno


class TierUpgradedata(models.Model):
    id = models.AutoField(primary_key=True)
    mobileno = models.BigIntegerField()
    prev_tierid = models.IntegerField()
    new_tierid = models.IntegerField()
    bill_date = models.DateTimeField()
    location_id = models.IntegerField()
    brand_id = models.IntegerField(null=True)
    bill_number = models.CharField(max_length=50)
    bill_amount = models.FloatField()
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    upgrade_points = models.FloatField(null=True)

    def __int__(self):
        return self.mobileno


class TblRegActivitySMSLogs(models.Model):
    id = models.AutoField(primary_key=True)
    mobileno = models.BigIntegerField(null=True)
    loyalty_id = models.CharField(max_length=50, null=True)
    sms_text = models.TextField(max_length=650, null=True)
    sms_response_status = models.CharField(max_length=100, null=True)
    sms_response = models.CharField(max_length=250, null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    sms_response_text = models.TextField(max_length=1000, null=True)
    sms_for = models.CharField(max_length=50, null=True)
    sms_length = models.CharField(max_length=50, null=True)
    user_id = models.IntegerField(null=True)
    location_id = models.IntegerField(null=True)
    bill_number = models.CharField(max_length=50, null=True)
    bill_amount = models.FloatField(null=True)
    bill_date = models.DateTimeField(null=True)
    brand_id = models.IntegerField(null=True)
    bill_status = models.CharField(max_length=50, null=True)

    def check_len(self):
        if len(self.sms_text) > 0 and len(self.sms_text) <= 160:
            return "1"
        elif len(self.sms_text) > 160:
            sm_len = len(self.sms_text) / 153
            sm_len = math.ceil(sm_len)
            return str(sm_len)
        elif len(self.sms_text) < 1:
            return "0"

    def __int__(self):
        return self.id

    def save(self, *args, **kwargs):
        print("save", self.check_len())
        self.sms_length = self.check_len()
        super().save(*args, **kwargs)


class TblTransActivitySMSLogs(models.Model):
    id = models.AutoField(primary_key=True)
    mobileno = models.BigIntegerField(null=True)
    sms_for = models.CharField(max_length=50, null=True)
    sms_text = models.TextField(max_length=650, null=True)
    sms_response_status = models.CharField(max_length=50, null=True)
    sms_response = models.CharField(max_length=250, null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    sms_response_text = models.TextField(max_length=1000, null=True)
    sms_length = models.CharField(max_length=50, null=True)
    user_id = models.IntegerField(null=True)
    location_id = models.IntegerField(null=True)
    brand_id = models.IntegerField(null=True)
    bill_number = models.CharField(max_length=50, null=True)
    bill_amount = models.CharField(max_length=50, null=True)
    bill_date = models.DateTimeField(null=True)
    bill_status = models.CharField(max_length=50, null=True)

    def check_len(self):
        if len(self.sms_text) > 0 and len(self.sms_text) <= 160:
            return "1"
        elif len(self.sms_text) > 160:
            sm_len = len(self.sms_text) / 153
            sm_len = math.ceil(sm_len)
            return str(sm_len)
        elif len(self.sms_text) < 1:
            return "0"

    def __str__(self):
        return "Mobileno-" + str(self.mobileno)

    def save(self, *args, **kwargs):
        print("save", self.check_len())
        self.sms_length = self.check_len()
        super().save(*args, **kwargs)

def random_generator():
    num = 11
    res = ''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(num))
    return res

class RewardGiftvouchers(models.Model):
    id = models.AutoField(primary_key=True)
    transaction_id = models.CharField(max_length=100, null=True)
    sys_gv_code = models.CharField(max_length=50, default=random_generator,unique=True) 
    brand_gv_code = models.CharField(max_length=50, null=True)
    gv_value = models.FloatField(null=True)
    gv_points_value = models.FloatField(null=True)
    brand_id = models.IntegerField(null=True)
    rwrd_brand_id = models.ForeignKey(RewardBrandsMst, on_delete=models.CASCADE, blank=True, null=True, db_column='rwrd_brand_id')
    received_on = models.DateTimeField(null=True)
    gv_issued_on = models.DateTimeField(null=True)
    gv_issued_to = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=200, null=True)
    mobileno = models.BigIntegerField(null=True)
    gv_expiry = models.DateTimeField(null=True)
    user_id = models.IntegerField()
    updated_on = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    gv_type = models.CharField(max_length=50, null=True)
    gv_mode = models.CharField(max_length=50, null=True)
    issue_flag = models.IntegerField(null=True)
    activation_date = models.DateTimeField(null=True)
    gv_assigned_on = models.DateTimeField(null=True)
    gv_assigned_by = models.IntegerField(null=True)
    gv_issued_by = models.IntegerField(null=True)
    gv_description = models.TextField(max_length=300, null=True)
    location_id = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    gv_status_flag = models.IntegerField(default=1)
    gv_identifier = models.CharField(max_length=50, null=True)
    gv_file_name = models.TextField(max_length=250, null=True)

    def mst_gif(self):
        # try:

        if not RewardGiftvouchersMst.objects.filter(rwrd_brand_id=self.rwrd_brand_id_id,gv_value=self.gv_value,status_flag=1, brand_id=self.brand_id).exists():
            category_id = RewardBrandsMst.objects.filter(id=self.rwrd_brand_id_id, brand_id=self.brand_id,status_flag=1).values("category_id_id")
            if not category_id:
                logger.error(f'category_id-{self.rwrd_brand_id_id} does not exist for brand_id-{self.brand_id}')
                raise Exception("Invalid Reward_brand_id.")
            RewardGiftvouchersMst.objects.create(
                brand_id=self.brand_id,
                rwrd_brand_id=self.rwrd_brand_id,
                gv_value=self.gv_value,
                gv_points_value=self.gv_points_value,
                gv_expiry=self.gv_expiry,
                gv_type=self.gv_type,
                gv_mode=self.gv_mode,
                category_id=category_id[0]['category_id_id'],
                user_id=self.user_id
            )

    def __int__(self):
        return self.id

    def save(self, *args, **kwargs):
        self.mst_gif()
        super(RewardGiftvouchers, self).save(*args, **kwargs)


class RewardGiftvouchersMst(models.Model):
    id = models.AutoField(primary_key=True)
    brand_id = models.IntegerField(null=True)
    rwrd_brand_id = models.ForeignKey(RewardBrandsMst, on_delete=models.CASCADE, blank=True, null=True, db_column='rwrd_brand_id')
    tot_gvs = models.IntegerField(null=True)
    tot_gv_issued = models.IntegerField(null=True)
    tot_gv_redeemed = models.IntegerField(null=True)
    tot_gv_balance = models.IntegerField(null=True)
    gv_value = models.FloatField(null=True)
    gv_points_value = models.FloatField(null=True)
    #gv_image = models.ImageField(upload_to= lambda instance, filename:FileUtils.get_upload_file_path(instance,filename,FilePathConstant.MstGiftVouchersRewards.GIFT_VOUCHER_IMAGE), null=True)
    gv_image = models.CharField(max_length=100, null=True)
    gv_expiry = models.DateTimeField(null=True)
    category_id = models.IntegerField(null=True)  # brand_category
    gv_frequency_type = models.CharField(max_length=100, null=True)
    gv_title = models.TextField(max_length=100, null=True)
    gv_description = models.TextField(max_length=500, null=True)
    gv_frequency_duration = models.IntegerField(null=True)
    gv_tnc = models.TextField(max_length=5000, null=True)
    gv_url = models.TextField(max_length=1000, null=True)
    gv_type = models.CharField(max_length=20, null=True)
    gv_mode = models.CharField(max_length=20, null=True)
    gv_special_sdate = models.DateTimeField(null=True)
    gv_special_edate = models.DateTimeField(null=True)
    gv_code_display = models.CharField(max_length=200, null=True)
    gv_redemption_steps = models.TextField(max_length=5000, null=True, blank=True)
    gv_identifier = models.CharField(max_length=50, null=True)
    gv_deal_image_url = models.CharField(max_length=500, null=True)
    support_remarks = models.TextField(max_length=1000, null=True)
    user_id = models.IntegerField(null=True)
    updated_on = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    def __int__(self):
        return self.id


class AssignedGiftVouchers(models.Model):
    id = models.AutoField(primary_key=True)
    brand_id = models.IntegerField(null=True)
    category_id = models.ForeignKey(CategoryMst, on_delete=models.CASCADE, blank=True, null=True, db_column='category_id')
    rwrd_brand_id = models.ForeignKey(RewardBrandsMst, on_delete=models.CASCADE, blank=True, null=True, db_column='rwrd_brand_id')
    gv_points_value = models.FloatField(null=True)
    tot_gvs = models.IntegerField(null=True)
    tot_gvs_value = models.FloatField(null=True)
    support_remarks = models.TextField(max_length=1000, null=True)
    user_id = models.IntegerField(null=True)
    updated_on = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    
    def __int__(self):
        return self.id


class PendingBills(models.Model):
    id = models.AutoField(primary_key=True)
    brand_id = models.IntegerField(null=True)
    rwrd_brand_id = models.ForeignKey(RewardBrandsMst, on_delete=models.CASCADE, blank=True, null=True, db_column='rwrd_brand_id')
    mobileno = mobileno = models.BigIntegerField()
    #upload_file_name = models.CharField(max_length=100, null=True)
    upload_file_name = models.FileField(upload_to='billscans/')
    bill_amount = models.FloatField(null=True)
    bill_number = models.CharField(max_length=50)
    bill_date = models.DateTimeField(null=True)
    location_id = models.ForeignKey(LocationMst, on_delete=models.CASCADE, blank=True, null=True, db_column='location_id')
    support_remarks = models.TextField(max_length=1000, null=True)
    user_id = models.IntegerField(null=True)
    updated_on = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    
    def __int__(self):
        return self.id


class OtpVerficationDetails(models.Model):
    class Flag(models.IntegerChoices):
        registration = 1
        redeem = 2
                
    class StatusFlag(models.IntegerChoices):  
        deactive = 0
        Active = 1
        redeemed = 2
        Expired = 3
        Cancel = 4

    id = models.AutoField(primary_key=True)
    brand_id = models.IntegerField(null=True)
    mobileno = models.BigIntegerField(null=True)
    code = models.CharField(max_length=250, null=True)
    points = models.CharField(max_length=50, null=True)
    flag = models.IntegerField(choices=Flag.choices)
    secureotp = models.CharField(max_length=256, null=True)
    source = models.CharField(max_length=50, null=True)
    otp_expired_on = models.DateTimeField(null=True)
    location_id = models.CharField(max_length=50, null=True)
    support_remarks = models.TextField(max_length=500, null=True)
    user_id = models.CharField(max_length=50, null=True)
    updated_on = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=0, choices=StatusFlag.choices)
    
    def __int__(self):
        return self.id


class CustomerLoginOtpVerification(models.Model):
    class Meta:
        unique_together = (('mobileno', 'brand_id', 'source'))

    id = models.AutoField(primary_key=True)
    brand_id = models.IntegerField(null=True)
    mobileno = models.BigIntegerField(null=True)
    secureotp = models.CharField(max_length=256)
    source = models.CharField(max_length=50, null=True)
    flag = models.CharField(max_length=100, null=True)
    device_id = models.TextField(max_length=500, null=True)
    device_type = models.CharField(max_length=250, null=True)
    user_id = models.IntegerField(null=True)
    user_type = models.CharField(max_length=50, null=True)
    otp_expired_on = models.DateTimeField(null=True)
    support_remarks = models.TextField(max_length=500, null=True)
    updated_on = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    
    def __int__(self):
        return self.id
    

class TemplateFlagsMst(models.Model):
    id = models.AutoField(primary_key=True)
    template_type = models.CharField(max_length=30, null=True)
    template_category = models.CharField(max_length=100, null=True)
    template_category_desc = models.TextField(max_length=300, null=True)
    template_flag = models.CharField(max_length=50, null=True)
    template_flag_description = models.TextField(max_length=250, null=True)
    user_id = models.IntegerField(null=True)
    brand_id = models.IntegerField(null=True)
    updated_on = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)

    def __int__(self):
        return self.id
    
class Templates(models.Model):
    id = models.AutoField(primary_key=True)
    template_name = models.CharField(max_length=50, null=True)
    template_id = models.CharField(max_length=100, null=True)
    template_text = models.TextField(max_length=750, null=True)
    template_flag = models.CharField(max_length=50, null=True)
    #template_category = models.CharField(max_length=100, null=True)
    #template_type = models.CharField(max_length=30, null=True)
    template_flag_id = models.ForeignKey(TemplateFlagsMst, on_delete=models.CASCADE, blank=True, null=True, db_column='template_flag_id')
    user_id = models.IntegerField(null=True)
    brand_id = models.IntegerField(null=True)
    updated_on = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)

    def __int__(self):
        return self.id



class BillingTrans(models.Model):
    row_id = models.AutoField(primary_key=True)
    brand_id = models.IntegerField(null=True)
    location_code = models.CharField(max_length=250, null=True)
    location_name = models.TextField(max_length=500, null=True)
    bill_number = models.CharField(max_length=250)
    bill_transcation_no = models.TextField(max_length=500, null=True)
    bill_date = models.DateTimeField(null=True)
    bill_time = models.TextField(max_length=500, null=True)
    bill_type = models.TextField(max_length=500, null=True)
    bill_status = models.CharField(max_length=250, null=True)
    bill_tender_type = models.TextField(max_length=500, null=True)
    bill_amt_without_tax = models.TextField(max_length=500, null=True)
    bill_amt_with_tax = models.TextField(max_length=500, null=True)
    bill_tender_type_amt = models.TextField(max_length=500, null=True)
    bill_round_off_amt = models.TextField(max_length=500, null=True)
    bill_discount_per = models.TextField(max_length=500, null=True)
    bill_discount = models.TextField(max_length=500, null=True)
    bill_tax = models.TextField(max_length=500, null=True)
    bill_service_charge = models.TextField(max_length=500, null=True)
    bill_cancel_date = models.TextField(max_length=500, null=True)
    bill_cancel_time = models.TextField(max_length=500, null=True)
    bill_cancel_reason = models.TextField(max_length=500, null=True)
    bill_cancel_amount = models.TextField(max_length=500, null=True)
    bill_cancel_against = models.TextField(max_length=500, null=True)
    bill_modify = models.TextField(max_length=500, null=True)
    bill_modify_reason = models.TextField(max_length=500, null=True)
    bill_modify_datetime = models.TextField(max_length=500, null=True)
    adjustbill_no = models.CharField(max_length=50, null=True)
    bill_remarks = models.TextField(max_length=500, null=True)
    bill_remarks1 = models.TextField(max_length=500, null=True)
    bill_remarks2 = models.TextField(max_length=500, null=True)
    bill_remarks3 = models.TextField(max_length=500, null=True)
    bill_remarks4 = models.TextField(max_length=500, null=True)
    bill_remarks5 = models.TextField(max_length=500, null=True)
    sku_serial_no = models.TextField(max_length=500, null=True)
    sku_code = models.TextField(max_length=500, null=True)
    sku_name1 = models.TextField(max_length=500, null=True)
    sku_name2 = models.TextField(max_length=500, null=True)
    sku_name3 = models.TextField(max_length=500, null=True)
    sku_category_code = models.TextField(max_length=500, null=True)
    sku_sub_category_code = models.TextField(max_length=500, null=True)
    sku_group_code = models.TextField(max_length=500, null=True)
    sku_brand_code = models.TextField(max_length=500, null=True)
    sku_department_code = models.TextField(max_length=500, null=True)
    sku_quantity = models.TextField(max_length=500, null=True)
    sku_amt_without_tax = models.TextField(max_length=500, null=True)
    sku_amt_with_tax = models.TextField(max_length=500, null=True)
    sku_round_off_amt = models.TextField(max_length=500, null=True)
    sku_rate = models.TextField(max_length=500, null=True)
    sku_discount = models.TextField(max_length=500, null=True)
    sku_discount_per = models.TextField(max_length=500, null=True)
    sku_tax = models.TextField(max_length=500, null=True)
    sku_color_code = models.TextField(max_length=500, null=True)
    sku_barcode = models.TextField(max_length=500, null=True)
    sku_size_code = models.TextField(max_length=500, null=True)
    sku_status = models.TextField(max_length=500, null=True)
    sku_remarks1 = models.TextField(max_length=500, null=True)
    sku_remarks2 = models.TextField(max_length=500, null=True)
    sku_remarks3 = models.TextField(max_length=500, null=True)
    sku_remarks4 = models.TextField(max_length=500, null=True)
    sku_remarks5 = models.TextField(max_length=500, null=True)
    customer_code = models.TextField(max_length=500, null=True)
    customer_fname = models.TextField(max_length=500, null=True)
    customer_mname = models.TextField(max_length=500, null=True)
    customer_lname = models.TextField(max_length=500, null=True)
    customer_gender = models.TextField(max_length=500, null=True)
    mobileno = models.BigIntegerField(null=True)
    customer_phone = models.TextField(max_length=500, null=True)
    customer_phone2 = models.TextField(max_length=500, null=True)
    customer_email = models.TextField(max_length=500, null=True)
    customer_dob = models.TextField(max_length=500, null=True)
    customer_doa = models.TextField(max_length=500, null=True)
    customer_city = models.TextField(max_length=500, null=True)
    customer_area = models.TextField(max_length=500, null=True)
    customer_address = models.TextField(max_length=500, null=True)
    customer_address2 = models.TextField(max_length=500, null=True)
    customer_address3 = models.TextField(max_length=500, null=True)
    customer_pin = models.TextField(max_length=500, null=True)
    customer_state = models.TextField(max_length=500, null=True)
    customer_profession = models.TextField(max_length=500, null=True)
    spousename = models.TextField(max_length=500, null=True)
    customer_country = models.TextField(max_length=500, null=True)
    customer_remarks1 = models.TextField(max_length=500, null=True)
    customer_remarks2 = models.TextField(max_length=500, null=True)
    customer_remarks3 = models.TextField(max_length=500, null=True)
    customer_remarks4 = models.TextField(max_length=500, null=True)
    customer_remarks5 = models.TextField(max_length=500, null=True)
    coupon_code = models.TextField(max_length=500, null=True)
    coupon_value = models.TextField(max_length=500, null=True)
    coupon_type = models.TextField(max_length=500, null=True)
    coupon_remarks1 = models.TextField(max_length=500, null=True)
    coupon_remarks2 = models.TextField(max_length=500, null=True)
    ext_param1 = models.TextField(max_length=500, null=True)
    ext_param2 = models.TextField(max_length=500, null=True)
    ext_param3 = models.TextField(max_length=500, null=True)
    ext_param4 = models.TextField(max_length=500, null=True)
    ext_param5 = models.TextField(max_length=500, null=True)
    guest_count = models.TextField(max_length=500, null=True)
    customer_type = models.TextField(max_length=500, null=True)
    unique_no = models.TextField(max_length=500, null=True)
    discount_remark = models.TextField(max_length=500, null=True)
    cashiername = models.TextField(max_length=500, null=True)
    idiscountbasis = models.TextField(max_length=500, null=True)
    igstrate = models.TextField(max_length=500, null=True)
    igstamt = models.TextField(max_length=500, null=True)
    cgstrate = models.TextField(max_length=500, null=True)
    cgstamt = models.TextField(max_length=500, null=True)
    sgstrate = models.TextField(max_length=500, null=True)
    sgstamt = models.TextField(max_length=500, null=True)
    cessrate = models.TextField(max_length=500, null=True)
    cessamt = models.TextField(max_length=500, null=True)
    item_remarks = models.TextField(max_length=500, null=True)
    cnrtype = models.TextField(max_length=500, null=True)
    addeddate = models.TextField(max_length=500, null=True)
    twitterid = models.TextField(max_length=500, null=True)
    cloudregistrationid = models.TextField(max_length=500, null=True)
    uniqueidentifier = models.TextField(max_length=500, null=True)
    org_customer_mobile = models.TextField(max_length=500, null=True)
    customer_dob_original = models.TextField(max_length=500, null=True)
    possessionid = models.TextField(max_length=500, null=True)
    terminalid = models.TextField(max_length=500, null=True)
    stockpointid = models.TextField(max_length=500, null=True)
    chargeamt = models.TextField(max_length=500, null=True)
    roundoff = models.TextField(max_length=500, null=True)
    netpayable = models.TextField(max_length=500, null=True)
    promocode = models.TextField(max_length=500, null=True)
    promono = models.TextField(max_length=500, null=True)
    promoname = models.TextField(max_length=500, null=True)
    promostartdate = models.TextField(max_length=500, null=True)
    promoenddate = models.TextField(max_length=500, null=True)
    promostarttime = models.TextField(max_length=500, null=True)
    promoendtime = models.TextField(max_length=500, null=True)
    promoadvtmedia = models.TextField(max_length=500, null=True)
    returnamt = models.TextField(max_length=500, null=True)
    saleamt = models.TextField(max_length=500, null=True)
    idiscountamt = models.TextField(max_length=500, null=True)
    mdiscountamt = models.TextField(max_length=500, null=True)
    sku_promocode = models.TextField(max_length=500, null=True)
    sku_promono = models.TextField(max_length=500, null=True)
    sku_promoname = models.TextField(max_length=500, null=True)
    sku_promostartdate = models.TextField(max_length=500, null=True)
    sku_promoenddate = models.TextField(max_length=500, null=True)
    sku_promobenefit = models.TextField(max_length=500, null=True)
    articleid = models.TextField(max_length=500, null=True)
    cat2 = models.TextField(max_length=500, null=True)
    cat3 = models.TextField(max_length=500, null=True)
    cat4 = models.TextField(max_length=500, null=True)
    cat5 = models.TextField(max_length=500, null=True)
    cat6 = models.TextField(max_length=500, null=True)
    cat7 = models.TextField(max_length=500, null=True)
    cat8 = models.TextField(max_length=500, null=True)
    article_name = models.TextField(max_length=500, null=True)
    mdiscountid = models.TextField(max_length=500, null=True)
    mdiscountdesc = models.TextField(max_length=500, null=True)
    mrpamt = models.TextField(max_length=500, null=True)
    basicamt = models.TextField(max_length=500, null=True)
    promoamt = models.TextField(max_length=500, null=True)
    mrp = models.TextField(max_length=500, null=True)
    rsp = models.TextField(max_length=500, null=True)
    esp = models.TextField(max_length=500, null=True)
    bill_tender_type_tender = models.TextField(max_length=500, null=True)
    bill_tender_type_balance = models.TextField(max_length=500, null=True)
    bill_tender_type_base_amount = models.TextField(max_length=500, null=True)
    cnr_tender = models.TextField(max_length=500, null=True)
    cnr_balance = models.TextField(max_length=500, null=True)
    cnr_base = models.TextField(max_length=500, null=True)
    cust_extract_flag = models.IntegerField(default=1)
    Trans_extract_flag = models.IntegerField(default=1)
    created_on = models.DateTimeField(default=timezone.now)
    status_flag = models.IntegerField(default=1)
    
    def __int__(self):
        return self.row_id
