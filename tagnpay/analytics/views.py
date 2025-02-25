from errno import EILSEQ
from turtle import end_fill
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from pymysql import NULL
import pandas as pd
from rest_framework.response import Response
from tagnpayloyalty.models import *
from django.urls import reverse
from datetime import datetime, timedelta
from django.core.paginator import Paginator
import matplotlib.pyplot as plt
import io
from django.http import JsonResponse
from django.db import connection
import plotly.express as px
from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from tagnpay.env_details import *
import random
from pymongo import MongoClient
import calendar
import xml.etree.ElementTree as ET
from django.db.models import Count, Sum, F, Q
from django.shortcuts import render
from django.views import View
from collections import defaultdict
from . import helpers as analytics_helpers
from django.utils.timezone import now
from tagnpayloyalty.helpers import *
from datetime import datetime


per_page = 50


class View_LoyaltyCustomerData(TemplateView):

    def get(self, request):

        loyalcustomers = (
            LoyaltyCustomers.objects.select_related("location_id", "mall_brand_id")
            .all()
            .order_by("-created_on")
        )
        brand_id = request.session.get("brand_id")
        loyalcustomers = loyalcustomers.filter(status_flag=1, brand_id=brand_id)

        total_loyal_customers = loyalcustomers.count()

        paginator = Paginator(loyalcustomers, per_page)
        page_no = request.GET.get("page")
        loyalcustomersfinal = paginator.get_page(page_no)
        totalpage = loyalcustomersfinal.paginator.num_pages
        # print(page_no)
        if page_no is None or page_no == "":
            page_no = 1
        if totalpage > 1 and totalpage < 4:
            newpagelist = [1, 2, 3]
        else:
            newpagelist = [page_no, int(page_no) + 1, int(page_no) + 2]
        if int(totalpage) >= int(page_no) and int(totalpage) - 2 <= int(page_no):
            newpagelist = [int(totalpage) - 2, int(totalpage) - 1, int(totalpage)]

        locations = LocationMst.objects.all().order_by("location_Name")
        brands = RewardBrandsMst.objects.all().order_by("rwrd_brand_name")

        return render(
            request,
            "pages/forms/analytics-customer-details.html",
            {
                "loyalcustomers": loyalcustomersfinal,
                "locations": locations,
                "brands": brands,
                "page_no": page_no,
                "totalpage": totalpage,
                "totalpagelist": [n + 1 for n in range(totalpage)],
                "newpagelist": newpagelist,
                "total_loyal_customers": total_loyal_customers,
            },
        )

    def post(self, request):

        loyalcustomers = (
            LoyaltyCustomers.objects.select_related("location_id", "mall_brand_id")
            .all()
            .order_by("-created_on")
        )
        brand_id = request.session.get("brand_id")
        loyalcustomers = loyalcustomers.filter(status_flag=1, brand_id=brand_id)
        locations = LocationMst.objects.all().order_by("location_Name")
        brands = RewardBrandsMst.objects.all().order_by("rwrd_brand_name")

        total_loyal_customers = loyalcustomers.count()

        if request.method == "POST":
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")
            location_filter = request.POST.get("location")
            brand_filter = request.POST.get("brand")

            # Apply date filters if start_date and/or end_date are provided
            if start_date:
                try:
                    start_date = datetime.strptime(start_date, "%Y-%m-%d")
                    loyalcustomers = loyalcustomers.filter(created_on__gte=start_date)
                except ValueError:
                    pass  # Handle invalid date format

            if end_date:
                try:
                    end_date = datetime.strptime(end_date, "%Y-%m-%d")
                    end_date_with_time = datetime.combine(end_date, datetime.max.time())
                    loyalcustomers = loyalcustomers.filter(
                        created_on__lte=end_date_with_time
                    )
                except ValueError:
                    pass  # Handle invalid date format

            # Apply location filter if available
            if location_filter:
                loyalcustomers = loyalcustomers.filter(location_id=location_filter)

            # Apply brand filter if available
            if brand_filter:
                loyalcustomers = loyalcustomers.filter(mall_brand_id=brand_filter)

            paginator = Paginator(loyalcustomers, per_page)
            page_no = request.GET.get("page")
            loyalcustomersfinal = paginator.get_page(page_no)
            totalpage = loyalcustomersfinal.paginator.num_pages
            if page_no is None or page_no == "":
                page_no = 1
            if totalpage > 1 and totalpage < 4:
                newpagelist = [1, 2, 3]
            else:
                newpagelist = [page_no, int(page_no) + 1, int(page_no) + 2]
            if int(totalpage) >= int(page_no) and int(totalpage) - 2 <= int(page_no):
                newpagelist = [int(totalpage) - 2, int(totalpage) - 1, int(totalpage)]

        return render(
            request,
            "pages/forms/analytics-customer-details.html",
            {
                "loyalcustomers": loyalcustomersfinal,
                "locations": locations,
                "brands": brands,
                "selected_location": location_filter,
                "selected_brand": brand_filter,
                "start_date": start_date,
                "end_date": end_date,
                "page_no": page_no,
                "totalpage": totalpage,
                "totalpagelist": [n + 1 for n in range(totalpage)],
                "newpagelist": newpagelist,
                "total_loyal_customers": total_loyal_customers,
            },
        )


def View_CustomersData(request):
    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["tagnpayloyalty_analytics"]
    brand_id = request.session.get("brand_id")
    mongo_cust_collection = mongo_db["loyaltycustomersdata"]
    start_date = None
    end_date = None
    selected_report = "Location"

    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        selected_report = request.POST.get("report_type")
        print("1  Start Date:", start_date)
        print("1  End Date:", end_date)

        # Apply date filters if start_date and/or end_date are provided
        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                pass  # Handle invalid date format

        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                end_date_with_time = datetime.combine(end_date, datetime.max.time())
            except ValueError:
                pass  # Handle invalid date format

        print("2 Start Date:", start_date)
        print("2 End Date:", end_date)

    report_types = ["Location", "City", "State", "Zone", "Month", "Tier"]
    # Build query
    match_query = {"brand_id": int(brand_id), "status_flag": 1}

    if start_date and end_date:
        match_query["created_on"] = {"$gte": start_date, "$lte": end_date}
    elif start_date:
        match_query["created_on"] = {"$gte": start_date}
    elif end_date:
        match_query["created_on"] = {"$lte": end_date_with_time}

    # Select filreport type field
    report_type_mapping = {
        "Location": "$location_name",
        "City": "$city",
        "State": "$state",
        "Zone": "$location_zone",
        "Month": {"$dateToString": {"format": "%Y-%m", "date": "$created_on"}},
        "Tier": "$tier",
    }
    group_by_field = report_type_mapping.get(selected_report, "$location_name")

    pipeline = [
        {"$match": match_query},
        {"$group": {"_id": group_by_field, "customer_count": {"$sum": 1}}},
    ]

    results = list(mongo_cust_collection.aggregate(pipeline))

    sum_of_tot_cusomers = mongo_cust_collection.count_documents(
        {"brand_id": int(brand_id), "status_flag": 1}
    )
    x_axis_label = selected_report  # Dynamically set x-axis label

    # Extract Data for Plotly
    locations = [res["_id"] for res in results]
    counts = [res["customer_count"] for res in results]

    if results:
        customer_data = pd.DataFrame(results)
        customer_data.rename(columns={"_id": x_axis_label}, inplace=True)
    else:
        customer_data = pd.DataFrame(columns=[x_axis_label, "customer_count"])

    # Sort dynamically based on selected report type
    if selected_report in ["City", "State", "Zone", "Location", "Tier"]:
        customer_data[selected_report] = (
            customer_data[selected_report].fillna("").astype(str)
        )
        customer_data = customer_data.sort_values(
            by=selected_report, ascending=True
        )  # A-Z sorting
    else:
        customer_data = customer_data.sort_values(
            by="customer_count", ascending=False
        )  # High to Low sorting

    # Generate random colors
    num_bars = len(customer_data)  # Number of bars in the chart
    colors = [
        "#" + "".join(random.choices("0123456789ABCDEF", k=6)) for _ in range(num_bars)
    ]

    # Create Plotly Figure
    fig = px.bar(
        customer_data,
        x=x_axis_label,
        y="customer_count",
        labels={"x": x_axis_label, "y": "Customer Count"},
        title=f"Customer Count by {x_axis_label}",
        text_auto=True,
        hover_data={x_axis_label: True, "customer_count": True},
    )

    # Manually set the bar colors
    fig.update_traces(marker=dict(color=colors))

    # Convert Figure to JSON for rendering in template
    # graph_json = json.dumps(fig, cls=px.utils.PlotlyJSONEncoder)

    graph = fig.to_html(full_html=False)
    customer_data.rename(columns={x_axis_label: "category"}, inplace=True)

    if selected_report == "Month":
        # Convert 'YYYY-MM' to 'Month YYYY' & Sort
        customer_data["category"] = customer_data["category"].apply(
            lambda x: f"{calendar.month_name[int(x.split('-')[1])]} {x.split('-')[0]}"
        )

        # Ensure sorting by actual month order
        customer_data["sort_key"] = customer_data["category"].apply(
            lambda x: datetime.strptime(x, "%B %Y")
        )
        customer_data = customer_data.sort_values("sort_key").drop(columns=["sort_key"])

    context = {
        #'grouped_data': grouped_dict,
        "graph": graph,
        "customer_data": customer_data.to_dict(orient="records"),
        #'plot_html': plot_div,
        "sum_of_tot_cusomers": sum_of_tot_cusomers,
        "report_types": report_types,
        "start_date": start_date,
        "end_date": end_date,
        "selected_report": selected_report,
        # "fig_bar": fig_bar_div,
        # "fig_pie": fig_pie_div,
    }
    print("Start Date:", start_date)
    print("End Date:", end_date)

    return render(request, "pages/forms/customersbylocandbrand.html", context)


def ExportCustomerData(request):
    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["tagnpayloyalty_analytics"]
    brand_id = request.session.get("brand_id")
    mongo_cust_collection = mongo_db["loyaltycustomersdata"]
    start_date = None
    end_date = None
    selected_report = "Location"

    if not brand_id:
        return JsonResponse({"error": "Brand ID not found in session"}, status=400)

    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        selected_report = request.POST.get("report_type")

        # Apply date filters if start_date and/or end_date are provided
        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                pass  # Handle invalid date format

        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                end_date_with_time = datetime.combine(end_date, datetime.max.time())
            except ValueError:
                pass  # Handle invalid date format

    # Build query
    match_query = {"brand_id": int(brand_id), "status_flag": 1}

    if start_date and end_date:
        match_query["created_on"] = {"$gte": start_date, "$lte": end_date}
    elif start_date:
        match_query["created_on"] = {"$gte": start_date}
    elif end_date:
        match_query["created_on"] = {"$lte": end_date_with_time}

    # Select filreport type field
    report_type_mapping = {
        "Location": "$location_name",
        "City": "$city",
        "State": "$state",
        "Zone": "$location_zone",
        "Month": {"$dateToString": {"format": "%Y-%m", "date": "$created_on"}},
        "Tier": "$tier",
    }
    group_by_field = report_type_mapping.get(selected_report, "$location_name")

    pipeline = [
        {"$match": match_query},
        {"$group": {"_id": group_by_field, "customer_count": {"$sum": 1}}},
    ]

    results = list(mongo_cust_collection.aggregate(pipeline))
    sum_of_tot_customers = mongo_cust_collection.count_documents(
        {"brand_id": int(brand_id), "status_flag": 1}
    )
    x_axis_label = selected_report  # Dynamically set x-axis label

    if results:
        customer_data = pd.DataFrame(results)
        customer_data.rename(columns={"_id": x_axis_label}, inplace=True)
    else:
        customer_data = pd.DataFrame(columns=[x_axis_label, "customer_count"])

    # Sort dynamically based on selected report type
    if selected_report in ["City", "State", "Zone", "Location", "Tier"]:
        customer_data[selected_report] = (
            customer_data[selected_report].fillna("").astype(str)
        )
        customer_data = customer_data.sort_values(
            by=selected_report, ascending=True
        )  # A-Z sorting
    else:
        customer_data = customer_data.sort_values(
            by="customer_count", ascending=False
        )  # High to Low sorting

    if selected_report == "Month":
        # Convert 'YYYY-MM' to 'Month YYYY' & Sort
        customer_data[x_axis_label] = customer_data[x_axis_label].apply(
            lambda x: f"{calendar.month_name[int(x.split('-')[1])]} {x.split('-')[0]}"
        )

        # Ensure sorting by actual month order
        customer_data["sort_key"] = customer_data[x_axis_label].apply(
            lambda x: datetime.strptime(x, "%B %Y")
        )
        customer_data = customer_data.sort_values("sort_key").drop(columns=["sort_key"])

    # Add total row
    total_row = pd.DataFrame(
        [{x_axis_label: "Total", "customer_count": sum_of_tot_customers}]
    )
    customer_data = pd.concat([customer_data, total_row], ignore_index=True)

    # Convert DataFrame to Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        customer_data.to_excel(writer, sheet_name="Customer Data", index=False)

    output.seek(0)
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="customer_data_by_{x_axis_label}.xlsx"'
    )
    return response


def fetch_customer_details(request):
    if request.method == "POST":
        brand_id = request.session.get("brand_id")
        category = request.POST.get("category")
        report_type = request.POST.get("report_type")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        page = int(request.POST.get("page", 1))

        mongo_client = MongoClient("mongodb://localhost:27017/")
        mongo_db = mongo_client["tagnpayloyalty_analytics"]
        mongo_cust_collection = mongo_db["loyaltycustomersdata"]

        match_query = {"brand_id": int(brand_id), "status_flag": 1}

        date_format = "%Y-%m-%d"
        if start_date:
            start_date = datetime.strptime(start_date, date_format)
        if end_date:
            end_date = datetime.strptime(end_date, date_format)

        if start_date and end_date:
            match_query["created_on"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            match_query["created_on"] = {"$gte": start_date}
        elif end_date:
            match_query["created_on"] = {"$lte": end_date}

        field_map = {
            "Location": "location_name",
            "City": "city",
            "State": "state",
            "Zone": "location_zone",
            "Tier": "tier",
        }
        if report_type in field_map:
            match_query[field_map[report_type]] = category
        elif report_type == "Month":
            category = datetime.strptime(category, "%B %Y").strftime("%Y-%m")
            # Update match_query for Month filtering
            match_query["$expr"] = {
                "$eq": [
                    {"$dateToString": {"format": "%Y-%m", "date": "$created_on"}},
                    category,
                ]
            }

        customer_details = list(
            mongo_cust_collection.find(
                match_query,
                {
                    "_id": 0,
                    "firstname": 1,
                    "lastname": 1,
                    "email": 1,
                    "mobileno": 1,
                    "city": 1,
                    "state": 1,
                    "location_zone": 1,
                    "tier": 1,
                    "gender": 1,
                    "created_on": 1,
                    "location_name": 1,
                },
            )
        )
        # Paginate results
        paginator = Paginator(customer_details, per_page)  # Show 10 customers per page
        paginated_customers = paginator.get_page(page)

        totalpage = paginator.num_pages
        page_no = int(page) if page else 1

        # Generate pagination numbers dynamically
        if totalpage <= 3:
            newpagelist = list(range(1, totalpage + 1))
        elif page_no <= 2:
            newpagelist = [1, 2, 3]
        elif page_no >= totalpage - 1:
            newpagelist = [totalpage - 2, totalpage - 1, totalpage]
        else:
            newpagelist = [page_no - 1, page_no, page_no + 1]

        return JsonResponse(
            {
                "data": list(paginated_customers),
                "has_next": paginated_customers.has_next(),
                "has_previous": paginated_customers.has_previous(),
                "page_no": page_no,
                "totalpage": totalpage,
                "newpagelist": newpagelist,
            }
        )

    return JsonResponse({"error": "Invalid request"}, status=400)


def export_customer_details(request):
    brand_id = request.session.get("brand_id")
    category = request.GET.get("category")
    report_type = request.GET.get("report_type")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    page = int(request.GET.get("page", 1))

    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_db = mongo_client["tagnpayloyalty_analytics"]
    mongo_cust_collection = mongo_db["loyaltycustomersdata"]

    match_query = {"brand_id": int(brand_id), "status_flag": 1}

    date_format = "%Y-%m-%d"
    if start_date:
        start_date = datetime.strptime(start_date, date_format)
    if end_date:
        end_date = datetime.strptime(end_date, date_format)

    if start_date and end_date:
        match_query["created_on"] = {"$gte": start_date, "$lte": end_date}
    elif start_date:
        match_query["created_on"] = {"$gte": start_date}
    elif end_date:
        match_query["created_on"] = {"$lte": end_date}

    field_map = {
        "Location": "location_name",
        "City": "city",
        "State": "state",
        "Zone": "location_zone",
        "Tier": "tier",
    }

    if report_type in field_map:
        match_query[field_map[report_type]] = category
    elif report_type == "Month":
        category = datetime.strptime(category, "%B %Y").strftime("%Y-%m")

        # Update match_query for Month filtering
        match_query["$expr"] = {
            "$eq": [
                {"$dateToString": {"format": "%Y-%m", "date": "$created_on"}},
                category,
            ]
        }

    customer_details = list(
        mongo_cust_collection.find(
            match_query,
            {
                "_id": 0,
                "firstname": 1,
                "lastname": 1,
                "email": 1,
                "mobileno": 1,
                "gender": 1,
                "created_on": 1,
            },
        )
    )
    # Paginate results
    paginator = Paginator(customer_details, per_page)  # Show 10 customers per page
    paginated_customers = list(paginator.get_page(page))
    df = pd.DataFrame(paginated_customers)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Customers", index=False)

    output.seek(0)
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="customer_details_by_{report_type}.xlsx"'
    )
    return response


class View_TransactionSummary(View):
    def get(self, request):
        # Connect to MongoDB
        mongo_client = MongoClient("mongodb://localhost:27017/")
        mongo_db = mongo_client["tagnpayloyalty_analytics"]
        mongo_cust_collection = mongo_db["loyaltytransactionsdata"]

        # Get filters from request
        brand_id = int(request.session.get("brand_id"))
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        report_type = request.GET.get("report_type", "Location")  # Default to Location
        print("start_date-------------------------------------------", start_date)
        print("end_date-------------------------------------------", end_date)
        print("report_type-------------------------------------------", report_type)
        print("brand id-------------------------------------------", brand_id)

        # Execute query
        trans_data, query_filter = analytics_helpers.get_transaction_summary_data(
            start_date, end_date, brand_id, report_type
        )
        print(trans_data)

        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Extract data for graph
        categories = [item["_id"] for item in trans_data]
        total_points = [item["total_earnpts"] for item in trans_data]
        total_purchase = [item["total_purchase"] for item in trans_data]
        total_bills = [item["total_bills"] for item in trans_data]
        unique_customers = [item["total_customers"] for item in trans_data]

        # Get total summary
        totals_data = mongo_cust_collection.aggregate(
            [
                {"$match": query_filter},
                {
                    "$group": {
                        "_id": None,
                        "total_bills_count": {"$sum": 1},
                        "total_purchase_sum": {"$sum": "$bill_amount"},
                        "total_points_sum": {"$sum": "$points"},
                    }
                },
            ]
        )
        totals_data = next(totals_data, {})

        # Create Plotly Graph
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=categories,
                y=total_points,
                name="Total Points",
                marker_color="royalblue",
            )
        )
        fig.add_trace(
            go.Bar(
                x=categories,
                y=total_purchase,
                name="Total Purchase",
                marker_color="lightgreen",
            )
        )
        fig.add_trace(
            go.Bar(
                x=categories, y=total_bills, name="Total Bills", marker_color="orange"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=categories,
                y=unique_customers,
                name="Unique Customers",
                mode="lines+markers",
                marker=dict(color="crimson"),
                line=dict(width=2),
            )
        )

        fig.update_layout(
            title=f"{report_type} wise Transactions Summary",
            xaxis=dict(title=report_type),
            yaxis=dict(title="Counts/Amounts"),
            barmode="group",
            legend=dict(title="Metrics"),
            template="plotly_white",
        )

        graph_html = fig.to_html(full_html=False)

        if report_type == "Month":
            for item in trans_data:
                if "category" in item:
                    year, month = item["category"].split("-")
                    item["category"] = (
                        f"{calendar.month_name[int(month)]} {year}"  # Convert YYYY-MM to Month Year
                    )

            # Sort by actual date order
            trans_data.sort(key=lambda x: datetime.strptime(x["category"], "%B %Y"))

        context = {
            "trans_data": trans_data,
            "graph_html": graph_html,
            "totals_data": totals_data,
            "report_types": ["Location", "City", "State", "Zone", "Month", "Tier"],
            "selected_report": report_type,
            "start_date": start_date,
            "end_date": end_date,
        }

        print("start_date-------------------------------------------", start_date)
        print("end_date-------------------------------------------", end_date)
        print("trans_data-------------------------------------------", trans_data)
        return render(request, "pages/forms/locationwisetranssummary.html", context)


class ExportTransactionSummary(View):
    def post(self, request):
        # Get filters from request
        brand_id = int(request.session.get("brand_id"))
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        report_type = request.POST.get("report_type", "Location")  # Default to Location
        print(
            "Start date----------------------------------------------------", start_date
        )
        print("end_date----------------------------------------------------", end_date)
        print(
            "report_type----------------------------------------------------",
            report_type,
        )

        # Execute query
        trans_data, query_filter = analytics_helpers.get_transaction_summary_data(
            start_date, end_date, brand_id, report_type, for_export=True
        )
        print("trans data----------------------------------------", trans_data)

        # Convert MongoDB result to DataFrame
        df = pd.DataFrame(trans_data)

        # Rename columns for better readability
        df.rename(
            columns={
                "_id": report_type,
                "total_bills": "Total Bills",
                "total_purchase": "Total Purchase",
                "total_earnpts": "Total Earn Points",
                "total_customers": "Total Customers",
            },
            inplace=True,
        )

        # Convert month format from 'YYYY-MM' to 'Month YYYY'
        if report_type == "Month":
            df[report_type] = df[report_type].apply(
                lambda x: f"{datetime.strptime(x, '%Y-%m').strftime('%B %Y')}"
            )

        # Calculate Totals
        total_row = {
            report_type: "Total",  # Label for total row
            "Total Bills": df["Total Bills"].sum(),
            "Total Purchase": round(df["Total Purchase"].sum(), 2),
            "Total Earn Points": df["Total Earn Points"].sum(),
            "Total Customers": df["Total Customers"].sum(),
        }

        # Append total row to DataFrame using pd.concat()
        df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

        # Convert DataFrame to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Transaction Summary", index=False)

        output.seek(0)
        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="transaction_summary_by_{report_type}.xlsx"'
        )

        return response


class FetchCustomerTransactionsSummaryDetails(View):
    def post(self, request):
        brand_id = int(request.session.get("brand_id"))
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        report_type = request.POST.get("report_type", "Location")
        category_value = request.POST.get("category")
        page = int(request.POST.get("page", 1))  # Get current page
        print(
            "Start date----------------------------------------------------", start_date
        )
        print("end_date----------------------------------------------------", end_date)
        print(
            "report_type----------------------------------------------------",
            report_type,
        )
        print(
            "category----------------------------------------------------",
            category_value,
        )
        print("page----------------------------------------------------", page)

        # Fetch paginated transactions using the common function
        transactions_data = analytics_helpers.get_customer_transactions_summary_details(
            brand_id, start_date, end_date, report_type, category_value, page, per_page
        )

        print("customer transac details", transactions_data)

        return JsonResponse(transactions_data)


class ExportCustomerTransactionsSummaryDetails(View):
    def get(self, request):
        brand_id = int(request.session.get("brand_id"))
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        report_type = request.GET.get("report_type", "Location")
        category_value = request.GET.get("category")
        page = int(request.GET.get("page", 1))  # Get current page
        print(
            "Start date----------------------------------------------------", start_date
        )
        print("end_date----------------------------------------------------", end_date)
        print(
            "report_type----------------------------------------------------",
            report_type,
        )
        print(
            "category----------------------------------------------------",
            category_value,
        )
        print("page----------------------------------------------------", page)

        # Fetch paginated transactions using the common function
        transactions_data = analytics_helpers.get_customer_transactions_summary_details(
            brand_id, start_date, end_date, report_type, category_value, page, per_page
        )
        transactions = transactions_data["data"]

        if not transactions:
            return HttpResponse("No data found for export.", content_type="text/plain")

        # Convert data to Pandas DataFrame
        df = pd.DataFrame(transactions)

        # Convert DataFrame to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Transaction Summary", index=False)

        output.seek(0)
        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="customer_transaction_details_by_{report_type}.xlsx"'
        )

        return response


class View_TransactionData(TemplateView):

    def get(self, request):

        transdata = (
            LoyaltyTrans.objects.select_related("location_id", "rwrd_brand_id")
            .all()
            .order_by("-created_on")
        )
        brand_id = request.session.get("brand_id")
        transdata = transdata.filter(
            status_flag=1, brand_id=brand_id, bill_trans_type="Earn"
        )

        total_transactions_count = transdata.count()

        total_transactions_Amt = transdata.aggregate(total=Sum("bill_amount"))["total"]

        total_earn_points = transdata.aggregate(total=Sum("points"))["total"]

        paginator = Paginator(transdata, per_page)
        page_no = request.GET.get("page")
        transdatafinal = paginator.get_page(page_no)
        totalpage = transdatafinal.paginator.num_pages
        if page_no is None or page_no == "":
            page_no = 1
        if totalpage > 1 and totalpage < 4:
            newpagelist = [1, 2, 3]
        else:
            newpagelist = [page_no, int(page_no) + 1, int(page_no) + 2]
        if int(totalpage) >= int(page_no) and int(totalpage) - 2 <= int(page_no):
            newpagelist = [int(totalpage) - 2, int(totalpage) - 1, int(totalpage)]

        locations = LocationMst.objects.all().order_by("location_Name")
        brands = RewardBrandsMst.objects.all().order_by("rwrd_brand_name")

        return render(
            request,
            "pages/forms/transactiondata.html",
            {
                "transdata": transdatafinal,
                "locations": locations,
                "brands": brands,
                "page_no": page_no,
                "totalpage": totalpage,
                "totalpagelist": [n + 1 for n in range(totalpage)],
                "newpagelist": newpagelist,
                "total_transactions_count": total_transactions_count,
                "total_transactions_Amt": total_transactions_Amt,
                "total_earn_points": total_earn_points,
            },
        )

    def post(self, request):

        transdata = (
            LoyaltyTrans.objects.select_related("location_id", "rwrd_brand_id")
            .all()
            .order_by("-created_on")
        )
        brand_id = request.session.get("brand_id")
        transdata = transdata.filter(
            status_flag=1, brand_id=brand_id, bill_trans_type="Earn"
        )

        locations = LocationMst.objects.all().order_by("location_Name")
        brands = RewardBrandsMst.objects.all().order_by("rwrd_brand_name")

        if request.method == "POST":
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")
            location_filter = request.POST.get("location")
            brand_filter = request.POST.get("brand")

            # Apply date filters if start_date and/or end_date are provided
            if start_date:
                try:
                    start_date = datetime.strptime(start_date, "%Y-%m-%d")
                    transdata = transdata.filter(created_on__gte=start_date)
                except ValueError:
                    pass  # Handle invalid date format

            if end_date:
                try:
                    end_date = datetime.strptime(end_date, "%Y-%m-%d")
                    end_date_with_time = datetime.combine(end_date, datetime.max.time())
                    transdata = transdata.filter(created_on__lte=end_date_with_time)
                except ValueError:
                    pass  # Handle invalid date format

            # Apply location filter if available
            if location_filter:
                transdata = transdata.filter(location_id=location_filter)

            # Apply brand filter if available
            if brand_filter:
                transdata = transdata.filter(rwrd_brand_id=brand_filter)

            total_transactions_count = transdata.count()

            total_transactions_Amt = transdata.aggregate(total=Sum("bill_amount"))[
                "total"
            ]

            total_earn_points = transdata.aggregate(total=Sum("points"))["total"]

            paginator = Paginator(transdata, per_page)
            page_no = request.GET.get("page")
            transdatafinal = paginator.get_page(page_no)
            totalpage = transdatafinal.paginator.num_pages
            if page_no is None or page_no == "":
                page_no = 1
            if totalpage > 1 and totalpage < 4:
                newpagelist = [1, 2, 3]
            else:
                newpagelist = [page_no, int(page_no) + 1, int(page_no) + 2]
            if int(totalpage) >= int(page_no) and int(totalpage) - 2 <= int(page_no):
                newpagelist = [int(totalpage) - 2, int(totalpage) - 1, int(totalpage)]

        return render(
            request,
            "pages/forms/transactiondata.html",
            {
                "transdata": transdatafinal,
                "locations": locations,
                "brands": brands,
                "selected_location": location_filter,
                "selected_brand": brand_filter,
                "start_date": start_date,
                "end_date": end_date,
                "page_no": page_no,
                "totalpage": totalpage,
                "totalpagelist": [n + 1 for n in range(totalpage)],
                "newpagelist": newpagelist,
                "total_transactions_count": total_transactions_count,
                "total_transactions_Amt": total_transactions_Amt,
                "total_earn_points": total_earn_points,
            },
        )


class View_RepeatTransbyLocSummary(TemplateView):
    template_name = "pages/forms/repeatpurchasebylocation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_report"] = self.request.GET.get("report_type", "Location")
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        if start_date:
            context["start_date"] = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            context["end_date"] = datetime.strptime(end_date, "%Y-%m-%d")

        context["report_types"] = ["Location", "City", "State", "Zone", "Month"]
        print(context)

        return context


class GetRepeatTransactionsSummaryData(View):
    def get(self, request):
        brand_id = int(request.session.get("brand_id"))
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        report_type = request.GET.get("report_type", "Location")
        print("start date---------------------------------------------", start_date)
        print("end date---------------------------------------------", end_date)
        print("report type---------------------------------------------", report_type)

        # Fetch repeat transaction summary
        result = analytics_helpers.get_repeat_transaction_summary(
            brand_id, start_date, end_date, report_type
        )
        print(result)

        for item in result:
             # Format month type correctly
             if report_type == "Month":
                 try:
                     year, month = item["category"].split("-")
                     item["category"] = f"{calendar.month_name[int(month)]} {year}"
                 except Exception as e:
                     print(f"Error formatting month category: {e}")
                     item["category"] = item["category"]  # Keep it as is if error occurs
 
             # Round off numerical values
             item["tot_purchase"] = round(item.get("tot_purchase", 0), 2)
             item["total_repeat_trans_amount"] = round(item.get("total_repeat_trans_amount", 0), 2)
             item["total_current_repeat_trans_amount"] = round(item.get("total_current_repeat_trans_amount", 0), 2)

        # Sort results
        result = sorted(result, key=lambda x: str(x["category"]))

        # Extract data for Plotly
        categories = [item["category"] for item in result]
        repeat_counts = [item.get("total_repeat_trans", 0) for item in result]

        # Generate unique colors for each bar
        colors = [
            "#" + "".join(random.choices("0123456789ABCDEF", k=6)) for _ in categories
        ]

        # Create the bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(x=categories, y=repeat_counts, marker=dict(color=colors)))

        fig.update_layout(
            title=f"Repeat Transactions by {report_type}",
            xaxis_title=report_type,
            yaxis_title="Repeat Transactions",
            template="plotly_white",
        )

        graph_html = fig.to_html(full_html=False)

        # Context for template
        return JsonResponse(
            {
                "graph_html": graph_html,
                "result": result,
            }
        )
    
    
class GetCustomerRepeatTransDetail(View):
    def get(self, request):
        brand_id = int(request.session.get("brand_id"))
        category = request.GET.get("category")
        report_type = request.GET.get("report_type")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        transaction_type = request.GET.get("transaction_type")
        page = int(request.GET.get("page", 1))

        response_data = analytics_helpers.fetch_customer_repeat_transaction_detail_data(
            brand_id,
            category,
            report_type,
            start_date,
            end_date,
            transaction_type,
            per_page,
            page,
        )
        print(response_data)

        return JsonResponse(response_data)
        

class ExportRepeatTransSummary(TemplateView):
    def get(self, request):
        brand_id = int(request.session.get("brand_id"))
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        report_type = request.GET.get("report_type", "Location")

        data = analytics_helpers.get_repeat_transaction_summary(
            brand_id, start_date, end_date, report_type
        )

        # Convert data to DataFrame
        df = pd.DataFrame(data)

        # Rename `_id` column to the selected report type for better readability
        if "_id" in df.columns:
            df.rename(columns={"_id": report_type}, inplace=True)

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="repeat_transactions_by_{report_type}.xlsx"'
        )

        with pd.ExcelWriter(response, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Repeat Transactions")

        return response
    
    
class ExportRepeatTransactionsDetails(View):
    def get(self, request):
        brand_id = int(request.session.get("brand_id"))
        category = request.GET.get("category")
        report_type = request.GET.get("report_type")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        transaction_type = request.GET.get("transaction_type")
        page = int(request.GET.get("page", 1))

        transactions_data = analytics_helpers.fetch_customer_repeat_transaction_detail_data(
            brand_id,
            category,
            report_type,
            start_date,
            end_date,
            transaction_type,
            per_page,
            page,
        )
        transactions = transactions_data["data"]

        if not transactions:
            return HttpResponse("No data found for export.", content_type="text/plain")

        # Convert data to Pandas DataFrame
        df = pd.DataFrame(transactions)

        # Convert DataFrame to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Transaction Summary", index=False)

        output.seek(0)
        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="repeat_transaction_details_by_{report_type}.xlsx"'
        )

        return response


class EarnBurnSummaryView(TemplateView):
    def get(self, request):
        brand_id = int(request.session.get("brand_id"))
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        report_type = request.GET.get("report_type", "Location")  # Default to Location

        result = analytics_helpers.get_earn_burn_summary(
            brand_id, start_date, end_date, report_type
        )

        # Extract data for visualization
        categories = [item["category"] for item in result]
        total_earn = [item["tot_earn"] for item in result]
        total_redeem = [item["tot_redeem"] for item in result]

        # Generate plotly chart
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=categories, y=total_earn, name="Total Earn", marker_color="royalblue"
            )
        )
        fig.add_trace(
            go.Bar(
                x=categories,
                y=total_redeem,
                name="Total Redeem",
                marker_color="lightgreen",
            )
        )
        fig.update_layout(
            title=f"{report_type} wise Earn and Redeem Points",
            xaxis=dict(title=report_type),
            yaxis=dict(title="Earn/Redeem"),
            barmode="group",
            legend=dict(title="Metrics"),
            template="plotly_white",
        )

        graph_html = fig.to_html(full_html=False)

        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        print(result)

        context = {
            "result": result,
            "graph_html": graph_html,
            "report_types": ["Location", "City", "State", "Zone", "Month"],
            "selected_report": report_type,
            "start_date": start_date,
            "end_date": end_date,
        }

        return render(request, "pages/forms/earnburnbylocation.html", context)

    # def post(self, request):
    #     brand_id = request.session.get("brand_id")

    #     sql_query = "with tt1 as (select * From tagnpayloyalty_locationmst where status_flag=1 and brand_id=%s), tt2 as (select location_id,round(sum(points),2) as earn_points from tagnpayloyalty_loyaltytrans where status_flag = 1 and brand_id=%s and bill_trans_type='Earn' group by location_id), tt3 as (select location_id,round(sum(points),2) as redeem_points from tagnpayloyalty_loyaltytrans where status_flag = 1 and brand_id=%s and bill_trans_type='Redeem' group by location_id) select tt1.location_id,tt1.location_name,ifnull(tt2.earn_points,0) as tot_earn,ifnull(tt3.redeem_points,0) as tot_redeem,(ifnull(tt2.earn_points,0)-ifnull(tt3.redeem_points,0)) as tot_liability from tt1 left outer join tt2 on tt1.location_id=tt2.location_id left outer join tt3 on tt1.location_id=tt3.location_id"
    #     params = [brand_id, brand_id, brand_id]

    #     with connection.cursor() as cursor:
    #         cursor.execute(sql_query, params)
    #         columns = [col[0] for col in cursor.description]
    #         rows = cursor.fetchall()

    #     # Process the results into a list of dictionaries
    #     result = [dict(zip(columns, row)) for row in rows]

    #     return render(
    #         request, "pages/forms/earnburnbylocation.html", {"result": result}
    #     )


class EarnBurnSummaryExportView(View):
    """Exports Earn & Burn Summary as an Excel file"""

    def post(self, request):
        brand_id = int(request.session.get("brand_id"))
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        report_type = request.POST.get("report_type", "Location")

        # Fetch summarized data from MongoDB
        result = analytics_helpers.get_earn_burn_summary(
            brand_id, start_date, end_date, report_type
        )

        if not result:
            return HttpResponse("No data found for export.", content_type="text/plain")

        # Convert data into Pandas DataFrame
        df = pd.DataFrame(result)

        # Create an in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Earn Burn Summary", index=False)

        # Prepare response
        output.seek(0)
        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="earn_burn_summary_by_{report_type}.xlsx"'
        )

        return response


class CustomerEarnBurnDetailsView(View):
    def post(self, request):
        brand_id = int(request.session.get("brand_id"))
        category = request.POST.get("category")
        report_type = request.POST.get("report_type")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        transaction_type = request.POST.get("transaction_type")  # "Earn" or "Redeem"
        page = int(request.POST.get("page", 1))

        response_data = analytics_helpers.get_customer_earn_burn_details(
            brand_id,
            category,
            report_type,
            start_date,
            end_date,
            transaction_type,
            per_page,
            page,
        )
        print(response_data)

        return JsonResponse(response_data)


class ExportCustomerEarnBurnDetailsView(View):
    def get(self, request):
        brand_id = int(request.session.get("brand_id"))
        category = request.GET.get("category")
        report_type = request.GET.get("report_type")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        transaction_type = request.GET.get("transaction_type")  # "Earn" or "Redeem"
        page = int(request.GET.get("page", 1))

        transactions_data = analytics_helpers.get_customer_earn_burn_details(
            brand_id,
            category,
            report_type,
            start_date,
            end_date,
            transaction_type,
            per_page,
            page,
        )
        transactions = transactions_data["data"]

        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        if not df.empty:
            df["bill_date"] = pd.to_datetime(df["bill_date"]).dt.strftime("%d-%b-%Y")
            df.rename(
                columns={
                    "mobileno": "Mobile No",
                    "bill_number": "Bill Number",
                    "bill_date": "Bill Date",
                    "points": f"{transaction_type} Points",
                    "bill_status": "Bill Status",
                },
                inplace=True,
            )

        # Create in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Earn Burn Summary", index=False)

        # Prepare response
        output.seek(0)
        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="customer_earn_burn_detail_by_{report_type}.xlsx"'
        )
        return response


class CampaignROIView(TemplateView):
    def get(self, request):
        brand_id = request.session.get("brand_id")
        return render(request, "pages/forms/campaignROI.html")


class RepeatCustomersGraphView(View):
    def get(self, request):
        brand_id = int(request.session.get("brand_id"))
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        repeat_customers_data = analytics_helpers.get_repeat_customers_data(
            brand_id, start_date, end_date
        )

        # Extract data for the graph
        locations = [item["location_Name"] for item in repeat_customers_data]
        repeat_counts = [item["repeat_customers"] for item in repeat_customers_data]
        colors = [
            "hsl(" + str(i * 30 % 360) + ", 70%, 50%)" for i in range(len(locations))
        ]  # Generate different colors

        # Create Plotly Graph
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=locations,
                y=repeat_counts,
                marker=dict(color=colors),
                name="Repeat Customers",
            )
        )

        fig.update_layout(
            title="Repeat Customers per Location",
            xaxis=dict(title="Location"),
            yaxis=dict(title="Number of Repeat Customers"),
            template="plotly_white",
        )

        graph_html = fig.to_html(full_html=False)

        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        context = {
            "graph_html": graph_html,
            "repeat_customers_data": repeat_customers_data,
            "start_date": start_date,
            "end_date": end_date,
        }

        return render(request, "pages/forms/analyticsRepeatCustomers.html", context)


class ExportRepeatCustomersView(View):
    def post(self, request):
        brand_id = int(request.session.get("brand_id"))
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        repeat_customers_data = analytics_helpers.get_repeat_customers_data(
            brand_id, start_date, end_date
        )

        # Convert to DataFrame
        df = pd.DataFrame(repeat_customers_data)
        if not df.empty:
            df.rename(
                columns={
                    "location_Name": "Location",
                    "repeat_customers": "Repeat Customers",
                },
                inplace=True,
            )
            df = df[["Location", "Repeat Customers"]]  # Reorder columns

        # Create in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Repeat Customers", index=False)

        # Prepare response
        output.seek(0)
        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            'attachment; filename="repeat_customers_by_location.xlsx"'
        )
        return response


# View to return paginated repeat customer details for modal
class RepeatCustomerDetailView(View):
    def get(self, request):
        brand_id = int(request.session.get("brand_id"))
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        location_name = request.GET.get("category")  # Category = Location Name
        page = int(request.GET.get("page", 1))  # Default page = 1

        # Fetch paginated data
        response_data = analytics_helpers.get_repeat_customer_details(
            brand_id, start_date, end_date, location_name, per_page, page
        )

        return JsonResponse(response_data)


# View to export paginated repeat customer details
class ExportRepeatCustomerDetailsView(View):
    def get(self, request):
        brand_id = int(request.session.get("brand_id"))
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        location_name = request.GET.get("category")
        page = int(request.GET.get("page", 1))

        # Fetch only paginated data
        response_data = analytics_helpers.get_repeat_customer_details(
            brand_id, start_date, end_date, location_name, per_page, page
        )
        transactions = response_data["data"]

        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        if not df.empty:
            df.rename(
                columns={"Mobile No": "Mobile Number"}, inplace=True
            )  # Rename for consistency
            df = df[
                [
                    "Mobile Number",
                    "Bill Number",
                    "Bill Date",
                    "Bill Amount",
                    "Bill Status",
                ]
            ]  # Ensure correct order

        # Create in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Repeat Customers", index=False)

        # Prepare response
        output.seek(0)
        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="repeat_customers_{location_name}.xlsx"'
        )
        return response


class TopCustomersGraphView(View):
    def get(self, request):
        brand_id = int(request.session.get("brand_id"))
        report_type = request.GET.get("report_type", "visit")  # 'visit' or 'purchase'

        # Fetch data
        top_customers = analytics_helpers.get_top_customers(brand_id, report_type)

        # ✅ Update keys to match the new function output
        mobile_numbers = [item["mobile_no"] for item in top_customers]
        values = [
            item["total_visits"] if report_type == "visit" else item["total_purchase"]
            for item in top_customers
        ]
        colors = [
            "hsl(" + str(i * 40 % 360) + ", 70%, 50%)"
            for i in range(len(mobile_numbers))
        ]  # Dynamic colors

        # Create Plotly Graph
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=mobile_numbers,
                y=values,
                marker=dict(color=colors),
                name="Top Customers",
            )
        )

        fig.update_layout(
            title="Top 10 Customers by "
            + ("Visits" if report_type == "visit" else "Purchase"),
            xaxis=dict(title="Customer Mobile Number"),
            yaxis=dict(
                title="Total "
                + ("Visits" if report_type == "visit" else "Purchase Amount")
            ),
            template="plotly_white",
        )

        graph_html = fig.to_html(full_html=False)
        print("top_customers----------------------------", top_customers)

        context = {
            "graph_html": graph_html,
            "top_customers_data": top_customers,
            "report_type": report_type,
            "report_types": ["visit", "purchase"],
        }

        return render(request, "pages/forms/analyticsTopCustomers.html", context)


class LiveMonitorView(TemplateView):
    template_name = "pages/forms/live_monitor.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brandid = int(self.request.session.get("brand_id"))

        context["zones"] = ZoneMst.objects.filter(status_flag=1).values(
            "zone_id", "zone_name"
        )

        zoneID = self.request.GET.get("zone")

        if zoneID:
            context["locations"] = LocationMst.objects.filter(
                brand_id=brandid, status_flag=1, location_zone=int(zoneID)
            ).values("location_code", "location_Name")
        else:
            context["locations"] = LocationMst.objects.filter(
                brand_id=brandid, status_flag=1
            ).values("location_code", "location_Name")

        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        if start_date:
            context["start_date"] = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            context["end_date"] = datetime.strptime(end_date, "%Y-%m-%d")

        context["selected_location"] = self.request.GET.get("location")
        context["selected_zone"] = zoneID
        print(context)

        return context


def get_live_monitor_total_Data(request):
    brandid = int(request.session.get("brand_id"))
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    location_code = request.GET.get("location")
    zoneID = request.GET.get("zone")
    try:
        # Get current month's first date
        todays_date = datetime.today()
        # Set start_date_param to today's date at 00:00:00 (midnight)
        if start_date:
            start_date_param = f"{start_date} 00:00:00"  # Start of the day
        else:
            start_date_param = todays_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        # Set end_date_param to today's date at 23:59:59 (max time)
        if end_date:
            end_date_param = f"{end_date} 23:59:59"
        else:
            end_date_param = end_date or todays_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

        locations = LocationMst.objects.filter(brand_id=brandid, status_flag=1)

        # Apply zone filter if zoneID is provided
        if zoneID:
            locations = locations.filter(location_zone=int(zoneID))

        # Getting the live stores
        total_live_stores = len(list(locations))

        # Calculate total burn points where bill_trans_type is "Redeem"
        total_burn_points = (
            LoyaltyTrans.objects.filter(
                brand_id=brandid,
                bill_trans_type="Redeem",
                bill_date__gte=start_date_param,
                bill_date__lte=end_date_param,
            ).aggregate(total_burn_points=Sum("points"))["total_burn_points"]
            or 0
        )

        # Get distinct bills
        distinct_bills = (
            BillingTrans.objects.values(
                "location_code", "bill_number", "bill_date", "bill_status"
            )
            .filter(
                brand_id=brandid,
                bill_date__gte=start_date_param,
                bill_date__lte=end_date_param,
            )
            .distinct()
        )

        # Calculate total purchase and total bills
        total_aggregation = distinct_bills.aggregate(
            total_purchase=Sum("bill_amt_with_tax"),
            total_bills=Count("bill_number", distinct=True),
        )
        total_purchase = total_aggregation["total_purchase"] or 0  # Handle None case
        total_bills = total_aggregation["total_bills"] or 0

        # Calculating the loyalty bills and loyalty sale
        transactions = LoyaltyTrans.objects.filter(
            brand_id=brandid,
            bill_trans_type="Earn",
            bill_date__gte=start_date_param,
            bill_date__lte=end_date_param,
        )
        total_loyalty_sale = round(
            transactions.aggregate(total_loyalty_sale=Sum("bill_amount"))[
                "total_loyalty_sale"
            ]
            or 0,
            2,
        )
        total_loyalty_bill = transactions.count()

        # Calculating the data received
        total_data_received = (
            BillingTrans.objects.filter(brand_id=brandid)
            .values("location_code")
            .distinct()
            .count()
        )

        # Calculating the repeat bills
        sql_query = """
                WITH customer_purchases AS (
                    SELECT 
                        bt.mobileno,
                        bt.location_code,
                        CASE 
                            WHEN EXISTS (
                                SELECT 1 
                                FROM tagnpayloyalty.tagnpayloyalty_billingtrans bt2 
                                WHERE bt2.mobileno = bt.mobileno 
                                  AND bt2.brand_id = bt.brand_id 
                                  AND bt2.bill_date < %s
                            ) THEN 'Repeated'
                            WHEN COUNT(bt.mobileno) > 1 THEN 'Repeated'
                            ELSE 'New'
                        END AS customer_type
                    FROM tagnpayloyalty.tagnpayloyalty_billingtrans bt
                    WHERE bt.brand_id = %s
                      AND bt.bill_date BETWEEN %s AND %s
                      {location_filter}
                    GROUP BY bt.mobileno, bt.location_code
                )
                SELECT
                    COUNT(CASE WHEN customer_type = 'Repeated' THEN 1 END) AS repeated_customers
                FROM customer_purchases;
            """

        params = [start_date_param, brandid, start_date_param, end_date_param]
        location_filter = ""

        if location_code:
            location_filter = "AND bt.location_code = %s"
            params.append(location_code)

        # Format the SQL query with the filters
        sql_query = sql_query.format(location_filter=location_filter)

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            result = cursor.fetchone()  # Fetch the first row of results

        total_repeat_bills = result[0]

        return JsonResponse(
            {
                "total_purchase": total_purchase,
                "total_bills": total_bills,
                "total_burn_points": total_burn_points,
                "total_live_stores": total_live_stores,
                "total_loyalty_sale": total_loyalty_sale,
                "total_loyalty_bill": total_loyalty_bill,
                "total_data_received": total_data_received,
                "total_repeat_bills": total_repeat_bills,
            }
        )
    except Exception as e:
        print(f"ERROR in getting LIVE MONITOR DATA {e}")
        return JsonResponse({})


def get_live_monitor_table_data(request):
    brand_id = int(request.session.get("brand_id"))
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    location_code = request.GET.get("location")
    page = int(request.GET.get("page", 1))

    try:
        # Get current month's first date
        todays_date = datetime.today()
        # Set start_date_param to today's date at 00:00:00 (midnight)
        if start_date:
            start_date_param = f"{start_date} 00:00:00"  # Start of the day
        else:
            start_date_param = todays_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        # Set end_date_param to today's date at 23:59:59 (max time)
        if end_date:
            end_date_param = f"{end_date} 23:59:59"
        else:
            end_date_param = end_date or todays_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

        sql_query = """
            WITH customer_purchases AS (
                SELECT 
                    bt.mobileno,
                    bt.location_code,
                    MAX(bt.location_name) AS location_name,
                    MAX(bt.customer_fname || ' ' || bt.customer_lname) AS customer,
                    MAX(bt.bill_date) AS bill_date,
                    MAX(bt.bill_number) AS bill_number,
                    SUM(bt.bill_amt_with_tax) AS net_amount,
                    CASE 
                        WHEN EXISTS (
                            SELECT 1 
                            FROM tagnpayloyalty.tagnpayloyalty_billingtrans bt2 
                            WHERE bt2.mobileno = bt.mobileno 
                              AND bt2.brand_id = bt.brand_id 
                              AND bt2.bill_date < %s
                        ) THEN 'Repeated'
                        WHEN COUNT(bt.mobileno) > 1 THEN 'Repeated'
                        ELSE 'New'
                    END AS customer_type
                FROM tagnpayloyalty.tagnpayloyalty_billingtrans bt
                WHERE bt.brand_id = %s 
                    AND bt.bill_date >= %s
                    AND bt.bill_date <= %s
                    {location_filter}
                GROUP BY bt.mobileno, bt.location_code
            )
            SELECT  
                c.mobileno,  
                c.location_code AS store_code,  
                COALESCE(c.location_name, '') AS store_name,  
                c.bill_date,  
                c.net_amount,  
                c.customer,  
                c.customer_type,
                c.bill_number
            FROM customer_purchases c
            ORDER BY c.bill_date DESC;
        """

        params = [start_date_param, brand_id, start_date_param, end_date_param]
        location_filter = ""

        if location_code:
            location_filter = "AND bt.location_code = %s"
            params.append(location_code)

        # Format the SQL query with the filters
        sql_query = sql_query.format(location_filter=location_filter)

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        result = []

        for row in rows:
            data = dict(zip(columns, row))
            mobile_status = mobile_number_validation(str(data["mobileno"]), brand_id)

            # If the mobile number validation fails, mark customer as "Lost"
            if mobile_status:
                data["customer_type"] = "Lost"

            result.append(
                {
                    "customer_type": data["customer_type"],
                    "store_code": data["store_code"],
                    "store_name": data["store_name"],
                    "bill_date": data["bill_date"],
                    "bill_number": data["bill_number"],
                    "net_amount": data["net_amount"],
                    "customer": data["customer"],
                    "mobileno": data["mobileno"],
                }
            )

        # Paginate results
        paginator = Paginator(result, per_page)
        paginated_data = paginator.get_page(page)
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

        return JsonResponse(
            {
                "data": list(paginated_data),
                "page_no": page,
                "total_pages": paginator.num_pages,
                "has_previous": paginated_data.has_previous(),
                "has_next": paginated_data.has_next(),
                "new_page_list": new_page_list,
            }
        )
    except Exception as e:
        print(f"Error in getting live monitor table data. Error: {e}")
        return JsonResponse({})


def get_locations_by_zone(request):
    zone_id = request.GET.get("zone_id")
    brand_id = int(request.session.get("brand_id"))

    if zone_id:
        locations = LocationMst.objects.filter(
            brand_id=brand_id, location_zone=int(zone_id), status_flag=1
        ).values("location_code", "location_Name")
        return JsonResponse({"locations": list(locations)})
    return JsonResponse({"locations": []})
