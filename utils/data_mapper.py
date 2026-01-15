"""
Data Mapper for CFP Fields
Maps scraped data from cityfinance.in to Excel CFP field structure.
"""

from typing import Dict, List, Tuple, Optional

# Mapping from scraped field names to Excel row numbers and field names
# Based on Data Input sheet structure (rows 39-91)

CFP_FIELD_MAPPING = {
    # Revenue Income Fields
    'revenue_income': {
        'tax_revenue': {
            'row': 43,
            'excel_name': 'Tax Revenue',
            'unit': 'Lakhs'
        },
        'assigned_revenue': {
            'row': 44,
            'excel_name': 'Assigned Revenues & Compensation',
            'unit': 'Lakhs'
        },
        'rental_income': {
            'row': 45,
            'excel_name': 'Rental Income from Municipal Properties',
            'unit': 'Lakhs'
        },
        'fees_user_charges': {
            'row': 46,
            'excel_name': 'Fees & User Charges-Income head-wise',
            'unit': 'Lakhs'
        },
        'sale_hire_charges': {
            'row': 47,
            'excel_name': 'Sale & Hire Charges',
            'unit': 'Lakhs'
        },
        'revenue_grants': {
            'row': 48,
            'excel_name': 'Revenue Grants , Contributions & Subsidies',
            'unit': 'Lakhs'
        },
        'investment_income': {
            'row': 49,
            'excel_name': 'Income from Investments-General Fund',
            'unit': 'Lakhs'
        },
        'interest_earned': {
            'row': 50,
            'excel_name': 'Interest Earned',
            'unit': 'Lakhs'
        },
        'other_income': {
            'row': 51,
            'excel_name': 'Other Income',
            'unit': 'Lakhs'
        },
    },

    # Revenue Expenditure Fields
    'revenue_expenditure': {
        'establishment_expenses': {
            'row': 53,
            'excel_name': 'Establishment Expenses',
            'unit': 'Lakhs'
        },
        'administrative_expenses': {
            'row': 54,
            'excel_name': 'Administrative Expenses',
            'unit': 'Lakhs'
        },
        'operations_maintenance': {
            'row': 55,
            'excel_name': 'Operations & Maintenance',
            'unit': 'Lakhs'
        },
        'interest_finance_charges': {
            'row': 56,
            'excel_name': 'Interest & Finance Charges',
            'unit': 'Lakhs'
        },
        'programme_expenses': {
            'row': 57,
            'excel_name': 'Programme Expenses',
            'unit': 'Lakhs'
        },
        'revenue_grants_expenditure': {
            'row': 58,
            'excel_name': 'Revenue Grants, Contribution and Subsidies',
            'unit': 'Lakhs'
        },
        'provisions_writeoff': {
            'row': 59,
            'excel_name': 'Provisions and Write off',
            'unit': 'Lakhs'
        },
        'miscellaneous_expenses': {
            'row': 60,
            'excel_name': 'Miscellaneous Expenses',
            'unit': 'Lakhs'
        },
        'depreciation': {
            'row': 61,
            'excel_name': 'Depreciation',
            'unit': 'Lakhs'
        },
    },

    # Liabilities Fields
    'liabilities': {
        'municipal_fund': {
            'row': 63,
            'excel_name': 'Municipal (General) Fund',
            'unit': 'Lakhs'
        },
        'earmarked_funds': {
            'row': 64,
            'excel_name': 'Earmarked Funds',
            'unit': 'Lakhs'
        },
        'reserves': {
            'row': 65,
            'excel_name': 'Reserves',
            'unit': 'Lakhs'
        },
        'grants_specific_purposes': {
            'row': 66,
            'excel_name': 'Grants Contribution for specific purposes',
            'unit': 'Lakhs'
        },
        'secured_loans': {
            'row': 67,
            'excel_name': 'Secured Loans',
            'unit': 'Lakhs'
        },
        'deposits_received': {
            'row': 68,
            'excel_name': 'Deposits Received',
            'unit': 'Lakhs'
        },
        'deposit_works': {
            'row': 69,
            'excel_name': 'Deposit works',
            'unit': 'Lakhs'
        },
        'other_liabilities': {
            'row': 70,
            'excel_name': 'Other Liabilities',
            'unit': 'Lakhs'
        },
        'provisions': {
            'row': 71,
            'excel_name': 'Provisions',
            'unit': 'Lakhs'
        },
        'secured_unsecured_loans': {
            'row': 73,
            'excel_name': 'Secured and Unsecured Loans',
            'unit': 'Lakhs'
        },
    },

    # Assets Fields
    'assets': {
        'fixed_assets': {
            'row': 75,
            'excel_name': 'Fixed Assets (Gross block)',
            'unit': 'Lakhs'
        },
        'accumulated_depreciation': {
            'row': 76,
            'excel_name': 'Accumulated Depreciation',
            'unit': 'Lakhs'
        },
        'capital_wip': {
            'row': 77,
            'excel_name': 'Capital Work in Progress',
            'unit': 'Lakhs'
        },
        'investments_general': {
            'row': 78,
            'excel_name': 'Investments-General Fund',
            'unit': 'Lakhs'
        },
        'investments_other': {
            'row': 79,
            'excel_name': 'Investments-Other Fund',
            'unit': 'Lakhs'
        },
        'stock_in_hand': {
            'row': 80,
            'excel_name': 'Stock in Hand',
            'unit': 'Lakhs'
        },
        'sundry_debtors': {
            'row': 81,
            'excel_name': 'Sundry Debtors (Receivables) (Net)',
            'unit': 'Lakhs'
        },
        'cash_bank_balances': {
            'row': 82,
            'excel_name': 'Cash And Bank Balances',
            'unit': 'Lakhs'
        },
        'loans_advances_deposits': {
            'row': 83,
            'excel_name': 'Loans, Advances And Deposits (Net)',
            'unit': 'Lakhs'
        },
    },

    # Other Fields
    'other': {
        'audit_reports': {
            'row': 39,
            'excel_name': 'Does the city  prepare annual audit reports of ULB',
            'unit': 'Yes /No'
        },
    }
}

# City/State info rows
CITY_INFO_ROWS = {
    'state': {'row': 6, 'col': 3},
    'city': {'row': 7, 'col': 3},
}

# Year column mapping (column index in Excel)
YEAR_COLUMNS = {
    2022: 3,
    2023: 4,
    2024: 5,
    2025: 6,
}


def convert_to_lakhs(value: float, source_unit: str = 'lakhs') -> float:
    """Convert value to Lakhs if needed."""
    if value is None:
        return None

    source_unit = source_unit.lower()
    if source_unit in ['cr', 'crore', 'crores']:
        return value * 100  # 1 Crore = 100 Lakhs
    elif source_unit in ['l', 'lakh', 'lakhs']:
        return value
    elif source_unit in ['thousand', 'thousands']:
        return value / 100  # 1 Lakh = 100 Thousand
    return value


def map_scraped_to_excel(scraped_data: Dict) -> List[Tuple[int, int, any]]:
    """
    Map scraped data to Excel cell positions.

    Returns:
        List of tuples: (row, column, value)
    """
    updates = []

    # Determine year column
    year = scraped_data.get('year')
    year_col = YEAR_COLUMNS.get(year, 5)  # Default to 2024 column

    # Map revenue income fields
    revenue_income = scraped_data.get('revenue_income', {})
    for field_key, value in revenue_income.items():
        if value is not None and field_key in CFP_FIELD_MAPPING['revenue_income']:
            mapping = CFP_FIELD_MAPPING['revenue_income'][field_key]
            updates.append((mapping['row'], year_col, value))

    # Map revenue expenditure fields
    revenue_exp = scraped_data.get('revenue_expenditure', {})
    for field_key, value in revenue_exp.items():
        if value is not None and field_key in CFP_FIELD_MAPPING['revenue_expenditure']:
            mapping = CFP_FIELD_MAPPING['revenue_expenditure'][field_key]
            updates.append((mapping['row'], year_col, value))

    # Map liabilities fields
    liabilities = scraped_data.get('liabilities', {})
    for field_key, value in liabilities.items():
        if value is not None and field_key in CFP_FIELD_MAPPING['liabilities']:
            mapping = CFP_FIELD_MAPPING['liabilities'][field_key]
            updates.append((mapping['row'], year_col, value))

    # Map assets fields
    assets = scraped_data.get('assets', {})
    for field_key, value in assets.items():
        if value is not None and field_key in CFP_FIELD_MAPPING['assets']:
            mapping = CFP_FIELD_MAPPING['assets'][field_key]
            updates.append((mapping['row'], year_col, value))

    return updates


def get_field_summary(scraped_data: Dict) -> Dict:
    """
    Generate a summary of mapped vs unmapped fields.

    Returns:
        Dictionary with counts and lists of matched/unmatched fields
    """
    all_expected_fields = []
    for category, fields in CFP_FIELD_MAPPING.items():
        for field_key, info in fields.items():
            all_expected_fields.append({
                'category': category,
                'key': field_key,
                'excel_name': info['excel_name'],
                'row': info['row']
            })

    matched = []
    unmatched = []

    for field in all_expected_fields:
        category = field['category']
        key = field['key']

        scraped_category = scraped_data.get(category, {})
        value = scraped_category.get(key)

        if value is not None:
            matched.append({**field, 'value': value})
        else:
            unmatched.append(field)

    return {
        'total_fields': len(all_expected_fields),
        'matched_count': len(matched),
        'unmatched_count': len(unmatched),
        'matched_fields': matched,
        'unmatched_fields': unmatched,
        'completion_percentage': (len(matched) / len(all_expected_fields) * 100) if all_expected_fields else 0
    }


def validate_data(scraped_data: Dict) -> List[str]:
    """
    Validate scraped data for common issues.

    Returns:
        List of warning/error messages
    """
    issues = []

    # Check if any data was scraped
    has_any_data = False
    for category in ['revenue_income', 'revenue_expenditure', 'liabilities', 'assets']:
        cat_data = scraped_data.get(category, {})
        if any(v is not None for v in cat_data.values()):
            has_any_data = True
            break

    if not has_any_data:
        issues.append("WARNING: No financial data was scraped")

    # Check for negative values where unexpected
    for category, fields in [
        ('revenue_income', scraped_data.get('revenue_income', {})),
        ('assets', scraped_data.get('assets', {}))
    ]:
        for key, value in fields.items():
            if value is not None and value < 0:
                issues.append(f"WARNING: Negative value for {category}.{key}: {value}")

    # Check year
    year = scraped_data.get('year')
    if year is None:
        issues.append("WARNING: Financial year not specified")
    elif year < 2020 or year > 2030:
        issues.append(f"WARNING: Unusual financial year: {year}")

    return issues


if __name__ == "__main__":
    # Test the mapper
    sample_data = {
        'state': 'Tamil Nadu',
        'city': 'Tiruchirappalli',
        'year': 2024,
        'revenue_income': {
            'tax_revenue': 12500.5,
            'assigned_revenue': 3200.0,
            'fees_user_charges': 4500.0,
        },
        'revenue_expenditure': {
            'establishment_expenses': 8500.0,
            'operations_maintenance': 3200.0,
        },
        'liabilities': {
            'secured_loans': 15000.0,
        },
        'assets': {
            'fixed_assets': 125000.0,
            'cash_bank_balances': 5600.0,
        }
    }

    print("Testing Data Mapper...")

    print("\n1. Mapping to Excel positions:")
    updates = map_scraped_to_excel(sample_data)
    for row, col, value in updates:
        print(f"   Row {row}, Col {col}: {value}")

    print("\n2. Field Summary:")
    summary = get_field_summary(sample_data)
    print(f"   Matched: {summary['matched_count']}/{summary['total_fields']} ({summary['completion_percentage']:.1f}%)")
    print(f"   Unmatched: {summary['unmatched_count']}")

    print("\n3. Validation:")
    issues = validate_data(sample_data)
    if issues:
        for issue in issues:
            print(f"   {issue}")
    else:
        print("   No issues found")
