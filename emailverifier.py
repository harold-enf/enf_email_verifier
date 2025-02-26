import streamlit as st
import re
import dns.resolver
import requests
from disposable_email_domains import blocklist
from email_validator import validate_email, EmailNotValidError
import smtplib


class EmailValidator:
    EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    KNOWN_PROVIDERS_URL = "https://gist.githubusercontent.com/ammarshah/f5c2624d767f91a7cbdc4e54db8dd0bf/raw/660fd949eba09c0b86574d9d3aa0f2137161fc7c/all_email_provider_domains.txt"

    def __init__(self):
        self.known_providers = self.fetch_known_providers()

    def fetch_known_providers(self):
        try:
            response = requests.get(self.KNOWN_PROVIDERS_URL, timeout=10)
            if response.status_code == 200:
                return set(response.text.splitlines())
        except requests.RequestException:
            pass
        return {
            "gmail.com",
            "yahoo.com",
            "outlook.com",
            "hotmail.com",
            "icloud.com",
        }  # Default fallback

    def is_valid_email(self, email):
        return re.match(self.EMAIL_REGEX, email) is not None

    def get_domain(self, email):
        return email.split("@")[1].lower()

    def is_disposable(self, email):
        return self.get_domain(email) in blocklist

    def has_mx_record(self, domain):
        try:
            answers = dns.resolver.resolve(domain, "MX")
            return len(answers) > 0
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
            return False

    def smtp_validate(self, email):
        domain = self.get_domain(email)

        # Skip SMTP validation for known email providers that block verification
        SKIP_PROVIDERS = {
            "gmail.com",
            "yahoo.com",
            "outlook.com",
            "hotmail.com",
            "icloud.com",
        }
        if domain in SKIP_PROVIDERS:
            return "Valid (Provider blocks verification)"

        try:
            mx_records = dns.resolver.resolve(domain, "MX")
            mx_host = str(mx_records[0].exchange).strip(".")
        except dns.resolver.NoAnswer:
            return "No MX record found"
        except dns.resolver.NXDOMAIN:
            return "Domain does not exist"
        except Exception as e:
            return f"DNS lookup failed: {str(e)}"

        try:
            server = smtplib.SMTP(mx_host, 25, timeout=10)
            server.helo()
            server.mail("no-reply@enfinity.com")

            # Check the actual email
            code, _ = server.rcpt(email)

            # Perform multiple random email checks for catch-all detection
            catch_all_detected = True
            for i in range(3):
                random_email = f"random{i}@{domain}"
                catch_all_code, _ = server.rcpt(random_email)
                if catch_all_code != 250:
                    catch_all_detected = False
                    break  # If any random email gets rejected, it's NOT a catch-all

            server.quit()

            if catch_all_detected:
                return "Catch-all domain detected"

            return "Email is Valid" if code == 250 else "Email does not exist"
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

            smtp_result = self.smtp_validate(email)
            if smtp_result:
                return smtp_result

            email_info = validate_email(email, check_deliverability=True)
            if email_info:
                return "Email is Valid and has an active mail server"

        except EmailNotValidError as e:
            return f"{str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
