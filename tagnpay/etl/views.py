from tagnpayloyalty.models import LoyaltyCustomers
from pymongo import MongoClient

def extract_data():
    # Query MySQL for the required data
    customer_data = LoyaltyCustomers.objects.select_related('location_id','city','state').values('id', 'mobileno', 'brand_id', 'user_id', 'homeno','title','firstname','lastname','gender','dob','doa','age','email','address1','address2','town','district','zipcode','occupation','member_type','created_on','status_flag','user_identifier','city','state','country','location_id','landmark','location_id__location_Name','city__city_name','state__states_name')
    return list(customer_data)

def transform_data(data):
    transformed_dta = []
    for record in data:
        # Example: Format `updated_at` for MongoDB and remove unnecessary fields
        transformed_dta.append({
            "_id": record['id'],  # Use MySQL ID as MongoDB's `_id` for deduplication
            "mobileno": record['mobileno'],
            "brand_id": record['brand_id'],
            "user_id": record['user_id'],
            "homeno": record['homeno'],
            "title": record['title'],
            "firstname": record['firstname'],
            "lastname": record['lastname'],
            "gender": record['gender'],
            "dob": record['dob'].isoformat(),
            "doa": record['doa'].isoformat(),
            "age": record['age'],
            "email": record['email'],
            "address1": record['address1'],
            "address2": record['address2'],
            "town": record['town'],
            "district": record['district'],
            "zipcode": record['zipcode'],
            "occupation": record['occupation'],
            "member_type": record['member_type'],
            "status_flag": record['status_flag'],
            "user_identifier": record['user_identifier'],
            "landmark": record['landmark'],
            "city": record['city'],
            "state": record['state'],
            "country": record['country'],
            "location_id": record['location_id'],
            "location_name": record['location_id__location_Name'],
            "city_name": record['city__city_name'],
            "state_name": record['state__states_name'],
            "created_on": record['created_on'].isoformat(),  # ISO 8601 format
        })
    return transformed_dta


def load_data_to_mongo(data):

    mongo_client = MongoClient("mongodb://localhost:27017//")
    mongo_db = mongo_client['tagnpayloyalty_analytics

']
    mongo_collection = mongo_db['loyaltycustomers']
    
    if data:
        # Use `insert_many` to bulk insert data
        mongo_collection.insert_many(data, ordered=False)
    print(f"Inserted {len(data)} records into MongoDB.")


def etl_pipeline():
    print("Starting ETL Pipeline...")
    
    # Extract
    print("Extracting data from MySQL...")
    extracted_data = extract_data()
    
    # Transform
    print("Transforming data...")
    transformed_data = transform_data(extracted_data)
    
    # Load
    print("Loading data into MongoDB...")
    load_data_to_mongo(transformed_data)
    
    print("ETL Pipeline completed successfully!")

