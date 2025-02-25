"""
URL configuration for tagnpay project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from tagnpayloyalty.views import *
from RFAPIS.views import *
from MAppApis.views import *
from django.conf import settings
from django.conf.urls.static import static
from analytics.views import *

urlpatterns = [
    path("tagnpayloyaltyadmin/", admin.site.urls),
    path("", View_platformlogin.as_view(), name="login"),
    # path('Reg/', View_UserRegistration.as_view())
    # path('Reg/<lcid>/<int:brid>/', View_UserRegistration.as_view()),
    path(
        "CustRegistration/",
        CustRegistrationPlatformView.as_view(),
        name="CustRegistration",
    ),
    path("CustomerSearch/", CustomerDetailsView.as_view(), name="CustomerSearch"),
    path("home/", View_HomeDashboard.as_view(), name="home"),
    path("EnterBill/", EnterBillView.as_view(), name="EnterBill"),
    # path('IssueVoucher/', IssueVoucherView.as_view(),name="IssueVoucher"),
    path("RwrdBrandSearch/", RewardBrandSearchView.as_view(), name="RwrdBrandSearch"),
    path("RedeemCoupon/", RedeemCouponView.as_view(), name="RedeemCoupon"),
    path("RedeemPoints/", RedeemPointsView.as_view(), name="RedeemPoints"),
    # path('UploadBill/', upload_bill,name="UploadBill"),
    # path('SendSMS/', SendSMSView.as_view(),name="SendSMS"),
    # path('CreateEpapers/', createEpapersView.as_view(),name="CreateEpapers"),
    # path('movedata/', movedatatopg, name="movedata"),
    path("settings/programsetup/", AddProgramSetup.as_view(), name="ProgramSetup"),
    path("settings/logicconfig/", SettingsLogicConfig.as_view(), name="LogicConfig"),
    path("settings/logicconfig/addtier", AddTier.as_view(), name="AddTier"),
    path("settings/logicconfig/edittier", EditTier.as_view(), name="EditTier"),
    path("settings/logicconfig/deltier", DeleteTier.as_view(), name="DelTier"),
    path("settings/logicconfig/gettier", GetTierDetails.as_view(), name="GetTierData"),
    path(
        "settings/rwrdcategories/",
        SettingsRwrdCategoriesView.as_view(),
        name="RwrdCategories",
    ),
    path(
        "settings/rwrdcategories/getcatg",
        GetRwrdCategoryDetails.as_view(),
        name="GetRwrdCategory",
    ),
    path(
        "settings/rwrdcategories/delcatg",
        DeleteRwrdCategory.as_view(),
        name="DelRwrdCategory",
    ),
    path(
        "settings/rwrdcategories/editcatg",
        EditRwrdCategory.as_view(),
        name="EditRwrdCategory",
    ),
    path(
        "settings/rwrdcategories/importcatg",
        ImportRwrdCategory.as_view(),
        name="ImportRwrdCategory",
    ),
    path("settings/rwrdbrands/", SettingsRwrdBrandsView.as_view(), name="RwrdBrands"),
    path(
        "settings/rwrdbrands/getbrnd",
        GetRwrdBrandDetails.as_view(),
        name="GetRwrdBrand",
    ),
    path("settings/rwrdbrands/delbrnd", DeleteRwrdBrand.as_view(), name="DelRwrdBrand"),
    path("settings/rwrdbrands/editbrnd", EditRwrdBrand.as_view(), name="EditRwrdBrand"),
    path(
        "settings/rwrdbrands/importbrnd",
        ImportRwrdBrand.as_view(),
        name="ImportRwrdBrand",
    ),
    path("settings/rwrdgvs/", SettingsRwrdGVsView.as_view(), name="RwrdGVs"),
    path("settings/rwrdgvs/getgv", GetRwrdGVDetails.as_view(), name="GetRwrdGV"),
    path("settings/rwrdgvs/delgv", DeleteRwrdGV.as_view(), name="DelRwrdGV"),
    path("settings/rwrdgvs/editgv", EditRwrdGV.as_view(), name="EditRwrdGV"),
    path("settings/rwrdgvs/importgv", ImportRwrdGV.as_view(), name="ImportRwrdGV"),
    path(
        "settings/getbrandsbycat", GetBrandsByCategoryView, name="GetBrandsByCategory"
    ),
    path(
        "settings/getdenomination",
        GetBrandDenominationView,
        name="GetBrandDenomination",
    ),
    path("settings/getcustomerpts", GetCustomerBalPointsView, name="GetCustomerPts"),
    path(
        "settings/assigngv", AssignRwrdGVsToRewardsDesk.as_view(), name="AssignRwrdGVs"
    ),
    path(
        "settings/locations/", SettingsLocationMstView.as_view(), name="LocationMaster"
    ),
    path("settings/getlocation", GetLocationDetails.as_view(), name="GetLocation"),
    path("settings/delloc", DeleteLocation.as_view(), name="DelLocation"),
    path("settings/editlocmst", EditLocation.as_view(), name="EditLocationMst"),
    path(
        "settings/importlocmst", ImportLocationMst.as_view(), name="ImportLocationMst"
    ),
    path("settings/smsconfig/", SettingsSMSConfigureView.as_view(), name="SMSConfig"),
    path(
        "settings/gettemplatecatbytype",
        GetTemplateCategoryByTypeView,
        name="GetTemplateCategoryByType",
    ),
    path(
        "settings/gettemplateflagbycat",
        GetTemplateFlagByTypeCatView,
        name="GetTemplateFlagByTypeCat",
    ),
    path("settings/addtemplate", AddTemplateView.as_view(), name="AddTemplate"),
    path("settings/deltemplate", DeleteTemplate.as_view(), name="DelTemplate"),
    path(
        "settings/gettemplatedtls",
        GetTemplateDetailsView.as_view(),
        name="GetTemplateDtls",
    ),
    path("settings/edittemplate", EditTemplate.as_view(), name="EditTemplate"),
    path("api/", include("RFAPIS.urls", namespace="RFAPIS")),
    path("mappapi/", include("MAppApis.urls", namespace="MAppApis")),
    path("analytics/", include("analytics.urls", namespace="analytics")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
