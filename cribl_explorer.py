#!/usr/bin/env python3
"""
Cribl Cloud Architecture Explorer

This script provides a comprehensive overview of a Cribl Cloud environment by
querying the Cribl API and displaying information about worker groups, workers,
sources (inputs), destinations (outputs), pipelines, and routes.

Designed to help new engineers quickly understand the environment without
requiring deep prior knowledge of the system.

Requirements:
    - Python 3.6+
    - requests library (install with: pip install requests)

Usage:
    python cribl_explorer.py

Author: Generated for Cribl onboarding purposes
"""

import getpass
import sys
from typing import Dict, List, Optional, Any, Tuple

# ============================================================================
# DEPENDENCY CHECK
# ============================================================================
try:
    import requests
except ImportError:
    print("Error: The 'requests' library is required but not installed.")
    print("Please install it using: pip install requests")
    sys.exit(1)


# ============================================================================
# CONSTANTS
# ============================================================================

# API endpoint paths (appended to base URL)
ENDPOINTS = {
    'groups': '/api/v1/master/groups',
    'workers': '/api/v1/master/workers',
    'inputs': '/api/v1/m/{group_id}/system/inputs',
    'outputs': '/api/v1/m/{group_id}/system/outputs',
    'pipelines': '/api/v1/m/{group_id}/system/pipelines',
    'routes': '/api/v1/m/{group_id}/routes',
}

# HTTP timeout for API requests (in seconds)
REQUEST_TIMEOUT = 30


# ============================================================================
# API CLIENT CLASS
# ============================================================================

class CriblAPIClient:
    """
    A client for interacting with the Cribl Cloud API.

    Handles authentication, request formatting, and error handling for all
    API interactions with the Cribl Cloud instance.
    """

    def __init__(self, base_url: str, token: str):
        """
        Initialize the API client.

        Args:
            base_url: The Cribl Cloud instance base URL
                      (e.g., 'https://main-instance.cribl.cloud')
            token: The Bearer authentication token for API access
        """
        # Remove trailing slash from base URL if present
        self.base_url = base_url.rstrip('/')
        self.token = token

        # Set up default headers for all requests
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Tuple[bool, Any]:
        """
        Make an authenticated GET request to the Cribl API.

        Args:
            endpoint: The API endpoint path (will be appended to base URL)
            params: Optional query parameters for the request

        Returns:
            Tuple of (success: bool, data: dict or error message: str)
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=REQUEST_TIMEOUT
            )

            # Check for HTTP errors
            if response.status_code == 401:
                return False, "Authentication failed. Please check your Bearer token."
            elif response.status_code == 403:
                return False, "Access forbidden. Your token may lack required permissions."
            elif response.status_code == 404:
                return False, f"Endpoint not found: {endpoint}. Check your base URL."
            elif response.status_code >= 500:
                return False, f"Server error ({response.status_code}). Try again later."
            elif response.status_code != 200:
                return False, f"Unexpected status code: {response.status_code}"

            # Parse JSON response
            try:
                data = response.json()
                return True, data
            except ValueError as e:
                return False, f"Invalid JSON response: {str(e)}"

        except requests.exceptions.ConnectionError:
            return False, "Connection failed. Check your URL and network connection."
        except requests.exceptions.Timeout:
            return False, f"Request timed out after {REQUEST_TIMEOUT} seconds."
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {str(e)}"

    def get_groups(self) -> Tuple[bool, Any]:
        """
        Retrieve all worker groups (fleets) from the Cribl instance.

        Returns:
            Tuple of (success, list of groups or error message)
        """
        return self._make_request(ENDPOINTS['groups'])

    def get_workers(self) -> Tuple[bool, Any]:
        """
        Retrieve all workers across all groups.

        Returns:
            Tuple of (success, list of workers or error message)
        """
        return self._make_request(ENDPOINTS['workers'])

    def get_inputs(self, group_id: str) -> Tuple[bool, Any]:
        """
        Retrieve all sources (inputs) for a specific worker group.

        Args:
            group_id: The ID of the worker group

        Returns:
            Tuple of (success, list of inputs or error message)
        """
        endpoint = ENDPOINTS['inputs'].format(group_id=group_id)
        return self._make_request(endpoint)

    def get_outputs(self, group_id: str) -> Tuple[bool, Any]:
        """
        Retrieve all destinations (outputs) for a specific worker group.

        Args:
            group_id: The ID of the worker group

        Returns:
            Tuple of (success, list of outputs or error message)
        """
        endpoint = ENDPOINTS['outputs'].format(group_id=group_id)
        return self._make_request(endpoint)

    def get_pipelines(self, group_id: str) -> Tuple[bool, Any]:
        """
        Retrieve all pipelines for a specific worker group.

        Args:
            group_id: The ID of the worker group

        Returns:
            Tuple of (success, list of pipelines or error message)
        """
        endpoint = ENDPOINTS['pipelines'].format(group_id=group_id)
        return self._make_request(endpoint)

    def get_routes(self, group_id: str) -> Tuple[bool, Any]:
        """
        Retrieve all routes for a specific worker group.

        Args:
            group_id: The ID of the worker group

        Returns:
            Tuple of (success, list of routes or error message)
        """
        endpoint = ENDPOINTS['routes'].format(group_id=group_id)
        return self._make_request(endpoint)


# ============================================================================
# DATA EXTRACTION FUNCTIONS
# ============================================================================

def extract_group_info(groups_data: Dict) -> List[Dict]:
    """
    Extract relevant information from the groups API response.

    Args:
        groups_data: Raw API response containing group information

    Returns:
        List of dictionaries with extracted group details
    """
    items = groups_data.get('items', [])
    extracted = []

    for group in items:
        extracted.append({
            'id': group.get('id', 'N/A'),
            'name': group.get('name', group.get('id', 'N/A')),
            'product': group.get('product', 'stream'),
            'description': group.get('description', ''),
            'worker_count': group.get('workerCount', 0),
            'configVersion': group.get('configVersion', 'N/A'),
        })

    return extracted


def extract_worker_info(workers_data: Dict) -> List[Dict]:
    """
    Extract relevant information from the workers API response.

    Args:
        workers_data: Raw API response containing worker information

    Returns:
        List of dictionaries with extracted worker details
    """
    items = workers_data.get('items', [])
    extracted = []

    for worker in items:
        # Get worker info from nested structure if present
        info = worker.get('info', {})

        extracted.append({
            'id': worker.get('id', 'N/A'),
            'hostname': info.get('hostname', worker.get('hostname', 'N/A')),
            'group': worker.get('group', 'N/A'),
            'status': 'Online' if worker.get('connected', False) else 'Offline',
            'version': info.get('cribl', {}).get('version', 'N/A'),
            'ip': info.get('host', {}).get('ip', 'N/A'),
        })

    return extracted


def extract_input_info(inputs_data: Dict) -> List[Dict]:
    """
    Extract relevant information from the inputs (sources) API response.

    Args:
        inputs_data: Raw API response containing input information

    Returns:
        List of dictionaries with extracted input details
    """
    items = inputs_data.get('items', [])
    extracted = []

    for inp in items:
        extracted.append({
            'id': inp.get('id', 'N/A'),
            'type': inp.get('type', 'N/A'),
            'disabled': inp.get('disabled', False),
            'port': inp.get('port', inp.get('host', 'N/A')),
            'description': inp.get('description', ''),
        })

    return extracted


def extract_output_info(outputs_data: Dict) -> List[Dict]:
    """
    Extract relevant information from the outputs (destinations) API response.

    Args:
        outputs_data: Raw API response containing output information

    Returns:
        List of dictionaries with extracted output details
    """
    items = outputs_data.get('items', [])
    extracted = []

    for out in items:
        extracted.append({
            'id': out.get('id', 'N/A'),
            'type': out.get('type', 'N/A'),
            'disabled': out.get('disabled', False),
            'description': out.get('description', ''),
            'pipeline': out.get('pipeline', ''),
        })

    return extracted


def extract_pipeline_info(pipelines_data: Dict) -> List[Dict]:
    """
    Extract relevant information from the pipelines API response.

    Args:
        pipelines_data: Raw API response containing pipeline information

    Returns:
        List of dictionaries with extracted pipeline details
    """
    items = pipelines_data.get('items', [])
    extracted = []

    for pipe in items:
        # Count the number of functions in the pipeline
        functions = pipe.get('conf', {}).get('functions', [])
        function_types = [f.get('id', 'unknown') for f in functions]

        extracted.append({
            'id': pipe.get('id', 'N/A'),
            'description': pipe.get('conf', {}).get('description', ''),
            'function_count': len(functions),
            'functions': function_types[:5],  # Show first 5 functions
            'disabled': pipe.get('conf', {}).get('disabled', False),
        })

    return extracted


def extract_route_info(routes_data: Dict) -> List[Dict]:
    """
    Extract relevant information from the routes API response.

    Routes define how data flows from sources through pipelines to destinations.

    Args:
        routes_data: Raw API response containing route information

    Returns:
        List of dictionaries with extracted route details
    """
    items = routes_data.get('items', [])
    extracted = []

    for route in items:
        # Routes contain a list of route entries
        routes_list = route.get('routes', [])

        for r in routes_list:
            extracted.append({
                'id': r.get('id', r.get('name', 'N/A')),
                'name': r.get('name', 'N/A'),
                'filter': r.get('filter', '*'),
                'pipeline': r.get('pipeline', 'passthru'),
                'output': r.get('output', 'default'),
                'enabled': not r.get('disabled', False),
                'final': r.get('final', False),
                'description': r.get('description', ''),
            })

    return extracted


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def print_header(title: str, char: str = '='):
    """Print a formatted section header."""
    width = 70
    print(f"\n{char * width}")
    print(f" {title}")
    print(f"{char * width}")


def print_subheader(title: str):
    """Print a formatted subsection header."""
    print(f"\n  --- {title} ---")


def print_table(headers: List[str], rows: List[List[str]], indent: int = 4):
    """
    Print a simple text-based table.

    Args:
        headers: List of column headers
        rows: List of rows (each row is a list of values)
        indent: Number of spaces to indent the table
    """
    if not rows:
        print(f"{' ' * indent}No data available.")
        return

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Create format string
    indent_str = ' ' * indent
    separator = '-+-'.join('-' * w for w in col_widths)

    # Print header
    header_str = ' | '.join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(f"{indent_str}{header_str}")
    print(f"{indent_str}{separator}")

    # Print rows
    for row in rows:
        row_str = ' | '.join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        print(f"{indent_str}{row_str}")


def display_groups(groups: List[Dict]):
    """Display worker groups in a formatted table."""
    print_header("WORKER GROUPS (FLEETS)")

    headers = ['ID', 'Name', 'Product', 'Workers', 'Config Ver']
    rows = [
        [g['id'], g['name'], g['product'], str(g['worker_count']), g['configVersion']]
        for g in groups
    ]
    print_table(headers, rows)


def display_workers(workers: List[Dict], groups: List[Dict]):
    """
    Display workers organized by their groups.

    Args:
        workers: List of extracted worker information
        groups: List of extracted group information
    """
    print_header("WORKERS")

    # Organize workers by group
    workers_by_group: Dict[str, List[Dict]] = {}
    for worker in workers:
        group_id = worker['group']
        if group_id not in workers_by_group:
            workers_by_group[group_id] = []
        workers_by_group[group_id].append(worker)

    # Display workers under each group
    for group in groups:
        group_id = group['id']
        group_workers = workers_by_group.get(group_id, [])

        print_subheader(f"Group: {group['name']} ({len(group_workers)} workers)")

        if group_workers:
            headers = ['Hostname', 'Status', 'Version', 'IP']
            rows = [
                [w['hostname'], w['status'], w['version'], w['ip']]
                for w in group_workers
            ]
            print_table(headers, rows, indent=6)
        else:
            print("      No workers in this group.")


def display_group_details(group: Dict, inputs: List[Dict], outputs: List[Dict],
                         pipelines: List[Dict], routes: List[Dict]):
    """
    Display detailed information for a single worker group.

    Args:
        group: Group information dictionary
        inputs: List of inputs (sources) for the group
        outputs: List of outputs (destinations) for the group
        pipelines: List of pipelines for the group
        routes: List of routes for the group
    """
    print_header(f"GROUP DETAILS: {group['name']}", char='-')

    # Display Sources (Inputs)
    print_subheader(f"Sources/Inputs ({len(inputs)} total)")
    if inputs:
        headers = ['ID', 'Type', 'Status', 'Port/Host']
        rows = [
            [
                i['id'][:25],
                i['type'],
                'Disabled' if i['disabled'] else 'Enabled',
                str(i['port'])[:20]
            ]
            for i in inputs
        ]
        print_table(headers, rows, indent=6)
    else:
        print("      No sources configured.")

    # Display Destinations (Outputs)
    print_subheader(f"Destinations/Outputs ({len(outputs)} total)")
    if outputs:
        headers = ['ID', 'Type', 'Status']
        rows = [
            [
                o['id'][:30],
                o['type'],
                'Disabled' if o['disabled'] else 'Enabled'
            ]
            for o in outputs
        ]
        print_table(headers, rows, indent=6)
    else:
        print("      No destinations configured.")

    # Display Pipelines
    print_subheader(f"Pipelines ({len(pipelines)} total)")
    if pipelines:
        headers = ['ID', 'Functions', 'Status']
        rows = [
            [
                p['id'][:30],
                str(p['function_count']),
                'Disabled' if p['disabled'] else 'Enabled'
            ]
            for p in pipelines
        ]
        print_table(headers, rows, indent=6)
    else:
        print("      No pipelines configured.")

    # Display Routes
    print_subheader(f"Routes ({len(routes)} total)")
    if routes:
        headers = ['Name', 'Filter', 'Pipeline', 'Output', 'Final']
        rows = [
            [
                r['name'][:20] if r['name'] != 'N/A' else r['id'][:20],
                r['filter'][:15] if len(r['filter']) <= 15 else r['filter'][:12] + '...',
                r['pipeline'][:15],
                r['output'][:15],
                'Yes' if r['final'] else 'No'
            ]
            for r in routes
        ]
        print_table(headers, rows, indent=6)
    else:
        print("      No routes configured.")


def display_data_flow_diagram(group: Dict, inputs: List[Dict], outputs: List[Dict],
                              pipelines: List[Dict], routes: List[Dict]):
    """
    Display an ASCII art diagram showing the data flow for a group.

    This visualization helps understand how data moves from sources
    through pipelines to destinations.
    """
    print_subheader("Data Flow Visualization")

    # Get active (enabled) components
    active_inputs = [i for i in inputs if not i['disabled']]
    active_outputs = [o for o in outputs if not o['disabled']]
    active_pipelines = [p for p in pipelines if not p['disabled']]
    enabled_routes = [r for r in routes if r['enabled']]

    # Determine unique types for display
    input_types = list(set(i['type'] for i in active_inputs))[:4]
    output_types = list(set(o['type'] for o in active_outputs))[:4]
    pipeline_ids = [p['id'] for p in active_pipelines][:4]

    print()
    print("    " + "=" * 62)
    print(f"    |  Group: {group['name'][:50]:<50} |")
    print("    " + "=" * 62)
    print()

    # ASCII flow diagram
    print("    +-----------+     +-----------+     +-----------+     +------------+")
    print("    |  SOURCES  | --> |   ROUTES  | --> | PIPELINES | --> |   OUTPUTS  |")
    print("    +-----------+     +-----------+     +-----------+     +------------+")
    print(f"    | {len(active_inputs):^9} |     | {len(enabled_routes):^9} |     | {len(active_pipelines):^9} |     | {len(active_outputs):^10} |")
    print("    +-----------+     +-----------+     +-----------+     +------------+")
    print()

    # Show component types
    print("    Source Types:")
    for t in input_types:
        print(f"      - {t}")
    if len(input_types) < len(set(i['type'] for i in active_inputs)):
        print(f"      ... and {len(set(i['type'] for i in active_inputs)) - len(input_types)} more")

    print()
    print("    Output Types:")
    for t in output_types:
        print(f"      - {t}")
    if len(output_types) < len(set(o['type'] for o in active_outputs)):
        print(f"      ... and {len(set(o['type'] for o in active_outputs)) - len(output_types)} more")

    print()
    print("    Active Pipelines:")
    for p in pipeline_ids:
        print(f"      - {p}")
    if len(pipeline_ids) < len(active_pipelines):
        print(f"      ... and {len(active_pipelines) - len(pipeline_ids)} more")

    print()


def display_architecture_summary(groups: List[Dict], workers: List[Dict],
                                 all_group_data: Dict[str, Dict]):
    """
    Display a high-level summary of the entire Cribl architecture.

    Args:
        groups: List of all worker groups
        workers: List of all workers
        all_group_data: Dictionary mapping group IDs to their components
    """
    print_header("ARCHITECTURE SUMMARY")

    # Count totals
    total_inputs = sum(len(d.get('inputs', [])) for d in all_group_data.values())
    total_outputs = sum(len(d.get('outputs', [])) for d in all_group_data.values())
    total_pipelines = sum(len(d.get('pipelines', [])) for d in all_group_data.values())
    total_routes = sum(len(d.get('routes', [])) for d in all_group_data.values())

    online_workers = len([w for w in workers if w['status'] == 'Online'])

    print(f"""
    Cribl Cloud Environment Overview
    ================================

    Worker Groups (Fleets):  {len(groups)}
    Total Workers:           {len(workers)} ({online_workers} online)
    Total Sources:           {total_inputs}
    Total Destinations:      {total_outputs}
    Total Pipelines:         {total_pipelines}
    Total Routes:            {total_routes}

    Data Flow Overview:

        +-------------+    +-------------+    +-------------+    +--------------+
        |   SOURCES   | => |   ROUTES    | => |  PIPELINES  | => | DESTINATIONS |
        | ({total_inputs:^9}) |    | ({total_routes:^9}) |    | ({total_pipelines:^9}) |    | ({total_outputs:^10}) |
        +-------------+    +-------------+    +-------------+    +--------------+

    """)


# ============================================================================
# MAIN APPLICATION FUNCTIONS
# ============================================================================

def get_credentials() -> Tuple[str, str]:
    """
    Securely prompt the user for Cribl Cloud credentials.

    Returns:
        Tuple of (base_url, bearer_token)
    """
    print_header("CRIBL CLOUD ARCHITECTURE EXPLORER")
    print("""
    This tool provides a comprehensive overview of your Cribl Cloud environment.

    You will need:
    1. Your Cribl Cloud instance base URL
       (e.g., https://main-instance.cribl.cloud)
    2. A Bearer authentication token
       (Get it from Settings > Global > API Reference in Cribl)
    """)

    while True:
        base_url = input("\n    Enter Cribl Cloud base URL: ").strip()
        if not base_url:
            print("    Error: URL cannot be empty.")
            continue
        if not base_url.startswith(('http://', 'https://')):
            print("    Error: URL must start with http:// or https://")
            continue
        break

    while True:
        # Use getpass to hide the token input
        token = getpass.getpass("    Enter Bearer token (hidden): ").strip()
        if not token:
            print("    Error: Token cannot be empty.")
            continue
        break

    return base_url, token


def fetch_all_data(client: CriblAPIClient) -> Tuple[bool, Dict]:
    """
    Fetch all data from the Cribl API.

    Makes requests to all endpoints and aggregates the results.

    Args:
        client: Configured CriblAPIClient instance

    Returns:
        Tuple of (success, data dictionary or error message)
    """
    print("\n    Fetching data from Cribl API...")

    # Fetch groups
    print("    - Fetching worker groups...", end=" ")
    success, groups_data = client.get_groups()
    if not success:
        print("FAILED")
        return False, f"Failed to fetch groups: {groups_data}"
    print("OK")

    groups = extract_group_info(groups_data)

    # Fetch workers
    print("    - Fetching workers...", end=" ")
    success, workers_data = client.get_workers()
    if not success:
        print("FAILED")
        return False, f"Failed to fetch workers: {workers_data}"
    print("OK")

    workers = extract_worker_info(workers_data)

    # Fetch details for each group
    all_group_data = {}
    for group in groups:
        group_id = group['id']
        print(f"    - Fetching details for group '{group['name']}'...", end=" ")

        group_data = {'group': group}

        # Fetch inputs
        success, inputs_data = client.get_inputs(group_id)
        group_data['inputs'] = extract_input_info(inputs_data) if success else []

        # Fetch outputs
        success, outputs_data = client.get_outputs(group_id)
        group_data['outputs'] = extract_output_info(outputs_data) if success else []

        # Fetch pipelines
        success, pipelines_data = client.get_pipelines(group_id)
        group_data['pipelines'] = extract_pipeline_info(pipelines_data) if success else []

        # Fetch routes
        success, routes_data = client.get_routes(group_id)
        group_data['routes'] = extract_route_info(routes_data) if success else []

        all_group_data[group_id] = group_data
        print("OK")

    return True, {
        'groups': groups,
        'workers': workers,
        'group_data': all_group_data
    }


def display_menu() -> str:
    """
    Display the main menu and get user selection.

    Returns:
        User's menu choice
    """
    print("\n" + "-" * 50)
    print("    MENU")
    print("-" * 50)
    print("    1. View Architecture Summary")
    print("    2. View Worker Groups")
    print("    3. View Workers")
    print("    4. View Group Details (Sources, Outputs, Pipelines, Routes)")
    print("    5. View Data Flow Diagram")
    print("    6. Refresh Data")
    print("    7. Change Credentials")
    print("    Q. Quit")
    print("-" * 50)

    return input("    Select option: ").strip().upper()


def run_explorer(client: CriblAPIClient, data: Dict):
    """
    Run the main explorer interface loop.

    Args:
        client: Configured CriblAPIClient instance
        data: Fetched data dictionary
    """
    while True:
        choice = display_menu()

        if choice == '1':
            # Architecture Summary
            display_architecture_summary(
                data['groups'],
                data['workers'],
                data['group_data']
            )

        elif choice == '2':
            # Worker Groups
            display_groups(data['groups'])

        elif choice == '3':
            # Workers
            display_workers(data['workers'], data['groups'])

        elif choice == '4':
            # Group Details
            if not data['groups']:
                print("\n    No worker groups available.")
                continue

            print("\n    Available groups:")
            for i, group in enumerate(data['groups'], 1):
                print(f"      {i}. {group['name']} ({group['id']})")

            try:
                selection = input("    Select group number: ").strip()
                idx = int(selection) - 1
                if 0 <= idx < len(data['groups']):
                    group = data['groups'][idx]
                    group_data = data['group_data'].get(group['id'], {})
                    display_group_details(
                        group,
                        group_data.get('inputs', []),
                        group_data.get('outputs', []),
                        group_data.get('pipelines', []),
                        group_data.get('routes', [])
                    )
                else:
                    print("    Invalid selection.")
            except ValueError:
                print("    Please enter a valid number.")

        elif choice == '5':
            # Data Flow Diagram
            if not data['groups']:
                print("\n    No worker groups available.")
                continue

            print("\n    Available groups:")
            for i, group in enumerate(data['groups'], 1):
                print(f"      {i}. {group['name']} ({group['id']})")

            try:
                selection = input("    Select group number: ").strip()
                idx = int(selection) - 1
                if 0 <= idx < len(data['groups']):
                    group = data['groups'][idx]
                    group_data = data['group_data'].get(group['id'], {})
                    display_data_flow_diagram(
                        group,
                        group_data.get('inputs', []),
                        group_data.get('outputs', []),
                        group_data.get('pipelines', []),
                        group_data.get('routes', [])
                    )
                else:
                    print("    Invalid selection.")
            except ValueError:
                print("    Please enter a valid number.")

        elif choice == '6':
            # Refresh Data
            print("\n    Refreshing data...")
            success, new_data = fetch_all_data(client)
            if success:
                data.update(new_data)
                print("    Data refreshed successfully!")
            else:
                print(f"    Error: {new_data}")

        elif choice == '7':
            # Change Credentials - signal to restart
            return 'CHANGE_CREDENTIALS'

        elif choice == 'Q':
            print("\n    Goodbye!")
            return 'QUIT'

        else:
            print("    Invalid option. Please try again.")


def main():
    """
    Main entry point for the Cribl Architecture Explorer.

    Handles the credential input, data fetching, and main application loop.
    """
    while True:
        try:
            # Get credentials from user
            base_url, token = get_credentials()

            # Create API client
            client = CriblAPIClient(base_url, token)

            # Fetch initial data
            success, data = fetch_all_data(client)

            if not success:
                print(f"\n    Error: {data}")
                print("    Please check your credentials and try again.")
                retry = input("\n    Press Enter to retry or 'Q' to quit: ").strip().upper()
                if retry == 'Q':
                    break
                continue

            print("\n    Data fetched successfully!")

            # Run the explorer interface
            result = run_explorer(client, data)

            if result == 'QUIT':
                break
            elif result == 'CHANGE_CREDENTIALS':
                continue

        except KeyboardInterrupt:
            print("\n\n    Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n    Unexpected error: {str(e)}")
            print("    Please try again or check your inputs.")
            retry = input("\n    Press Enter to retry or 'Q' to quit: ").strip().upper()
            if retry == 'Q':
                break


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    main()
