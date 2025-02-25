from datetime import datetime, time, timedelta
from pymongo import MongoClient
from django.core.paginator import Paginator

from tagnpayloyalty.models import *
from tagnpayloyalty.helpers import *
from django.db.models import Count, Sum
from django.db import connection
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


def get_transaction_summary_data(
    start_date, end_date, brand_id, report_type, for_export=False
):
    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["tagnpayloyalty_analytics"]
    mongo_cust_collection = mongo_db["loyaltytransactionsdata"]

    # Convert start and end date to datetime format
    date_filter = {}
    if start_date:
        date_filter["$gte"] = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_date_with_time = datetime.combine(
            datetime.strptime(end_date, "%Y-%m-%d"), time.max
        )
        date_filter["$lte"] = end_date_with_time  # Ensure it includes the full day

    # Build query filter
    query_filter = {
        "brand_id": brand_id,
        "bill_trans_type": "Earn",
        "status_flag": 1,
    }
    if date_filter:
        query_filter["created_on"] = date_filter  # Apply date filter

    # Mapping for report type to MongoDB fields
    report_field_map = {
        "Location": "$location_Name",
        "City": "$location_city",
        "State": "$location_state",
        "Zone": "$location_zone",
        "Month": {"$dateToString": {"format": "%Y-%m", "date": "$created_on"}},
        "Tier": "$tier_name",
    }

    # MongoDB Aggregation Pipeline
    pipeline = [
        {"$match": query_filter},
        {
            "$group": {
                "_id": report_field_map.get(report_type, "$location_Name"),
                "total_customers": {"$addToSet": "$mobileno"},
                "total_bills": {"$sum": 1},
                "total_purchase": {"$sum": "$bill_amount"},
                "total_earnpts": {"$sum": "$points"},
            }
        },
        {
            "$project": {
                "total_customers": {"$size": "$total_customers"},
                "total_bills": 1,
                "total_purchase": {"$round": ["$total_purchase", 2]},
                "total_earnpts": 1,
            }
        },
        {"$sort": {"_id": 1}},
    ]

    # If not for export, add the 'category' field for HTML rendering
    if not for_export:
        pipeline[2]["$project"]["category"] = "$_id"

    # Execute query
    data = list(mongo_cust_collection.aggregate(pipeline))
    return data, query_filter


def get_customer_transactions_summary_details(
    brand_id, start_date, end_date, report_type, category_value, page, per_page
):
    # Connect to MongoDB
    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["tagnpayloyalty_analytics"]
    mongo_cust_collection = mongo_db["loyaltytransactionsdata"]
    print("start_date---------------------------------------------", start_date)
    print("end_date---------------------------------------------", end_date)
    print("page---------------------------------------------", page)
    print("report_type---------------------------------------------", report_type)
    print("category---------------------------------------------", category_value)
    print("per_page---------------------------------------------", per_page)

    # Convert start and end date to datetime format
    date_filter = {}
    if start_date:
        date_filter["$gte"] = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_date_with_time = datetime.combine(
            datetime.strptime(end_date, "%Y-%m-%d"), time.max
        )
        date_filter["$lte"] = end_date_with_time  # Ensure it includes the full day

    # Build query filter
    query_filter = {
        "brand_id": brand_id,
        "bill_trans_type": "Earn",
        "status_flag": 1,
    }
    if date_filter:
        query_filter["bill_date"] = date_filter  # Apply date filter

    # Map report type to MongoDB field
    report_field_map = {
        "Location": "location_Name",
        "City": "location_city",
        "State": "location_state",
        "Zone": "location_zone",
        "Month": {"$dateToString": {"format": "%Y-%m", "date": "$bill_date"}},
        "Tier": "tier_name",
    }

    # Handle "Month" report type filtering
    if report_type in ["Location", "City", "State", "Zone", "Tier"]:
        query_filter[report_field_map[report_type]] = category_value
    elif report_type == "Month":
        try:
            # Convert "September 2016" -> First and Last day of the month
            start_of_month = datetime.strptime(category_value, "%B %Y").replace(day=1)
            end_of_month = datetime.combine(
                start_of_month.replace(month=start_of_month.month % 12 + 1, day=1)
                - timedelta(days=1),
                time.max,
            )
            query_filter["bill_date"] = {"$gte": start_of_month, "$lte": end_of_month}

            print(f"Filtering from {start_of_month} to {end_of_month}")

        except ValueError:
            print("Error: Invalid month format in category_value:", category_value)
            return {
                "data": [],
                "has_next": False,
                "has_previous": False,
                "page_no": page,
                "total_pages": 0,
                "new_page_list": [],
            }

    # Fetch all transactions matching the filter
    transactions = list(
        mongo_cust_collection.find(
            query_filter,
            {
                "_id": 0,
                "mobileno": 1,
                "bill_number": 1,
                "bill_amount": 1,
                "bill_date": 1,
                "bill_status": 1,
            },
        )
    )
    print("tra", transactions)

    # Convert bill_date to readable format
    for trans in transactions:
        bill_date = trans.get("bill_date")
        # Ensure bill_date is a datetime object
        if isinstance(bill_date, datetime):
            trans["bill_date"] = trans["bill_date"].strftime("%d-%b-%Y")
        elif isinstance(trans.get("bill_date"), str):
            try:
                # If the bill_date is a string, attempt to convert it
                trans["bill_date"] = datetime.strptime(
                    trans["bill_date"], "%Y-%m-%d"
                ).strftime("%d-%b-%Y")
            except ValueError:
                # Handle case where the date format is invalid
                trans["bill_date"] = "Invalid Date"
        else:
            # If no valid date is available, you can set a default value like this
            trans["bill_date"] = "N/A"

    # Paginate results
    paginator = Paginator(transactions, per_page)
    paginated_transactions = paginator.get_page(page)

    # Generate pagination numbers dynamically
    total_pages = paginator.num_pages
    page_no = int(page) if page else 1

    if total_pages <= 3:
        new_page_list = list(range(1, total_pages + 1))
    elif page_no <= 2:
        new_page_list = [1, 2, 3]
    elif page_no >= total_pages - 1:
        new_page_list = [total_pages - 2, total_pages - 1, total_pages]
    else:
        new_page_list = [page_no - 1, page_no, page_no + 1]

    return {
        "data": list(paginated_transactions),
        "has_next": paginated_transactions.has_next(),
        "has_previous": paginated_transactions.has_previous(),
        "page_no": page_no,
        "total_pages": total_pages,
        "new_page_list": new_page_list,
    }


def get_earn_burn_summary(brand_id, start_date, end_date, report_type):
    """Fetches Earn & Burn summary from MongoDB."""

    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["tagnpayloyalty_analytics"]
    mongo_collection = mongo_db["loyaltytransactionsdata"]

    # Convert start and end date to datetime format
    date_filter = {}
    if start_date:
        date_filter["$gte"] = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        date_filter["$lte"] = datetime.combine(
            datetime.strptime(end_date, "%Y-%m-%d"), datetime.max.time()
        )

    query_filter = {
        "brand_id": brand_id,
        "status_flag": 1,
        "bill_trans_type": {"$in": ["Earn", "Redeem"]},
    }
    if date_filter:
        query_filter["bill_date"] = date_filter

    report_field_map = {
        "Location": "$location_Name",
        "City": "$location_city",
        "State": "$location_state",
        "Zone": "$location_zone",
        "Month": {"$dateToString": {"format": "%Y-%m", "date": "$bill_date"}},
        "Tier": "$tier_name",
    }
    group_by_field = report_field_map.get(report_type, "$location_Name")

    pipeline = [
        {"$match": query_filter},
        {
            "$group": {
                "_id": {
                    "group_by": group_by_field,
                    "bill_trans_type": "$bill_trans_type",
                },
                "total_points": {"$sum": "$points"},
            }
        },
        {
            "$group": {
                "_id": "$_id.group_by",
                "tot_earn": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$_id.bill_trans_type", "Earn"]},
                            "$total_points",
                            0,
                        ]
                    }
                },
                "tot_redeem": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$_id.bill_trans_type", "Redeem"]},
                            "$total_points",
                            0,
                        ]
                    }
                },
            }
        },
        {
            "$project": {
                "_id": 0,
                "category": "$_id",
                "tot_earn": {"$round": ["$tot_earn", 2]},
                "tot_redeem": {"$round": ["$tot_redeem", 2]},
                "tot_liability": {
                    "$round": [{"$subtract": ["$tot_earn", "$tot_redeem"]}, 2]
                },
            }
        },
        {"$sort": {"category": 1}},
    ]

    result = list(mongo_collection.aggregate(pipeline))

    if report_type == "Month":
        for item in result:
            year, month = item["category"].split("-")
            item["category"] = (
                datetime.strptime(month, "%m").strftime("%B") + " " + year
            )

    return result


def get_customer_earn_burn_details(
    brand_id,
    category,
    report_type,
    start_date,
    end_date,
    transaction_type,
    per_page,
    page=1,
):
    """Fetch customer transactions based on filters for both modal view and export."""

    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["tagnpayloyalty_analytics"]
    mongo_collection = mongo_db["loyaltytransactionsdata"]

    print("start_date---------------------------------------------", start_date)
    print("end_date---------------------------------------------", end_date)
    print("page---------------------------------------------", page)
    print(
        "transaction_type---------------------------------------------",
        transaction_type,
    )
    print("report_type---------------------------------------------", report_type)
    print("category---------------------------------------------", category)
    print("per_page---------------------------------------------", per_page)

    # Date filter
    date_filter = {}
    if start_date:
        date_filter["$gte"] = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        date_filter["$lte"] = datetime.combine(
            datetime.strptime(end_date, "%Y-%m-%d"), time.max
        )

    # Mapping report type to database field
    report_field_map = {
        "Location": "location_Name",
        "City": "location_city",
        "State": "location_state",
        "Zone": "location_zone",
    }
    category_filter = report_field_map.get(report_type, "location_Name")

    # Build the query
    match_query = {
        "brand_id": brand_id,
        "status_flag": 1,
        "bill_trans_type": transaction_type,  # "Earn" or "Redeem"
    }

    if date_filter:
        match_query["bill_date"] = date_filter

    if report_type == "Month":
        # Convert "August 2016" to actual date range
        try:
            start_of_month = datetime.strptime(category, "%B %Y").replace(day=1)
            end_of_month = datetime.combine(
                start_of_month.replace(month=start_of_month.month % 12 + 1, day=1)
                - timedelta(days=1),
                time.max,
            )
            match_query["bill_date"] = {"$gte": start_of_month, "$lte": end_of_month}
        except ValueError:
            print("Error: Invalid month format in category:", category)
            return {
                "data": [],
                "page_no": page,
                "total_pages": 0,
                "new_page_list": [],
                "has_previous": False,
                "has_next": False,
            }
    else:
        match_query[category_filter] = category

    # Debugging: Print the final query
    print("MongoDB Query:", match_query)

    # Fetch transactions
    projection = {
        "_id": 0,
        "mobileno": 1,
        "bill_number": 1,
        "bill_date": 1,
        "points": 1,  # Keep 'points' field as-is
        "bill_status": 1,
    }

    transactions = list(mongo_collection.find(match_query, projection))

    # Format bill_date and ensure points are present
    for transaction in transactions:
        if "bill_date" in transaction:
            transaction["bill_date"] = transaction["bill_date"].strftime("%d-%b-%Y")

        if "points" not in transaction:
            transaction["points"] = 0  # Ensure points exist

    # Paginate results
    paginator = Paginator(transactions, per_page)
    paginated_transactions = paginator.get_page(page)
    total_pages = paginator.num_pages

    new_page_list = (
        list(range(1, total_pages + 1))
        if total_pages <= 3
        else (
            [1, 2, 3]
            if page <= 2
            else (
                [total_pages - 2, total_pages - 1, total_pages]
                if page >= total_pages - 1
                else [page - 1, page, page + 1]
            )
        )
    )

    return {
        "data": list(paginated_transactions),
        "page_no": page,
        "total_pages": total_pages,
        "new_page_list": new_page_list,
        "has_previous": page > 1,
        "has_next": page < total_pages,
    }


def get_repeat_customers_data(brand_id, start_date, end_date):
    """Fetch repeat customer data from MongoDB."""
    # Connect to MongoDB
    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["tagnpayloyalty_analytics"]
    mongo_cust_collection = mongo_db["loyaltytransactionsdata"]

    # Convert start and end date to datetime
    date_filter = {}
    if start_date:
        date_filter["$gte"] = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        date_filter["$lte"] = datetime.strptime(end_date, "%Y-%m-%d")

    # Build query filter
    query_filter = {"brand_id": brand_id, "status_flag": 1}
    if date_filter:
        query_filter["bill_date"] = date_filter  # Apply date filter

    # Aggregation pipeline
    pipeline = [
        {"$match": query_filter},
        {
            "$group": {
                "_id": {"mobileno": "$mobileno", "location_Name": "$location_Name"},
                "visit_count": {"$sum": 1},
            }
        },
        {"$match": {"visit_count": {"$gt": 1}}},  # Customers who visited more than once
        {"$group": {"_id": "$_id.location_Name", "repeat_customers": {"$sum": 1}}},
        {"$project": {"_id": 0, "location_Name": "$_id", "repeat_customers": 1}},
        {"$sort": {"location_Name": 1}},  # Sort alphabetically by location name
    ]

    return list(mongo_cust_collection.aggregate(pipeline))


def get_repeat_customer_details(
    brand_id, start_date, end_date, location_name, per_page, page=1
):
    """Fetch repeat customer details based on filters for both modal view and export."""

    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["tagnpayloyalty_analytics"]
    mongo_collection = mongo_db["loyaltytransactionsdata"]

    print("start_date---------------------------------------------", start_date)
    print("end_date---------------------------------------------", end_date)
    print("page---------------------------------------------", page)
    print("location_name---------------------------------------------", location_name)
    print("per_page---------------------------------------------", per_page)

    # Date filter
    date_filter = {}
    if start_date:
        date_filter["$gte"] = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        date_filter["$lte"] = datetime.strptime(end_date, "%Y-%m-%d")

    # Query filter
    match_query = {
        "brand_id": brand_id,
        "status_flag": 1,
        "location_Name": location_name,
    }

    if date_filter:
        match_query["bill_date"] = date_filter

    # Aggregation pipeline
    pipeline = [
        {"$match": match_query},
        {"$sort": {"bill_date": 1, "mobileno": 1}},  # Sort by customer, then date
        {
            "$group": {
                "_id": "$mobileno",
                "transactions": {"$push": "$$ROOT"},
                "visit_count": {"$sum": 1},
            }
        },
        {"$match": {"visit_count": {"$gt": 1}}},  # Only repeat customers
        {"$unwind": "$transactions"},  # Flatten the array to get all transactions back
        {
            "$project": {
                "_id": 0,
                "Mobile No": "$transactions.mobileno",
                "Bill Date": "$transactions.bill_date",
                "Bill Amount": "$transactions.bill_amount",
                "Bill Number": "$transactions.bill_number",
                "Bill Status": "$transactions.bill_status",
            }
        },
    ]

    transactions = list(mongo_collection.aggregate(pipeline))

    # Format bill_date
    for transaction in transactions:
        if "Bill Date" in transaction:
            transaction["Bill Date"] = transaction["Bill Date"].strftime("%d-%b-%Y")

    # Paginate results
    paginator = Paginator(transactions, per_page)
    paginated_transactions = paginator.get_page(page)
    total_pages = paginator.num_pages

    new_page_list = (
        list(range(1, total_pages + 1))
        if total_pages <= 3
        else (
            [1, 2, 3]
            if page <= 2
            else (
                [total_pages - 2, total_pages - 1, total_pages]
                if page >= total_pages - 1
                else [page - 1, page, page + 1]
            )
        )
    )

    return {
        "data": list(paginated_transactions),
        "page_no": page,
        "total_pages": total_pages,
        "new_page_list": new_page_list,
        "has_previous": page > 1,
        "has_next": page < total_pages,
    }


def get_top_customers(brand_id, report_type):
    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["tagnpayloyalty_analytics"]
    mongo_collection = mongo_db["loyaltytransactionsdata"]

    pipeline = [
        {"$match": {"brand_id": brand_id, "status_flag": 1}},
        {
            "$group": {
                "_id": "$mobileno",
                "total_visits": {"$sum": 1},
                "total_purchase": {"$sum": "$bill_amount"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "mobile_no": "$_id",
                "total_visits": 1,
                "total_purchase": 1,
            }
        },
        {"$sort": {"total_visits" if report_type == "visit" else "total_purchase": -1}},
        {"$limit": 10},
    ]

    return list(mongo_collection.aggregate(pipeline))


def get_repeat_transaction_summary(
    brand_id, start_date=None, end_date=None, report_type="Location"
):
    """This function is used to get the summary data in the repeat transaction report."""
    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["tagnpayloyalty_analytics"]
    mongo_collection = mongo_db["loyaltytransactionsdata"]

    now = datetime.now()
    start_date_dt = (
        datetime.strptime(start_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
        if start_date
        else datetime(now.year, now.month, 1, 0, 0, 0)
    )
    end_date_dt = (
        datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        if end_date
        else datetime(now.year, now.month, now.day, 23, 59, 59)
    )
    print("start date---------------------", start_date_dt)
    print("end date-----------------------", end_date_dt)

    report_type_field = {
        "Location": "$location_Name",
        "City": "$location_city",
        "State": "$location_state",
        "Zone": "$location_zone",
        "Month": {"$dateToString": {"format": "%Y-%m", "date": "$bill_date"}},
    }.get(report_type, "$location_Name")

    # Step 1: Fetch customers who transacted in the time range
    pipeline = [
        {
            "$match": {
                "status_flag": 1,
                "brand_id": brand_id,
                "bill_trans_type": "Earn",
                "bill_date": {"$gte": start_date_dt, "$lte": end_date_dt},
            }
        },
        {
            "$group": {
                "_id": "$mobileno",
                "first_bill_date_in_range": {"$min": "$bill_date"},
                "total_trans_in_range": {"$sum": 1},
                "total_purchase_in_range": {"$sum": "$bill_amount"},
                "report_group": {"$first": report_type_field},
            }
        },
    ]
    customer_data = list(mongo_collection.aggregate(pipeline))
    print("customer data------------------------------", customer_data)
    customer_ids = [c["_id"] for c in customer_data]

    # Step 2: Check if customers have transactions outside the time range
    second_pipeline = [
        {
            "$match": {
                "mobileno": {"$in": customer_ids},
                "status_flag": 1,
                "brand_id": brand_id,
                "bill_trans_type": "Earn",
            }
        },
        {
            "$group": {
                "_id": "$mobileno",
                "first_transaction_date": {"$min": "$bill_date"},
            }
        },
    ]
    classification_data = {
        c["_id"]: c for c in mongo_collection.aggregate(second_pipeline)
    }
    print("classification data---------------------------------", classification_data)

    # Step 3: Aggregate results
    summary = {}
    for customer in customer_data:
        print("customer---------------------", customer)
        customer_id = customer["_id"]
        report_group = customer["report_group"]
        first_transaction_date = classification_data.get(customer_id, {}).get(
            "first_transaction_date", start_date_dt
        )

        if report_group not in summary:
            summary[report_group] = {
                "unique_customers": 0,
                "total_bills": 0,
                "tot_purchase": 0,
                "total_earlier_repeat_customers": 0,
                "total_earlier_repeat_trans": 0,
                "total_earlier_repeat_trans_amount": 0,
                "total_unique_current_repeat_cust": 0,
                "total_current_repeat_trans": 0,
                "total_current_repeat_trans_amount": 0,
                "total_unique_repeat_customers": 0,
                "total_repeat_trans": 0,
                "total_repeat_trans_amount": 0,
            }

        summary[report_group]["unique_customers"] += 1
        summary[report_group]["total_bills"] += customer["total_trans_in_range"]
        summary[report_group]["tot_purchase"] += customer["total_purchase_in_range"]

        if first_transaction_date < start_date_dt:
            summary[report_group]["total_earlier_repeat_customers"] += 1
            summary[report_group]["total_earlier_repeat_trans"] += customer[
                "total_trans_in_range"
            ]
            summary[report_group]["total_earlier_repeat_trans_amount"] += customer[
                "total_purchase_in_range"
            ]
        elif customer["total_trans_in_range"] > 1:
            summary[report_group]["total_unique_current_repeat_cust"] += 1
            summary[report_group]["total_current_repeat_trans"] += customer[
                "total_trans_in_range"
            ]
            summary[report_group]["total_current_repeat_trans_amount"] += customer[
                "total_purchase_in_range"
            ]

        summary[report_group]["total_unique_repeat_customers"] = (
            summary[report_group]["total_earlier_repeat_customers"]
            + summary[report_group]["total_unique_current_repeat_cust"]
        )
        summary[report_group]["total_repeat_trans"] = (
            summary[report_group]["total_earlier_repeat_trans"]
            + summary[report_group]["total_current_repeat_trans"]
        )
        summary[report_group]["total_repeat_trans_amount"] = (
            summary[report_group]["total_earlier_repeat_trans_amount"]
            + summary[report_group]["total_current_repeat_trans_amount"]
        )

    return [{"category": key, **value} for key, value in summary.items()]


def fetch_customer_repeat_transaction_detail_data(
    brand_id,
    category,
    report_type,
    start_date,
    end_date,
    transaction_type,
    per_page,
    page=1,
):
    """This function fetches customer data in the repeat transaction report."""
    
    # Connect to MongoDB
    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["tagnpayloyalty_analytics"]
    mongo_collection = mongo_db["loyaltytransactionsdata"]

    print("brand_id:", brand_id)
    print("category:", category)
    print("report_type:", report_type)
    print("transaction_type:", transaction_type)

    now = datetime.now()
    start_date_dt = (
        datetime.strptime(start_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
        if start_date
        else datetime(now.year, now.month, 1, 0, 0, 0)
    )
    end_date_dt = (
        datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        if end_date
        else datetime(now.year, now.month, now.day, 23, 59, 59)
    )

    print("start_date_dt:", start_date_dt)
    print("end_date_dt:", end_date_dt)

    # Handle Month Type Separately
    if report_type == "Month":
        try:
            start_date_dt = datetime.strptime(category, "%B %Y").replace(day=1, hour=0, minute=0, second=0)
            end_date_dt = datetime.combine(
                start_date_dt.replace(month=start_date_dt.month % 12 + 1, day=1) - timedelta(days=1),
                time.max,
            )
        except ValueError:
            return {"error": "Invalid month format. Use 'Month Year' (e.g., 'February 2025')"}

    # Define the field for grouping based on report type
    report_type_field = {
        "Location": "location_Name",
        "City": "location_city",
        "State": "location_state",
        "Zone": "location_zone",
    }.get(report_type)

    # Step 1: Find customers who made transactions in the time range
    customer_pipeline = [
        {
            "$match": {
                "status_flag": 1,
                "brand_id": brand_id,
                "bill_trans_type": "Earn",
                "bill_date": {"$gte": start_date_dt, "$lte": end_date_dt},
            }
        },
        {"$group": {"_id": "$mobileno", "first_bill_date": {"$min": "$bill_date"}}},
    ]

    if report_type_field:  # Apply category filter only if needed
        customer_pipeline[0]["$match"][report_type_field] = category

    customers_in_range = list(mongo_collection.aggregate(customer_pipeline))
    customer_ids = {c["_id"]: c["first_bill_date"] for c in customers_in_range}

    # Step 2: Find first transaction dates outside the given time range
    past_transaction_pipeline = [
        {
            "$match": {
                "mobileno": {"$in": list(customer_ids.keys())},
                "status_flag": 1,
                "brand_id": brand_id,
                "bill_trans_type": "Earn",
            }
        },
        {
            "$group": {
                "_id": "$mobileno",
                "first_transaction_date": {"$min": "$bill_date"},
            }
        },
    ]
    past_transactions = {
        c["_id"]: c["first_transaction_date"]
        for c in mongo_collection.aggregate(past_transaction_pipeline)
    }

    print("past_transactions:", past_transactions)

    # Step 3: Categorize customers
    current_customers = {
        mobile
        for mobile, date in customer_ids.items()
        if start_date_dt <= date <= end_date_dt
    }
    repeat_customers = {
        mobile for mobile, date in past_transactions.items() if date < start_date_dt
    }

    # Step 4: Find current repeat customers (who made multiple transactions in the time range)
    current_repeat_customers_pipeline = [
        {
            "$match": {
                "mobileno": {"$in": list(current_customers)},  # Only check current customers
                "status_flag": 1,
                "brand_id": brand_id,
                "bill_trans_type": "Earn",
                "bill_date": {"$gte": start_date_dt, "$lte": end_date_dt},
            }
        },
        {"$group": {"_id": "$mobileno", "transaction_count": {"$sum": 1}}},  # Count transactions per customer
        {"$match": {"transaction_count": {"$gt": 1}}},  # Only customers with multiple transactions
    ]
    current_repeat_customers = {
        c["_id"] for c in mongo_collection.aggregate(current_repeat_customers_pipeline)
    }

    print("current_customers:", current_customers)
    print("repeat_customers:", repeat_customers)

    # Step 4: Filter data based on transaction_type
    if transaction_type == "total":
        filter_customers = list(customer_ids.keys())
    elif transaction_type == "current":
        filter_customers = list(current_repeat_customers)
    elif transaction_type == "earlier":
        filter_customers = list(repeat_customers)
    elif transaction_type == "total_repeat":
        filter_customers = list(current_repeat_customers | repeat_customers)
    else:
        filter_customers = []

    # Construct the match query
    match_stage = {
        "status_flag": 1,
        "brand_id": brand_id,
        "bill_trans_type": "Earn",
        "bill_date": {"$gte": start_date_dt, "$lte": end_date_dt},
        "mobileno": {"$in": filter_customers},
    }

    if report_type_field:  # Apply category filter only if needed
        match_stage[report_type_field] = category

    transaction_pipeline = [
        {"$match": match_stage},
        {
            "$project": {
                "_id": 0,
                "mobileno": 1,
                "bill_number": 1,
                "bill_date": 1,
                "bill_status": 1,
            }
        },
    ]

    transactions = list(mongo_collection.aggregate(transaction_pipeline))

    # Step 5: Paginate Results
    paginator = Paginator(transactions, per_page)
    paginated_transactions = paginator.get_page(page)
    total_pages = paginator.num_pages

    new_page_list = (
        list(range(1, total_pages + 1))
        if total_pages <= 3
        else (
            [1, 2, 3]
            if page <= 2
            else (
                [total_pages - 2, total_pages - 1, total_pages]
                if page >= total_pages - 1
                else [page - 1, page, page + 1]
            )
        )
    )

    return {
        "data": list(paginated_transactions),
        "page_no": page,
        "total_pages": total_pages,
        "new_page_list": new_page_list,
        "has_previous": page > 1,
        "has_next": page < total_pages,
    }
