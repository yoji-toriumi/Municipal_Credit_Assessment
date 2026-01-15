"""
Data loader for Municipal Credit Assessment Excel file.
Extracts and parses data from all sheets.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_excel_data(file_path: str) -> dict:
    """Load all data from the CWAS Excel file."""

    data = {
        'city_info': extract_city_info(file_path),
        'data_input': extract_data_input(file_path),
        'financial_ratios': extract_financial_ratios(file_path),
        'financial_scores': extract_financial_scores(file_path),
        'operating_ratios': extract_operating_ratios(file_path),
        'operating_scores': extract_operating_scores(file_path),
        'final_scores': extract_final_scores(file_path),
    }
    return data


def clean_value(val):
    """Clean a cell value, handling ND and other special cases."""
    if pd.isna(val):
        return None
    if isinstance(val, str):
        val = val.strip()
        if val in ['ND', '-', '']:
            return None
    return val


def extract_city_info(file_path: str) -> dict:
    """Extract city and state information."""
    df = pd.read_excel(file_path, sheet_name='Data Input', header=None)
    return {
        'state': clean_value(df.iloc[6, 3]) if len(df) > 6 else None,
        'city': clean_value(df.iloc[7, 3]) if len(df) > 7 else None,
    }


def extract_data_input(file_path: str) -> pd.DataFrame:
    """Extract the data input sheet as a structured DataFrame."""
    df = pd.read_excel(file_path, sheet_name='Data Input', header=None)

    # Get years from row 9
    years = []
    for col in range(3, 8):
        val = df.iloc[9, col] if col < len(df.columns) else None
        if pd.notna(val):
            try:
                years.append(int(float(val)))
            except:
                pass

    # Extract data rows (10-91)
    records = []
    for idx in range(10, min(92, len(df))):
        row = df.iloc[idx]
        source = clean_value(row[0]) if len(row) > 0 else None
        indicator = clean_value(row[1]) if len(row) > 1 else None
        unit = clean_value(row[2]) if len(row) > 2 else None

        if indicator:
            values = {}
            for i, year in enumerate(years):
                col_idx = 3 + i
                if col_idx < len(row):
                    values[year] = clean_value(row[col_idx])

            records.append({
                'source': source,
                'indicator': indicator,
                'unit': unit,
                **values
            })

    return pd.DataFrame(records)


def extract_financial_ratios(file_path: str) -> pd.DataFrame:
    """Extract financial ratios data."""
    df = pd.read_excel(file_path, sheet_name='Financial Ratios', header=None)

    # Get years from row 9 (columns 2-6)
    years = []
    for col in range(2, 7):
        val = df.iloc[9, col] if col < len(df.columns) else None
        if pd.notna(val):
            try:
                y = int(float(val))
                if 2000 < y < 2100:  # Valid year
                    years.append(y)
            except:
                pass

    records = []
    current_category = None

    for idx in range(10, min(50, len(df))):
        row = df.iloc[idx]
        indicator = clean_value(row[0]) if len(row) > 0 else None
        unit = clean_value(row[1]) if len(row) > 1 else None

        # Check if this is a category header (has indicator but no unit)
        if indicator and unit is None:
            current_category = indicator
            continue

        if indicator and unit:
            values = {}
            for i, year in enumerate(years):
                col_idx = 2 + i
                if col_idx < len(row):
                    val = clean_value(row[col_idx])
                    if val is not None:
                        try:
                            values[year] = float(val)
                        except:
                            values[year] = val

            records.append({
                'category': current_category,
                'indicator': indicator,
                'unit': unit,
                **values
            })

    return pd.DataFrame(records)


def extract_financial_scores(file_path: str) -> pd.DataFrame:
    """Extract financial scores data."""
    df = pd.read_excel(file_path, sheet_name='Financial Score', header=None)

    years = []
    for col in range(2, 7):
        val = df.iloc[5, col] if col < len(df.columns) else None
        if pd.notna(val):
            try:
                y = int(float(val))
                if 2000 < y < 2100:
                    years.append(y)
            except:
                pass

    records = []
    current_category = None

    for idx in range(6, min(40, len(df))):
        row = df.iloc[idx]
        indicator = clean_value(row[0]) if len(row) > 0 else None
        unit = clean_value(row[1]) if len(row) > 1 else None

        if indicator and unit is None:
            current_category = indicator
            continue

        if indicator and unit:
            values = {}
            for i, year in enumerate(years):
                col_idx = 2 + i
                if col_idx < len(row):
                    val = clean_value(row[col_idx])
                    if val is not None:
                        try:
                            values[year] = float(val)
                        except:
                            values[year] = val

            records.append({
                'category': current_category,
                'indicator': indicator,
                **values
            })

    return pd.DataFrame(records)


def extract_operating_ratios(file_path: str) -> pd.DataFrame:
    """Extract operating ratios data."""
    df = pd.read_excel(file_path, sheet_name='Operating Ratios', header=None)

    years = []
    for col in range(2, 7):
        val = df.iloc[9, col] if col < len(df.columns) else None
        if pd.notna(val):
            try:
                y = int(float(val))
                if 2000 < y < 2100:
                    years.append(y)
            except:
                pass

    records = []
    current_category = None

    for idx in range(10, min(50, len(df))):
        row = df.iloc[idx]
        indicator = clean_value(row[0]) if len(row) > 0 else None
        unit = clean_value(row[1]) if len(row) > 1 else None

        if indicator and unit is None:
            current_category = indicator
            continue

        if indicator and unit:
            values = {}
            for i, year in enumerate(years):
                col_idx = 2 + i
                if col_idx < len(row):
                    val = clean_value(row[col_idx])
                    if val is not None:
                        try:
                            values[year] = float(val)
                        except:
                            values[year] = val

            records.append({
                'category': current_category,
                'indicator': indicator,
                'unit': unit,
                **values
            })

    return pd.DataFrame(records)


def extract_operating_scores(file_path: str) -> pd.DataFrame:
    """Extract operating scores data."""
    df = pd.read_excel(file_path, sheet_name='Operating Score', header=None)

    years = []
    for col in range(2, 7):
        val = df.iloc[6, col] if col < len(df.columns) else None
        if pd.notna(val):
            try:
                y = int(float(val))
                if 2000 < y < 2100:
                    years.append(y)
            except:
                pass

    records = []
    current_category = None

    for idx in range(7, min(45, len(df))):
        row = df.iloc[idx]
        indicator = clean_value(row[0]) if len(row) > 0 else None
        unit = clean_value(row[1]) if len(row) > 1 else None

        if indicator and unit is None:
            current_category = indicator
            continue

        if indicator and unit:
            values = {}
            for i, year in enumerate(years):
                col_idx = 2 + i
                if col_idx < len(row):
                    val = clean_value(row[col_idx])
                    if val is not None:
                        try:
                            values[year] = float(val)
                        except:
                            values[year] = val

            records.append({
                'category': current_category,
                'indicator': indicator,
                **values
            })

    return pd.DataFrame(records)


def extract_final_scores(file_path: str) -> dict:
    """Extract final scores and grades."""
    df = pd.read_excel(file_path, sheet_name='Final Score & Grade', header=None)

    financial_scores = {}
    operating_scores = {}
    total_scores = {}

    # Financial scores (rows 8-11, columns 1 and 2)
    for idx in range(8, 12):
        if idx < len(df):
            year = df.iloc[idx, 1]  # Column 1 has year
            score = df.iloc[idx, 2]  # Column 2 has score
            if pd.notna(year) and pd.notna(score):
                try:
                    financial_scores[int(year)] = float(score)
                except:
                    pass

    # Operating scores (rows 16-19, columns 1 and 2)
    for idx in range(16, 20):
        if idx < len(df):
            year = df.iloc[idx, 1]
            score = df.iloc[idx, 2]
            if pd.notna(year) and pd.notna(score):
                try:
                    operating_scores[int(year)] = float(score)
                except:
                    pass

    # Total scores (rows 24-27, columns 1, 2, 4, 5)
    for idx in range(24, 28):
        if idx < len(df):
            year = df.iloc[idx, 1]
            total = df.iloc[idx, 2]
            grade = df.iloc[idx, 4]
            status = df.iloc[idx, 5]
            if pd.notna(year):
                try:
                    total_scores[int(year)] = {
                        'total_score': float(total) if pd.notna(total) else 0,
                        'grade': str(grade) if pd.notna(grade) else 'N/A',
                        'status': str(status) if pd.notna(status) else 'N/A'
                    }
                except:
                    pass

    return {
        'financial_scores': financial_scores,
        'operating_scores': operating_scores,
        'total_scores': total_scores
    }


def get_available_years(file_path: str) -> list:
    """Get list of available years from the data."""
    df = pd.read_excel(file_path, sheet_name='Data Input', header=None)
    years = []
    for col in range(3, 8):
        val = df.iloc[9, col] if col < len(df.columns) else None
        if pd.notna(val):
            try:
                y = int(float(val))
                if 2000 < y < 2100:
                    years.append(y)
            except:
                pass
    return years


if __name__ == "__main__":
    # Test the data loader
    file_path = "/content/drive/MyDrive/Municipal_Credit_Assessment/data/CWAS - Creditworthiness DIY Tool-Trichy.xlsm"
    data = load_excel_data(file_path)
    print("City Info:", data['city_info'])
    print("\nFinal Scores:", data['final_scores'])
