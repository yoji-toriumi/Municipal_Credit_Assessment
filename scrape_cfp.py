#!/usr/bin/env python3
"""
CFP Data Scraper CLI
Command-line tool to scrape municipal financial data from cityfinance.in
"""

import argparse
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.cfp_scraper import CFPScraper, list_states, list_cities, fetch_cfp_data
from utils.data_mapper import get_field_summary, validate_data
from utils.excel_updater import update_excel_with_cfp_data


def cmd_list_states(args):
    """List all available states."""
    print("Fetching states from City Finance Portal...")
    states = list_states()

    print(f"\nAvailable States ({len(states)} total):")
    print("-" * 50)
    for state in sorted(states, key=lambda x: x['name']):
        ulbs = state.get('total_ulbs', 'N/A')
        print(f"  {state['code']:4} - {state['name']} ({ulbs} ULBs)")


def cmd_list_cities(args):
    """List cities for a given state."""
    state_code = args.state.upper()

    print(f"Fetching cities for state: {state_code}...")
    cities = list_cities(state_code)

    if not cities:
        print(f"No cities found for state code: {state_code}")
        return

    print(f"\nAvailable Cities ({len(cities)} total):")
    print("-" * 60)
    for city in sorted(cities, key=lambda x: x['name']):
        ulb_type = city.get('ulb_type', 'Unknown')
        print(f"  {city['slug']:30} - {city['name']} [{ulb_type}]")


def cmd_fetch(args):
    """Fetch CFP data for a city."""
    state_slug = args.state.lower().replace(' ', '-')
    city_slug = args.city.lower().replace(' ', '-')

    print(f"Fetching CFP data...")
    print(f"  State: {state_slug}")
    print(f"  City: {city_slug}")
    print()

    scraper = CFPScraper()
    data = scraper.get_financial_data(state_slug, city_slug)

    if args.output:
        # Save to JSON file
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to: {output_path}")
    else:
        # Print summary
        print("Scraped Data Summary:")
        print("-" * 40)
        print(f"  State: {data.get('state', 'N/A')}")
        print(f"  City: {data.get('city', 'N/A')}")
        print(f"  Year: {data.get('year', 'N/A')}")
        print(f"  Source: {data.get('source', 'N/A')}")

        # Field summary
        summary = get_field_summary(data)
        print(f"\nField Coverage:")
        print(f"  Matched: {summary['matched_count']}/{summary['total_fields']}")
        print(f"  Completion: {summary['completion_percentage']:.1f}%")

        # Revenue income
        ri = data.get('revenue_income', {})
        if any(v is not None for v in ri.values()):
            print(f"\nRevenue Income:")
            for key, value in ri.items():
                if value is not None:
                    print(f"  {key}: {value:,.2f} Lakhs")

        # Revenue expenditure
        re = data.get('revenue_expenditure', {})
        if any(v is not None for v in re.values()):
            print(f"\nRevenue Expenditure:")
            for key, value in re.items():
                if value is not None:
                    print(f"  {key}: {value:,.2f} Lakhs")

        # Validate
        issues = validate_data(data)
        if issues:
            print(f"\nValidation Issues:")
            for issue in issues:
                print(f"  {issue}")


def cmd_update_excel(args):
    """Fetch CFP data and update Excel file."""
    state_slug = args.state.lower().replace(' ', '-')
    city_slug = args.city.lower().replace(' ', '-')
    excel_path = args.excel

    if not Path(excel_path).exists():
        print(f"Error: Excel file not found: {excel_path}")
        return 1

    print(f"Fetching CFP data...")
    print(f"  State: {state_slug}")
    print(f"  City: {city_slug}")

    scraper = CFPScraper()
    data = scraper.get_financial_data(state_slug, city_slug)

    # Validate data first
    issues = validate_data(data)
    if issues:
        print(f"\nValidation warnings:")
        for issue in issues:
            print(f"  {issue}")

    if args.dry_run:
        print(f"\nDry run - Excel would be updated with:")
        summary = get_field_summary(data)
        print(f"  {summary['matched_count']} fields")
        print(f"  {summary['completion_percentage']:.1f}% coverage")
        return 0

    print(f"\nUpdating Excel file: {excel_path}")

    try:
        result = update_excel_with_cfp_data(
            excel_path,
            data,
            create_backup=not args.no_backup
        )

        print(f"\nUpdate Complete!")
        print(f"  Year: {result['year']}")
        print(f"  Updated: {result['updated_count']} fields")
        print(f"  Completion: {result['completion_percentage']:.1f}%")

        if result.get('backup_path'):
            print(f"  Backup: {result['backup_path']}")

        if args.verbose:
            print(f"\nChanges made:")
            for change in result['changes']:
                print(f"  {change}")

    except Exception as e:
        print(f"Error updating Excel: {e}")
        return 1

    return 0


def main():
    parser = argparse.ArgumentParser(
        description='CFP Data Scraper - Fetch municipal financial data from cityfinance.in',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s list-states
  %(prog)s list-cities --state TN
  %(prog)s fetch --state tamil-nadu --city tiruchirappalli
  %(prog)s fetch --state tamil-nadu --city chennai --output data.json
  %(prog)s update --state tamil-nadu --city tiruchirappalli --excel data/CWAS.xlsm
        '''
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List states command
    states_parser = subparsers.add_parser('list-states', help='List available states')
    states_parser.set_defaults(func=cmd_list_states)

    # List cities command
    cities_parser = subparsers.add_parser('list-cities', help='List cities for a state')
    cities_parser.add_argument('--state', '-s', required=True, help='State code (e.g., TN, MH)')
    cities_parser.set_defaults(func=cmd_list_cities)

    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch CFP data for a city')
    fetch_parser.add_argument('--state', '-s', required=True, help='State slug (e.g., tamil-nadu)')
    fetch_parser.add_argument('--city', '-c', required=True, help='City slug (e.g., tiruchirappalli)')
    fetch_parser.add_argument('--output', '-o', help='Output JSON file path')
    fetch_parser.set_defaults(func=cmd_fetch)

    # Update Excel command
    update_parser = subparsers.add_parser('update', help='Fetch and update Excel file')
    update_parser.add_argument('--state', '-s', required=True, help='State slug')
    update_parser.add_argument('--city', '-c', required=True, help='City slug')
    update_parser.add_argument('--excel', '-e', required=True, help='Path to Excel file')
    update_parser.add_argument('--dry-run', '-n', action='store_true', help='Show what would be updated')
    update_parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
    update_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed changes')
    update_parser.set_defaults(func=cmd_update_excel)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main() or 0)
