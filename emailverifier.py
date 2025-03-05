import re
import dns.resolver
import requests
import smtplib
from email_validator import validate_email, EmailNotValidError
from disposable_email_domains import blocklist


class EmailValidator:
    KNOWN_PROVIDERS_URL = "https://gist.githubusercontent.com/ammarshah/f5c2624d767f91a7cbdc4e54db8dd0bf/raw/660fd949eba09c0b86574d9d3aa0f2137161fc7c/all_email_provider_domains.txt"

    def __init__(self):
        self.known_providers = self.fetch_known_providers()

    def fetch_known_providers(self):
        try:
            response = requests.get(self.KNOWN_PROVIDERS_URL, timeout=5)
            if response.status_code == 200:
                return set(response.text.splitlines())
        except requests.RequestException as e:
            print(f"Error fetching known providers: {e}")
        return {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"}

    def get_domain(self, email):
        return email.split("@")[1].lower()

    def is_valid_email(self, email):
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False

    def is_disposable(self, email):
        return self.get_domain(email) in blocklist

    def get_mx_records(self, domain):
        try:
            return dns.resolver.resolve(domain, "MX")
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
            return None

    def has_mx_record(self, domain):
        return self.get_mx_records(domain) is not None

    def smtp_validate(self, email):
        domain = self.get_domain(email)

        SKIP_PROVIDERS = self.known_providers
        if domain in SKIP_PROVIDERS:
            return "Valid (Provider blocks verification)"

        mx_records = self.get_mx_records(domain)
        if not mx_records:
            return "No MX record found"

        mx_host = str(mx_records[0].exchange).strip(".")

        try:
            server = smtplib.SMTP(mx_host, 25, timeout=10)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.mail("no-reply@enfinity.com")

            code, _ = server.rcpt(email)
            server.quit()
            return "Email is Valid" if code == 250 else "Email does not exist"
        except smtplib.SMTPResponseException as e:
            return f"SMTP error: {e.smtp_code} - {e.smtp_error.decode()}"
        except smtplib.SMTPConnectError:
            return "Unable to connect to mail server"
        except smtplib.SMTPServerDisconnected:
            return "Mail server disconnected unexpectedly"
        except Exception as e:
            return f"SMTP validation failed: {str(e)}"

    def verify_email(self, email):
        try:
            if not self.is_valid_email(email):
                return "Invalid email format"

            domain = self.get_domain(email)
            if self.is_disposable(email):
                return "Disposable email detected"

            if not self.has_mx_record(domain):
                return "No MX Record found"

            return self.smtp_validate(email)
        except Exception as e:
            return f"Unexpected error: {str(e)}"
