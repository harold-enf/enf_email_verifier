# Email Verifier App

## Overview
The **Email Verifier App** is a simple tool built using Streamlit that allows users to verify multiple email addresses. It checks the validity of email addresses based on several criteria, including format correctness, disposable email detection, and the presence of an MX record for the domain.

## Features
- **Bulk Email Verification**: Enter multiple email addresses at once.
- **Email Format Validation**: Ensures the email follows a valid pattern.
- **Disposable Email Detection**: Identifies if the email is from a temporary or disposable provider.
- **MX Record Lookup**: Verifies whether the email domain has an MX record.
- **Categorized Results**: Emails are categorized as Valid, Invalid, Catch-all, Disposable, or Error with colored labels.

## Installation
### Prerequisites
- Python 3.8+
- pip

### Install Dependencies
```sh
pip install streamlit pandas emailverifier
```

## Usage
Run the application with the following command:
```sh
streamlit run app.py
```

### Steps to Use
1. Open the app in your browser.
2. Enter email addresses in the text area, one per line.
3. Click the **Verify Emails** button.
4. View verification results in a table with categorized statuses.

## Result Categories
| Status      | Meaning |
|------------|---------|
| ✅ Valid   | The email is valid and can receive messages. |
| ⚠️ Error   | There was an issue verifying the email. |
| ⚠️ Catch-all | The domain accepts all emails, so validity cannot be determined. |
| ⚠️ Disposable | The email is from a disposable provider. |
| ❌ Invalid | The email format is incorrect or domain has no MX record. |

## License
This project is licensed under the MIT License.

