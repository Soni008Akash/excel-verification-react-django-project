# Regex Validation Feature Guide

## Overview
The Excel Verify Project now includes customizable regex validation rules that allow users to select specific validation patterns for each column during the header mapping step.

## Available Validation Rules

### 1. Mobile Number Validation
- **Pattern Key**: `mobile`
- **Description**: Mobile number (various formats)
- **Regex**: `^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$`
- **Valid Examples**:
  - `1234567890`
  - `+1-555-123-4567`
  - `(555) 123-4567`
  - `555.123.4567`
- **Use Case**: Phone number columns, contact fields

### 2. Email Validation
- **Pattern Key**: `email`
- **Description**: Email address
- **Regex**: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- **Valid Examples**:
  - `user@example.com`
  - `john.doe@company.co.uk`
  - `test_user+filter@domain.org`
- **Use Case**: Email address columns

### 3. Alphanumeric Validation
- **Pattern Key**: `alphanumeric`
- **Description**: Alphanumeric (letters and numbers only)
- **Regex**: `^[a-zA-Z0-9]+$`
- **Valid Examples**:
  - `ABC123`
  - `User123`
  - `12345`
  - `ProductCode`
- **Use Case**: Product codes, user IDs, license keys (without special characters)

### 4. 6-Digit Pincode Validation
- **Pattern Key**: `pincode`
- **Description**: 6-digit pincode
- **Regex**: `^[0-9]{6}$`
- **Valid Examples**:
  - `123456`
  - `560001`
  - `000001`
- **Use Case**: Postal codes, PIN codes, area codes (6 digits exactly)

### 5. No Validation
- **Pattern Key**: `none`
- **Description**: No validation
- **Pattern**: None
- **Use Case**: Free text fields, columns that don't require validation

## How to Use

### Step 1: Upload Excel File
Upload your Excel file as usual through the upload page.

### Step 2: Map Headers and Select Validation Rules
For each column:
1. Enter the new header name (or keep original)
2. **Select validation rule** from the dropdown:
   - Choose "Mobile" for phone number columns
   - Choose "Email" for email address columns
   - Choose "Alphanumeric" for code/ID columns
   - Choose "6-digit pincode" for pincode columns
   - Choose "No validation" to skip validation for that column

### Step 3: Proceed to Validation
Click "Next: Verify Data" to validate the data using your selected rules.

### Step 4: Review Results
The validation report will show:
- Errors for values that don't match the selected regex pattern
- Specific error messages like "Invalid Mobile number (various formats)"
- Row numbers where validation failed

## Example Workflow

**Scenario**: Validating a customer database

### Excel Headers:
- Customer Name
- Phone
- Email Address
- Customer ID
- ZIP Code

### Header Mapping with Validation:
1. **Customer Name** → "Full Name" + **No validation**
2. **Phone** → "Mobile Number" + **Mobile** validation
3. **Email Address** → "Email" + **Email** validation
4. **Customer ID** → "Customer ID" + **Alphanumeric** validation
5. **ZIP Code** → "Pincode" + **6-digit pincode** validation

### Sample Data:
```
Customer Name | Phone          | Email Address      | Customer ID | ZIP Code
John Doe      | 1234567890     | john@example.com   | CUST001     | 560001
Jane Smith    | invalid_phone  | jane@example.com   | CUST002     | 56001
Bob Johnson   | 555-123-4567   | not_an_email       | CUST@03     | 123456
```

### Validation Results:
- ❌ **Row 3**: Invalid Mobile number (value: "invalid_phone")
- ❌ **Row 3**: Invalid 6-digit pincode (value: "56001") - only 5 digits
- ❌ **Row 4**: Invalid Email address (value: "not_an_email")
- ❌ **Row 4**: Invalid Alphanumeric (value: "CUST@03") - contains special character

## Backend Implementation

### API Changes

**Get Regex Patterns**:
```
GET /api/excel-uploads/regex_patterns/
```
Returns all available regex patterns with descriptions and examples.

**Save Mappings with Validation Rules**:
```
POST /api/excel-uploads/{id}/map_headers/
Body: {
  "mappings": { "Phone": "Mobile Number" },
  "validation_rules": { "Phone": "mobile" }
}
```

**Validation Process**:
The validation engine (`validators.py`) now accepts validation rules and applies the selected regex pattern to each column.

### Database Changes

Added `validation_rules` JSONField to `ExcelUpload` model:
```python
validation_rules = models.JSONField(
    default=dict, 
    blank=True, 
    help_text='Regex validation rules per column'
)
```

### Code Structure

**Predefined Patterns** (`validators.py`):
```python
REGEX_PATTERNS = {
    'mobile': {
        'pattern': r'^[\+]?[(]?[0-9]{1,4}[)]?...',
        'description': 'Mobile number (various formats)',
        'example': '1234567890, +1-555-123-4567'
    },
    # ... more patterns
}
```

**Validation Function**:
```python
def validate_excel_data(df, mapped_headers, validation_rules=None):
    validator = DataValidator(df, mapped_headers, validation_rules)
    return validator.validate_all()
```

## Frontend Implementation

### HeaderMapper Component Updates

1. **Fetches available patterns** on mount
2. **Displays validation dropdown** for each column
3. **Tracks validation rules** alongside mappings
4. **Passes both mappings and rules** to parent component

### State Management

```javascript
const [mappings, setMappings] = useState({});
const [validationRules, setValidationRules] = useState({});
const [regexPatterns, setRegexPatterns] = useState({});
```

## Customization

### Adding New Validation Patterns

To add a new regex pattern:

1. **Update `validators.py`**:
```python
REGEX_PATTERNS = {
    # ... existing patterns
    'custom_pattern': {
        'pattern': r'^your-regex-here$',
        'description': 'Your description',
        'example': 'example1, example2'
    }
}
```

2. **Pattern is automatically available** in frontend dropdown (fetched via API)

3. **No frontend changes needed** - the dropdown is populated dynamically

### Examples of Custom Patterns

**US Social Security Number**:
```python
'ssn': {
    'pattern': r'^\d{3}-\d{2}-\d{4}$',
    'description': 'US Social Security Number (XXX-XX-XXXX)',
    'example': '123-45-6789'
}
```

**Date (DD/MM/YYYY)**:
```python
'date_ddmmyyyy': {
    'pattern': r'^\d{2}/\d{2}/\d{4}$',
    'description': 'Date (DD/MM/YYYY)',
    'example': '31/12/2023'
}
```

**Currency Amount**:
```python
'currency': {
    'pattern': r'^\$?\d{1,3}(,\d{3})*(\.\d{2})?$',
    'description': 'Currency amount (USD)',
    'example': '$1,234.56, 1234.56'
}
```

## Testing

### Test with Various Patterns

Create a test Excel file:
```
Name       | Mobile         | Email            | Code    | Pincode
John Doe   | 1234567890     | john@email.com   | ABC123  | 560001
Jane Smith | +1-555-123456  | jane@email.com   | XYZ789  | 560002
Invalid    | abc            | not_email        | AB@123  | 12345
```

Expected results:
- Row 4: Invalid mobile, invalid email, invalid alphanumeric, invalid pincode

## Migration

Run migration to add `validation_rules` field:
```powershell
cd backend
python manage.py migrate
```

## Benefits

1. **Flexible Validation**: Users choose validation per column
2. **Reduced False Positives**: Only validate what needs validation
3. **User Control**: Different files may need different rules
4. **Extensible**: Easy to add new regex patterns
5. **Clear Error Messages**: Shows which validation rule failed

## Notes

- Empty cells are **not validated** (they trigger warnings, not errors)
- Validation is **case-sensitive** for alphanumeric
- Mobile pattern supports **international formats**
- Email pattern follows **standard RFC validation**
- Pincode must be **exactly 6 digits** (no more, no less)
