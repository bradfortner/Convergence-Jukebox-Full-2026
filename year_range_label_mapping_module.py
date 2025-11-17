"""
Year Range Label Mapping Module
Loads year-range-to-label mappings from YearRangeLabelList.txt and provides lookup functionality
"""
import os
import ast

# Module-level storage for year range mappings
_year_range_mappings = []

def _load_year_range_mappings():
    """Load year range mappings from YearRangeLabelList.txt at module import time"""
    global _year_range_mappings

    file_path = 'YearRangeLabelList.txt'

    if not os.path.exists(file_path):
        print(f"[YEAR RANGE MAPPING] {file_path} not found - will use all labels for all years")
        _year_range_mappings = []
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        if not content:
            print(f"[YEAR RANGE MAPPING] {file_path} is empty - will use all labels for all years")
            _year_range_mappings = []
            return

        # Parse the list using ast.literal_eval for safe evaluation
        mappings = ast.literal_eval(content)

        if not isinstance(mappings, list):
            print(f"[YEAR RANGE MAPPING] Invalid format in {file_path} - expected list")
            _year_range_mappings = []
            return

        _year_range_mappings = mappings
        print(f"[YEAR RANGE MAPPING] Loaded {len(_year_range_mappings)} year range mappings")

        # Log each range for debugging
        for mapping in _year_range_mappings:
            if len(mapping) == 3:
                start_year, end_year, labels = mapping
                print(f"[YEAR RANGE MAPPING]   {start_year}-{end_year}: {len(labels)} labels")

    except Exception as e:
        print(f"[YEAR RANGE MAPPING] Error loading {file_path}: {e}")
        _year_range_mappings = []

def get_labels_for_year(year, available_labels):
    """
    Get the list of valid labels for a specific year based on year range mappings.

    Args:
        year: The year to look up (int or string that can be converted to int)
        available_labels: List of all available label filenames

    Returns:
        List of label filenames valid for the given year.
        Returns available_labels (all labels) if:
        - year is None/invalid
        - No mappings are loaded
        - No range matches the year
    """
    # If no mappings loaded, return all labels
    if not _year_range_mappings:
        return available_labels

    # Try to convert year to integer
    try:
        if year is None:
            return available_labels
        year_int = int(year)
    except (ValueError, TypeError):
        print(f"[YEAR RANGE MAPPING] Invalid year value: {year} - using all labels")
        return available_labels

    # Search for matching year range
    for mapping in _year_range_mappings:
        if len(mapping) != 3:
            continue

        start_year, end_year, mapped_labels = mapping

        # Check if year falls in this range
        if start_year <= year_int <= end_year:
            # Filter to only labels that exist in available_labels
            valid_labels = [label for label in mapped_labels if label in available_labels]

            if valid_labels:
                print(f"[YEAR RANGE MAPPING] Year {year_int} matches {start_year}-{end_year}: {len(valid_labels)} valid labels")
                return valid_labels
            else:
                print(f"[YEAR RANGE MAPPING] Year {year_int} matches {start_year}-{end_year} but no valid labels found - using all labels")
                return available_labels

    # No range matched - return all labels
    print(f"[YEAR RANGE MAPPING] Year {year_int} has no matching range - using all labels")
    return available_labels

# Load mappings when module is imported
_load_year_range_mappings()
