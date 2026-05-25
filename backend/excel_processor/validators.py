import re
import pandas as pd
from typing import List, Dict, Any, Tuple


# Predefined regex patterns for validation
REGEX_PATTERNS = {
    'mobile': {
        'pattern': r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$',
        'description': 'Mobile number (various formats)',
        'example': '1234567890, +1-555-123-4567, (555) 123-4567'
    },
    'email': {
        'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'description': 'Email address',
        'example': 'user@example.com'
    },
    'alphanumeric': {
        'pattern': r'^[a-zA-Z0-9]+$',
        'description': 'Alphanumeric (letters and numbers only)',
        'example': 'ABC123, User123'
    },
    'string_only': {
        'pattern': r'^[a-zA-Z\s]+$',
        'description': 'String only (letters and spaces, no numbers)',
        'example': 'John Doe, Mary Jane'
    },
    'numeric_only': {
        'pattern': r'^[0-9]+$',
        'description': 'Numeric only (digits only)',
        'example': '12345, 9876543210'
    },
    'pincode': {
        'pattern': r'^[0-9]{6}$',
        'description': '6-digit pincode',
        'example': '123456, 560001'
    },
    'none': {
        'pattern': None,
        'description': 'No validation',
        'example': 'Any value accepted'
    }
}


class DataValidator:
    """Validation engine for Excel data"""
    
    def __init__(self, df: pd.DataFrame, mapped_headers: Dict[str, str], validation_rules: Dict[str, str] | None = None, validation_options: Dict[str, bool] | None = None):
        """
        Initialize validator with dataframe and header mappings
        
        Args:
            df: pandas DataFrame with data to validate
            mapped_headers: dict mapping original headers to new headers
            validation_rules: dict mapping original headers to regex pattern keys
            validation_options: dict with boolean flags (check_duplicates, check_empty_values, etc.)
        """
        self.df = df
        self.mapped_headers = mapped_headers
        self.validation_rules = validation_rules or {}
        self.validation_options = validation_options or {'check_duplicates': True, 'check_empty_values': True}
        self.errors = []
        self.warnings = []
        
    def validate_all(self) -> Dict[str, Any]:
        """
        Run all validation rules and return report
        
        Returns:
            dict with errors, warnings, and counts
        """
        # Validate columns with user-selected regex patterns
        self.validate_with_regex_rules()
        
        # Check for required fields if enabled
        if self.validation_options.get('check_empty_values', True):
            self.validate_required_fields()
        
        # Check for duplicates if enabled
        if self.validation_options.get('check_duplicates', True):
            self.check_duplicates()
        
        valid_rows = self._count_valid_rows()
        invalid_rows = len(self.df) - valid_rows
        
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'valid_rows_count': valid_rows,
            'invalid_rows_count': invalid_rows
        }
    
    def validate_with_regex_rules(self):
        """Validate columns based on user-selected regex patterns"""
        for orig_header, new_header in self.mapped_headers.items():
            if orig_header not in self.df.columns:
                continue
            
            # Get the validation rule for this column
            rule_key = self.validation_rules.get(orig_header, 'none')
            
            # Skip if no validation or rule doesn't exist
            if rule_key == 'none' or rule_key not in REGEX_PATTERNS:
                continue
            
            pattern_info = REGEX_PATTERNS[rule_key]
            if pattern_info['pattern']:
                self._validate_column_with_regex(
                    orig_header, 
                    new_header, 
                    pattern_info['pattern'],
                    pattern_info['description']
                )
    
    def _validate_column_with_regex(self, column: str, display_name: str, regex_pattern: str, rule_description: str):
        """Validate a column using a regex pattern"""
        for idx, value in enumerate(self.df[column], start=2):  # Start from row 2 (Excel row numbering)
            if pd.isna(value) or str(value).strip() == '':
                continue
                
            value_str = str(value).strip()
            if not re.match(regex_pattern, value_str):
                self.errors.append({
                    'row': idx,
                    'column': display_name,
                    'value': value_str,
                    'issue': f'Invalid {rule_description}',
                    'type': 'data_type'
                })
    
    def validate_required_fields(self):
        """Check for missing values in all fields"""
        for orig_header, new_header in self.mapped_headers.items():
            if orig_header in self.df.columns:
                missing_rows = []
                for idx, value in enumerate(self.df[orig_header], start=2):
                    if pd.isna(value) or str(value).strip() == '':
                        missing_rows.append(idx)
                
                if missing_rows:
                    self.warnings.append({
                        'column': new_header,
                        'rows': missing_rows,
                        'issue': f'Missing values in {len(missing_rows)} row(s)',
                        'type': 'required'
                    })
    
    def check_duplicates(self):
        """Check for duplicate rows"""
        # Check for complete duplicate rows
        duplicate_mask = self.df.duplicated(keep=False)
        duplicate_rows = self.df[duplicate_mask].index.tolist()
        
        if duplicate_rows:
            # Convert to 1-indexed Excel row numbers (add 2 for header row)
            excel_rows = [idx + 2 for idx in duplicate_rows]
            self.warnings.append({
                'column': 'All columns',
                'rows': excel_rows,
                'issue': f'Found {len(duplicate_rows)} duplicate row(s)',
                'type': 'business'
            })
        
        # Check for duplicates in key columns (like phone, email, ID)
        key_patterns = [r'phone', r'email', r'id', r'mobile']
        for orig_header, new_header in self.mapped_headers.items():
            if any(re.search(pattern, new_header.lower()) for pattern in key_patterns):
                if orig_header in self.df.columns:
                    self._check_column_duplicates(orig_header, new_header)
    
    def _check_column_duplicates(self, column: str, display_name: str):
        """Check for duplicates in a specific column"""
        # Filter out empty values
        non_empty = self.df[column].dropna()
        non_empty = non_empty[non_empty.astype(str).str.strip() != '']
        
        if len(non_empty) > 0:
            duplicate_mask = non_empty.duplicated(keep=False)
            if duplicate_mask.any():
                duplicate_values = non_empty[duplicate_mask].unique()
                for value in duplicate_values:
                    dup_indices = self.df[self.df[column] == value].index.tolist()
                    excel_rows = [idx + 2 for idx in dup_indices]
                    
                    self.errors.append({
                        'column': display_name,
                        'rows': excel_rows,
                        'value': str(value),
                        'issue': f'Duplicate {display_name} found in rows {", ".join(map(str, excel_rows))}',
                        'type': 'business'
                    })
    
    def _count_valid_rows(self) -> int:
        """Count rows without errors"""
        error_rows = set()
        for error in self.errors:
            if 'row' in error:
                error_rows.add(error['row'])
            elif 'rows' in error:
                error_rows.update(error['rows'])
        
        total_rows = len(self.df)
        return total_rows - len(error_rows)


def validate_excel_data(df: pd.DataFrame, mapped_headers: Dict[str, str], validation_rules: Dict[str, str] | None = None, validation_options: Dict[str, bool] | None = None) -> Dict[str, Any]:
    """
    Convenience function to validate Excel data
    
    Args:
        df: pandas DataFrame with data
        mapped_headers: dict mapping original to new headers
        validation_rules: dict mapping original headers to regex pattern keys
        validation_options: dict with boolean flags for validation options
        
    Returns:
        dict with validation results
    """
    validator = DataValidator(df, mapped_headers, validation_rules, validation_options)
    return validator.validate_all()


def get_available_regex_patterns() -> Dict[str, Dict[str, str]]:
    """
    Get available regex patterns for frontend
    
    Returns:
        dict of pattern keys to pattern info
    """
    return REGEX_PATTERNS
