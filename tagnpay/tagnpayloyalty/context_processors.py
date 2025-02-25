from utils.globaldata_utils import global_brand_data,get_global_data_for_brand

def global_filtered_data(request):
    sessionbrand_id = request.session.get("brand_id")
    #print(sessionbrand_id)
    #print(global_brand_data(sessionbrand_id))
    return {'global_filtered_data': global_brand_data(sessionbrand_id)}