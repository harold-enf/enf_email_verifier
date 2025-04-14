import streamlit as st
import requests
from closeio_api import Client
import streamlit as st

ev_api = st.secrets["email_verified_url"]


class EmailValidator:
    def email_validator(self, email):
        try:
            # Replace this with your actual API URL pattern
            url = ev_api.replace("EMAIL_TO_VALIDATE", email)
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()  # assuming the response is in JSON
                return True, data  # return the actual data if successful
            else:
                return (
                    False,
                    f"API returned status code {response.status_code}: {response.text}",
                )

        except Exception as e:
            return False, str(e)
