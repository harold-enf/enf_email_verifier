from closeio_api import Client
from datetime import datetime, timedelta
import streamlit as st
import pytz

api = Client(st.secrets["close_api_key"])


def get_latest_email(lead_id):
    response = api.get(
        "activity/email/",
        params={
            "lead_id": lead_id,
            "sort": "-date_created",
            "limit": 1,  # Get the most recent email only
        },
    )
    if response["data"]:
        latest_email = response["data"][0]
        utc_dt = datetime.fromisoformat(latest_email.get("date_created"))
        sg_ph_tz = pytz.timezone("Asia/Singapore")
        sg_ph_time = utc_dt.astimezone(sg_ph_tz)
        formatted_date = sg_ph_time.strftime("%Y-%m-%d")
        return f"{formatted_date}"
    return "Not Contacted"


def get_close_data(email):
    query = {
        "negate": False,
        "queries": [
            {"negate": False, "object_type": "lead", "type": "object_type"},
            {
                "mode": "beginning_of_words",
                "negate": False,
                "type": "text",
                "value": email,
            },
        ],
        "type": "and",
    }

    lead_results = api.post(
        "data/search/",
        data={
            "limit": None,
            "query": query,
            "results_limit": None,
            "sort": [
                {
                    "direction": "asc",
                    "field": {
                        "field_name": "num_emails",
                        "object_type": "lead",
                        "type": "regular_field",
                    },
                }
            ],
        },
    )

    if len(lead_results["data"]) == 0:
        return "Not Contacted"

    else:
        lead_id = lead_results["data"][0]["id"]
        date_last_email = get_latest_email(lead_id)
        return date_last_email
