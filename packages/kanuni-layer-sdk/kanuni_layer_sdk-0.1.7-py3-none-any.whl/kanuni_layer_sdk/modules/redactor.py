from pathlib import Path
import json
import string
import re
from importlib.resources import files, as_file


def redactor(prompt: str, opted_in: bool) -> str:
    """
    Extract sensitive information from the prompt and replace with pre-determined phrases.

    Args:
        prompt: The prompt to redact.
        opted_in: Whether the user has opted in to redaction.

    """

    if not opted_in:
        return prompt

    pii_redacted_prompt = pii_redactor(prompt)
    pwd_redacted_prompt = pwd_redactor(pii_redacted_prompt)
    return pwd_redacted_prompt


def pii_redactor(prompt: str) -> str:
    """
    Redacts personally identifiable information (PII) from the given prompt string.
    Full names
    * Email addresses
    * Phone numbers
    * Physical addresses
    National ID numbers (e.g., SSN, passport)
    * Credit card numbers
    Bank account numbers
    * Date of birth
    * IP addresses
    Usernames

    """

    # Detect and redact email addresses
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    redacted = re.sub(email_pattern, "[REDACTED_EMAIL]", prompt)

    # Detect and redact phone numbers (simple patterns)
    phone_pattern = (
        r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}"
    )
    redacted = re.sub(phone_pattern, "[REDACTED_PHONE]", redacted)

    # Detect and redact credit card numbers (Visa, MasterCard, UnionPay, etc.)
    # Visa: 4xxx..., MasterCard: 51-55xxx..., UnionPay: 62xxx..., 13-19 digits
    # Detect and redact credit card numbers (Visa, MasterCard, UnionPay, American Express, etc.)
    cc_patterns = [
        r"\b4[0-9]{12}(?:[0-9]{3})?\b",  # Visa
        r"\b5[1-5][0-9]{14}\b",  # MasterCard
        r"\b62[0-9]{14,17}\b",  # UnionPay
        r"\b3[47][0-9]{13}\b",  # American Express
        r"\b(?:\d[ -]*?){13,19}\b",  # General pattern
    ]

    for pattern in cc_patterns:
        redacted = re.sub(pattern, "[REDACTED_CREDIT_CARD]", redacted)

    # Detect and redact passport numbers (generic pattern: 6-9 alphanumeric characters)
    passport_pattern = r"\b([A-Z0-9]{6,9})\b"
    redacted = re.sub(passport_pattern, "[REDACTED_PASSPORT]", redacted)

    # Detect and redact IPv4 addresses
    ipv4_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    redacted = re.sub(ipv4_pattern, "[REDACTED_IP]", redacted)

    # Detect and redact IPv6 addresses
    ipv6_pattern = r"\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b"
    redacted = re.sub(ipv6_pattern, "[REDACTED_IP]", redacted)

    # Detect and redact date of births (common formats)
    dob_patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",  # 2025-09-16
        r"\b\d{2}/\d{2}/\d{4}\b",  # 16/09/2025 or 09/16/2025
        r"\b\d{2}-\d{2}-\d{4}\b",  # 16-09-2025 or 09-16-2025
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}\b",  # September 16, 2025
    ]
    for pattern in dob_patterns:
        redacted = re.sub(pattern, "[REDACTED_DOB]", redacted)

    # Detect and redact physical addresses (simple pattern: number + street + optional city/state/zip)
    address_pattern = r"\b\d{1,5}\s+[A-Za-z0-9\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Square|Sq|Plaza|Plz|Circle|Cir)\b"
    redacted = re.sub(address_pattern, "[REDACTED_ADDRESS]", redacted)

    return redacted


def pwd_redactor(prompt: str) -> str:
    try:
        # split on any ASCII punctuation or whitespace characters
        # tokenize into words and keep punctuation as their own items
        pattern = rf"\w+|[{re.escape(string.punctuation)}]+"
        words: list[str] = re.findall(pattern, prompt)
        redacted_prompt: list[str] = []

        disabilities: dict[str, list[str]] = {}
        disability_lookup: dict[str, str] = {}

        # Use importlib.resources so this works when installed from a wheel
        with as_file(files("kanuni_layer_sdk").joinpath("assets", "disabilities.json")) as disabilities_path:
            with disabilities_path.open("r", encoding="utf-8") as fh:
                disabilities = json.load(fh)
                disability_lookup = {
                    term.lower(): category
                    for category, terms in disabilities.items()
                    for term in terms
                }

        for word in words:
            if word.lower() in disability_lookup.keys():
                category = disability_lookup[word.lower()]
                redacted_prompt.append(
                    f"[{category.replace('-', ' ')} redacted]"
                )
            else:
                redacted_prompt.append(word)

        return " ".join(redacted_prompt)

    except (FileNotFoundError, json.JSONDecodeError):
        raise FileNotFoundError("Could not find or read disabilities.json")
