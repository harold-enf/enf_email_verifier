import streamlit as st
import pandas as pd
from emailverifier import EmailValidator
from closeio import get_close_data

st.title("Email Verifier App")

st.write(
    "This is a simple email verification tool. Enter multiple email addresses below, one per line, to check their validity."
    " The app will check if each email format is correct, whether it's from a disposable provider,"
    " and whether its domain has an MX record."
)

email_input = st.text_area("Enter Email Addresses (one per line):")


def get_result_style(result):
    if "Valid" in result:
        return f'<span style="background-color: green; color: white; padding: 5px; border-radius: 5px;">{result}</span>'
    elif "Error" in result or "Catch-all" in result or "Disposable" in result:
        return f'<span style="background-color: orange; color: white; padding: 5px; border-radius: 5px;">{result}</span>'
    else:
        return f'<span style="background-color: red; color: white; padding: 5px; border-radius: 5px;">{result}</span>'


if st.button("Verify Emails"):
    validator = EmailValidator()
    emails = email_input.splitlines()
    results = []
    progress_bar = st.progress(0)

    for index, email in enumerate(emails, start=1):
        progress_bar.progress(index / len(emails))
        if email.strip():
            diagnosis = validator.verify_email(email)
            contacted = get_close_data(email)
            if "Valid" in diagnosis:
                result = "Valid"
            elif "Error" in diagnosis:
                result = "Error"
            elif "Catch-all" in diagnosis:
                result = "Catch-all"
            elif "Disposable" in diagnosis:
                result = "Disposable"
            else:
                result = "Invalid"

            styled_result = get_result_style(result)
            results.append((email, styled_result, diagnosis, contacted))

    df = pd.DataFrame(
        results, columns=["Email Address", "Result", "Diagnosis", "Contacted Date"]
    )
    st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.warning("Please enter at least one email address.")
