"""
Score calculations for Municipal Credit Assessment.
Replicates the scoring logic from the Excel tool.
"""


# Rating scale definitions
RATING_SCALE = {
    'PAS AAA': {'min': 90, 'max': 100, 'status': 'Highest level of creditworthiness', 'color': '#006400'},
    'PAS AA': {'min': 80, 'max': 90, 'status': 'High level of creditworthiness', 'color': '#228B22'},
    'PAS A': {'min': 60, 'max': 80, 'status': 'Adequate level of creditworthiness', 'color': '#32CD32'},
    'PAS BBB': {'min': 50, 'max': 60, 'status': 'Moderate level of creditworthiness', 'color': '#FFD700'},
    'PAS BB': {'min': 40, 'max': 50, 'status': 'High level of Credit Risk', 'color': '#FFA500'},
    'PAS B': {'min': 30, 'max': 40, 'status': 'Very High level of Credit Risk', 'color': '#FF6347'},
    'PAS C': {'min': 20, 'max': 30, 'status': 'Very High level of Credit Risk', 'color': '#FF4500'},
    'PAS D': {'min': 0, 'max': 20, 'status': 'Not creditworthy', 'color': '#DC143C'},
}


def get_grade_from_score(score: float) -> tuple:
    """Get the grade and status from a total score."""
    for grade, info in RATING_SCALE.items():
        if info['min'] <= score < info['max']:
            return grade, info['status'], info['color']
    if score >= 100:
        return 'PAS AAA', RATING_SCALE['PAS AAA']['status'], RATING_SCALE['PAS AAA']['color']
    return 'PAS D', RATING_SCALE['PAS D']['status'], RATING_SCALE['PAS D']['color']


def calculate_total_score(financial_score: float, operating_score: float) -> float:
    """
    Calculate the weighted total score.
    70% financial score + 30% operating score
    """
    return (financial_score * 0.7) + (operating_score * 0.3)


def calculate_borrowing_capacity(operating_surplus: float, interest_rate: float = 0.10) -> float:
    """
    Calculate borrowing capacity based on operating surplus.
    Assumes a 2.5x multiplier on operating surplus for debt servicing.
    """
    if operating_surplus <= 0:
        return 0
    return operating_surplus * 2.5


# Scoring thresholds for financial indicators
FINANCIAL_SCORING = {
    'own_tax_revenue_ratio': [(0.4, 4), (0.3, 3), (0.2, 2), (0.1, 1), (0, 0)],
    'non_tax_revenue_ratio': [(0.4, 4), (0.3, 3), (0.2, 2), (0.1, 1), (0, 0)],
    'establishment_expense_ratio': [(0.3, 4), (0.4, 3), (0.5, 2), (0.6, 1), (1, 0)],
    'surplus_ratio': [(0.2, 4), (0.15, 3), (0.1, 2), (0.05, 1), (0, 0)],
    'interest_coverage': [(4, 4), (3, 3), (2, 2), (1, 1), (0, 0)],
}


# Scoring thresholds for operating indicators
OPERATING_SCORING = {
    'water_coverage': [(0.9, 4), (0.7, 3), (0.5, 2), (0.3, 1), (0, 0)],
    'swm_coverage': [(0.9, 4), (0.7, 3), (0.5, 2), (0.3, 1), (0, 0)],
    'toilet_coverage': [(0.95, 4), (0.85, 3), (0.7, 2), (0.5, 1), (0, 0)],
    'collection_efficiency': [(0.9, 4), (0.8, 3), (0.7, 2), (0.6, 1), (0, 0)],
    'cost_recovery': [(1.0, 4), (0.8, 3), (0.6, 2), (0.4, 1), (0, 0)],
    'nrw': [(0.15, 4), (0.25, 3), (0.35, 2), (0.45, 1), (1, 0)],  # Lower is better
}


def score_indicator(value: float, thresholds: list, reverse: bool = False) -> int:
    """
    Score an indicator based on thresholds.
    thresholds: list of (threshold, score) tuples, ordered from best to worst
    reverse: if True, lower values are better
    """
    if value is None:
        return 0

    if reverse:
        for threshold, score in thresholds:
            if value <= threshold:
                return score
    else:
        for threshold, score in thresholds:
            if value >= threshold:
                return score
    return 0


def format_percentage(value) -> str:
    """Format a value as percentage."""
    if value is None:
        return "N/A"
    try:
        return f"{float(value) * 100:.1f}%"
    except:
        return str(value)


def format_currency(value, unit='Lakhs') -> str:
    """Format a value as currency."""
    if value is None:
        return "N/A"
    try:
        return f"₹{float(value):,.2f} {unit}"
    except:
        return str(value)


def get_trend_indicator(current: float, previous: float) -> tuple:
    """
    Get trend indicator comparing current to previous value.
    Returns (direction, color, icon)
    """
    if current is None or previous is None:
        return ('neutral', '#808080', '➖')

    diff = current - previous
    if diff > 0:
        return ('up', '#28a745', '📈')
    elif diff < 0:
        return ('down', '#dc3545', '📉')
    else:
        return ('neutral', '#808080', '➖')


def calculate_score_summary(financial_scores_df, operating_scores_df, year: int) -> dict:
    """Calculate summary scores for a given year."""

    # Sum financial scores
    financial_total = 0
    financial_max = 0
    if financial_scores_df is not None and year in financial_scores_df.columns:
        for _, row in financial_scores_df.iterrows():
            val = row.get(year)
            if val is not None and isinstance(val, (int, float)):
                financial_total += val
                financial_max += 4  # Max score per indicator

    # Sum operating scores
    operating_total = 0
    operating_max = 0
    if operating_scores_df is not None and year in operating_scores_df.columns:
        for _, row in operating_scores_df.iterrows():
            val = row.get(year)
            if val is not None and isinstance(val, (int, float)):
                operating_total += val
                operating_max += 4

    # Normalize to 100
    financial_score = (financial_total / financial_max * 100) if financial_max > 0 else 0
    operating_score = (operating_total / operating_max * 100) if operating_max > 0 else 0

    # Calculate total weighted score
    total_score = calculate_total_score(financial_score, operating_score)

    # Get grade
    grade, status, color = get_grade_from_score(total_score)

    return {
        'financial_score': round(financial_score, 1),
        'operating_score': round(operating_score, 1),
        'total_score': round(total_score, 1),
        'grade': grade,
        'status': status,
        'color': color
    }
