import pandas as pd
import json
from typing import List, Optional

REQUIRED_FIELDS = ["type", "amount", "source", "category"]
VALID_TYPES = ["income", "expense"]
VALID_CATEGORIES = ["freelance", "subscription", "tool", "personal", "other"]

def validate_transactions(transactions: List[dict]) -> tuple[bool, str, List[dict]]:
    """
    Validates transaction list.
    Returns: (is_valid, error_message, cleaned_transactions)
    """
    if not transactions:
        return False, "No transactions found in the data.", []

    cleaned = []
    for i, t in enumerate(transactions):
        # Check required fields
        missing = [f for f in REQUIRED_FIELDS if f not in t or t[f] == ""]
        if missing:
            return False, f"Row {i+1} is missing: {', '.join(missing)}", []

        # Validate type
        if str(t["type"]).lower() not in VALID_TYPES:
            return False, f"Row {i+1}: type must be 'income' or 'expense', got '{t['type']}'", []

        # Validate amount
        try:
            amount = float(t["amount"])
            if amount <= 0:
                return False, f"Row {i+1}: amount must be greater than 0", []
        except (ValueError, TypeError):
            return False, f"Row {i+1}: amount must be a number, got '{t['amount']}'", []

        # Build clean transaction
        cleaned.append({
            "id":         t.get("id", f"t{i+1:02d}"),
            "type":       str(t["type"]).lower(),
            "amount":     float(t["amount"]),
            "source":     str(t["source"]),
            "category":   str(t["category"]).lower(),
            "usage_days": int(t.get("usage_days", 0))
        })

    return True, "Valid", cleaned


def parse_csv(file) -> tuple[bool, str, List[dict]]:
    """Parse uploaded CSV file."""
    try:
        df = pd.read_csv(file)
        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()
        transactions = df.to_dict(orient="records")
        return validate_transactions(transactions)
    except Exception as e:
        return False, f"CSV parsing failed: {str(e)}", []


def parse_json(file) -> tuple[bool, str, List[dict]]:
    """Parse uploaded JSON file."""
    try:
        content = file.read()
        data = json.loads(content)
        # Handle both list and dict with transactions key
        if isinstance(data, list):
            transactions = data
        elif isinstance(data, dict) and "transactions" in data:
            transactions = data["transactions"]
        else:
            return False, "JSON must be a list of transactions or {\"transactions\": [...]}", []
        return validate_transactions(transactions)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {str(e)}", []
    except Exception as e:
        return False, f"JSON parsing failed: {str(e)}", []


def parse_manual(rows: List[dict]) -> tuple[bool, str, List[dict]]:
    """Parse manually entered rows from form."""
    return validate_transactions(rows)


def get_summary(transactions: List[dict]) -> dict:
    """Quick summary for display before running GUARDIAN."""
    income = sum(t["amount"] for t in transactions if t["type"] == "income")
    expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
    subs = [t for t in transactions if t["category"] == "subscription"]
    return {
        "total_transactions": len(transactions),
        "total_income":       income,
        "total_expenses":     expenses,
        "net_position":       income - expenses,
        "subscription_count": len(subs),
        "subscription_total": sum(s["amount"] for s in subs)
    }
