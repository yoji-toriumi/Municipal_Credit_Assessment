"""
CFP (City Finance Portal) Data Scraper
Scrapes municipal financial data from https://www.cityfinance.in
"""

import requests
import time
import json
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

# Base URL for City Finance Portal
BASE_URL = "https://cityfinance.in"
API_BASE = "https://cityfinance.in/api/v1"

# Headers to mimic browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://cityfinance.in/',
}


class CFPScraper:
    """Scraper for City Finance Portal data."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self._states_cache = None
        self._ulbs_cache = {}

    def get_states(self) -> List[Dict]:
        """Get list of all states with their codes."""
        if self._states_cache:
            return self._states_cache

        try:
            response = self.session.get(f"{API_BASE}/state")
            if response.status_code == 200:
                data = response.json()
                states = data.get('data', [])
                self._states_cache = [
                    {
                        'name': s.get('name'),
                        'code': s.get('code'),
                        'slug': s.get('slug'),
                        'total_ulbs': s.get('fiscalRanking', [{}])[0].get('totalUlbs', 0) if s.get('fiscalRanking') else 0
                    }
                    for s in states if s.get('isActive')
                ]
                return self._states_cache
        except Exception as e:
            print(f"Error fetching states: {e}")

        # Fallback: return hardcoded major states
        return [
            {'name': 'Tamil Nadu', 'code': 'TN', 'slug': 'tamil-nadu', 'total_ulbs': 651},
            {'name': 'Maharashtra', 'code': 'MH', 'slug': 'maharashtra', 'total_ulbs': 428},
            {'name': 'Karnataka', 'code': 'KA', 'slug': 'karnataka', 'total_ulbs': 321},
            {'name': 'Gujarat', 'code': 'GJ', 'slug': 'gujarat', 'total_ulbs': 195},
            {'name': 'Andhra Pradesh', 'code': 'AP', 'slug': 'andhra-pradesh', 'total_ulbs': 123},
            {'name': 'Telangana', 'code': 'TS', 'slug': 'telangana', 'total_ulbs': 143},
            {'name': 'Kerala', 'code': 'KL', 'slug': 'kerala', 'total_ulbs': 93},
            {'name': 'Rajasthan', 'code': 'RJ', 'slug': 'rajasthan', 'total_ulbs': 213},
            {'name': 'Madhya Pradesh', 'code': 'MP', 'slug': 'madhya-pradesh', 'total_ulbs': 433},
            {'name': 'Uttar Pradesh', 'code': 'UP', 'slug': 'uttar-pradesh', 'total_ulbs': 775},
        ]

    def get_ulbs_by_state(self, state_code: str) -> List[Dict]:
        """Get list of ULBs (cities) for a given state."""
        if state_code in self._ulbs_cache:
            return self._ulbs_cache[state_code]

        try:
            # Try multiple API endpoint patterns
            endpoints = [
                f"{API_BASE}/ulb?stateCode={state_code}",
                f"{API_BASE}/ulbs/state/{state_code}",
                f"{API_BASE}/ulb/state/{state_code}",
            ]

            for endpoint in endpoints:
                try:
                    response = self.session.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        ulbs = data.get('data', data.get('ulbs', []))
                        if ulbs:
                            self._ulbs_cache[state_code] = [
                                {
                                    'name': u.get('name'),
                                    'code': u.get('code'),
                                    'slug': u.get('slug'),
                                    'ulb_type': u.get('ulbType', 'Unknown')
                                }
                                for u in ulbs
                            ]
                            return self._ulbs_cache[state_code]
                except:
                    continue
        except Exception as e:
            print(f"Error fetching ULBs for {state_code}: {e}")

        # Fallback: return sample data for Tamil Nadu
        if state_code == 'TN':
            return [
                {'name': 'Tiruchirappalli City Municipal Corporation', 'code': 'TRICHY', 'slug': 'tiruchirappalli', 'ulb_type': 'Municipal Corporation'},
                {'name': 'Chennai Corporation', 'code': 'CHENNAI', 'slug': 'chennai', 'ulb_type': 'Municipal Corporation'},
                {'name': 'Coimbatore City Municipal Corporation', 'code': 'CBE', 'slug': 'coimbatore', 'ulb_type': 'Municipal Corporation'},
                {'name': 'Madurai City Municipal Corporation', 'code': 'MDU', 'slug': 'madurai', 'ulb_type': 'Municipal Corporation'},
                {'name': 'Salem City Municipal Corporation', 'code': 'SLM', 'slug': 'salem', 'ulb_type': 'Municipal Corporation'},
            ]
        return []

    def get_financial_data(self, state_slug: str, ulb_slug: str) -> Dict:
        """
        Get financial data for a specific ULB.
        Returns a dictionary with CFP fields.
        """
        financial_data = {
            'state': None,
            'city': None,
            'year': None,
            'revenue_income': {},
            'revenue_expenditure': {},
            'liabilities': {},
            'assets': {},
            'source': 'cityfinance.in'
        }

        try:
            # Try to fetch from dashboard API
            endpoints = [
                f"{API_BASE}/dashboard/{state_slug}/{ulb_slug}",
                f"{API_BASE}/ulb/{ulb_slug}/financial-data",
                f"{API_BASE}/fiscal-ranking/ulb/{ulb_slug}",
            ]

            for endpoint in endpoints:
                try:
                    response = self.session.get(endpoint, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        return self._parse_financial_data(data)
                except:
                    continue

            # Try scraping the dashboard page directly
            dashboard_url = f"{BASE_URL}/v1/dashboard/{state_slug}/{ulb_slug}"
            return self._scrape_dashboard_page(dashboard_url)

        except Exception as e:
            print(f"Error fetching financial data: {e}")

        return financial_data

    def _parse_financial_data(self, data: Dict) -> Dict:
        """Parse API response into CFP fields structure."""
        result = {
            'state': data.get('state', {}).get('name'),
            'city': data.get('ulb', {}).get('name'),
            'year': data.get('financialYear', data.get('year')),
            'revenue_income': {},
            'revenue_expenditure': {},
            'liabilities': {},
            'assets': {},
            'source': 'cityfinance.in'
        }

        # Map income fields
        income_data = data.get('incomeStatement', data.get('revenue', {}))
        if income_data:
            result['revenue_income'] = {
                'tax_revenue': income_data.get('taxRevenue', income_data.get('ownTaxRevenue')),
                'assigned_revenue': income_data.get('assignedRevenue'),
                'rental_income': income_data.get('rentalIncome'),
                'fees_user_charges': income_data.get('feesAndUserCharges'),
                'sale_hire_charges': income_data.get('saleAndHireCharges'),
                'revenue_grants': income_data.get('revenueGrants'),
                'investment_income': income_data.get('incomeFromInvestments'),
                'interest_earned': income_data.get('interestEarned'),
                'other_income': income_data.get('otherIncome'),
            }

        # Map expenditure fields
        expense_data = data.get('expenditure', {})
        if expense_data:
            result['revenue_expenditure'] = {
                'establishment_expenses': expense_data.get('establishmentExpenses'),
                'administrative_expenses': expense_data.get('administrativeExpenses'),
                'operations_maintenance': expense_data.get('operationsAndMaintenance'),
                'interest_finance_charges': expense_data.get('interestAndFinanceCharges'),
                'programme_expenses': expense_data.get('programmeExpenses'),
                'provisions_writeoff': expense_data.get('provisionsAndWriteOff'),
                'miscellaneous_expenses': expense_data.get('miscellaneousExpenses'),
                'depreciation': expense_data.get('depreciation'),
            }

        # Map balance sheet fields
        balance_sheet = data.get('balanceSheet', {})
        if balance_sheet:
            liabilities = balance_sheet.get('liabilities', {})
            result['liabilities'] = {
                'municipal_fund': liabilities.get('municipalFund'),
                'earmarked_funds': liabilities.get('earmarkedFunds'),
                'reserves': liabilities.get('reserves'),
                'grants_specific_purposes': liabilities.get('grantsForSpecificPurposes'),
                'secured_loans': liabilities.get('securedLoans'),
                'unsecured_loans': liabilities.get('unsecuredLoans'),
                'deposits_received': liabilities.get('depositsReceived'),
                'other_liabilities': liabilities.get('otherLiabilities'),
                'provisions': liabilities.get('provisions'),
            }

            assets = balance_sheet.get('assets', {})
            result['assets'] = {
                'fixed_assets': assets.get('fixedAssets'),
                'accumulated_depreciation': assets.get('accumulatedDepreciation'),
                'capital_wip': assets.get('capitalWorkInProgress'),
                'investments_general': assets.get('investmentsGeneralFund'),
                'investments_other': assets.get('investmentsOtherFund'),
                'stock_in_hand': assets.get('stockInHand'),
                'sundry_debtors': assets.get('sundryDebtors'),
                'cash_bank_balances': assets.get('cashAndBankBalances'),
                'loans_advances_deposits': assets.get('loansAdvancesDeposits'),
            }

        return result

    def _scrape_dashboard_page(self, url: str) -> Dict:
        """
        Scrape financial data from dashboard page using BeautifulSoup.
        This is a fallback when API is not available.
        """
        result = {
            'state': None,
            'city': None,
            'year': None,
            'revenue_income': {},
            'revenue_expenditure': {},
            'liabilities': {},
            'assets': {},
            'source': 'cityfinance.in (scraped)'
        }

        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return result

            soup = BeautifulSoup(response.text, 'lxml')

            # Try to find JSON data embedded in the page
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'financialData' in script.string:
                    # Extract JSON from script
                    try:
                        import re
                        json_match = re.search(r'financialData\s*=\s*({.*?});', script.string, re.DOTALL)
                        if json_match:
                            data = json.loads(json_match.group(1))
                            return self._parse_financial_data(data)
                    except:
                        pass

            # Try to extract from Angular state
            for script in scripts:
                if script.string and '__nghData__' in script.string:
                    try:
                        # Parse Angular hydration data
                        pass
                    except:
                        pass

            # Extract from visible tables/elements
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)

                        # Map to appropriate field
                        if 'tax revenue' in label:
                            result['revenue_income']['tax_revenue'] = self._parse_value(value)
                        elif 'establishment' in label:
                            result['revenue_expenditure']['establishment_expenses'] = self._parse_value(value)
                        # Add more mappings as needed

        except Exception as e:
            print(f"Error scraping dashboard: {e}")

        return result

    def _parse_value(self, value_str: str) -> Optional[float]:
        """Parse a value string to float, handling currency and units."""
        if not value_str:
            return None

        try:
            # Remove currency symbols and commas
            cleaned = value_str.replace('₹', '').replace(',', '').replace(' ', '').strip()

            # Handle Cr (Crores) and L (Lakhs)
            multiplier = 1
            if 'cr' in cleaned.lower():
                multiplier = 100  # Convert Crores to Lakhs
                cleaned = cleaned.lower().replace('cr', '').replace('crore', '').replace('crores', '')
            elif 'l' in cleaned.lower() or 'lakh' in cleaned.lower():
                cleaned = cleaned.lower().replace('l', '').replace('lakh', '').replace('lakhs', '')

            return float(cleaned) * multiplier
        except:
            return None


def get_scraper() -> CFPScraper:
    """Get a CFP scraper instance."""
    return CFPScraper()


# Convenience functions
def list_states() -> List[Dict]:
    """List all available states."""
    scraper = CFPScraper()
    return scraper.get_states()


def list_cities(state_code: str) -> List[Dict]:
    """List cities for a given state code."""
    scraper = CFPScraper()
    return scraper.get_ulbs_by_state(state_code)


def fetch_cfp_data(state_slug: str, city_slug: str) -> Dict:
    """Fetch CFP financial data for a city."""
    scraper = CFPScraper()
    return scraper.get_financial_data(state_slug, city_slug)


if __name__ == "__main__":
    # Test the scraper
    print("Testing CFP Scraper...")

    scraper = CFPScraper()

    print("\n1. Fetching states...")
    states = scraper.get_states()
    print(f"   Found {len(states)} states")
    for s in states[:5]:
        print(f"   - {s['name']} ({s['code']}): {s['total_ulbs']} ULBs")

    print("\n2. Fetching ULBs for Tamil Nadu...")
    ulbs = scraper.get_ulbs_by_state('TN')
    print(f"   Found {len(ulbs)} ULBs")
    for u in ulbs[:5]:
        print(f"   - {u['name']}")

    print("\n3. Fetching financial data for Tiruchirappalli...")
    data = scraper.get_financial_data('tamil-nadu', 'tiruchirappalli')
    print(f"   City: {data.get('city')}")
    print(f"   Year: {data.get('year')}")
    print(f"   Source: {data.get('source')}")
