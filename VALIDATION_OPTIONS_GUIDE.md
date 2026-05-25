# Validation Options & Enhanced Regex Patterns Guide

## New Features

### ✅ 1. Backend Processing
**All Excel data processing now happens on the backend** - No data processing occurs in the frontend. The frontend only sends configuration (mappings, validation rules, options) to the backend API, which handles all data reading, validation, and Excel file generation.

### ✅ 2. Validation Options (Checkboxes)
Users can now choose which validations to apply:

| Option | Description | Default |
|--------|-------------|---------|
| **Check for Duplicates** | Detects duplicate rows and duplicate values in key columns (email, phone, ID, mobile) | ✅ Enabled |
| **Check for Empty Values** | Flags missing or empty values in all columns | ✅ Enabled |

**How to Use:**
1. Upload your Excel file
2. Map headers on Step 2
3. **Toggle checkboxes** at the top of the mapping page to enable/disable validation types
4. The backend will only perform enabled validations

### ✅ 3. New Regex Patterns

Two new validation patterns have been added:

#### **String Only** (Names)
- **Pattern:** `^[a-zA-Z\s]+$`
- **Description:** Letters and spaces only, no numbers
- **Use Cases:** 
  - Names (First Name, Last Name, Full Name)
  - City names
  - Country names
- **Examples:**
  - ✅ Valid: `John Doe`, `Mary Jane`, `San Francisco`
  - ❌ Invalid: `John123`, `User1`, `ABC-123`

#### **Numeric Only**
- **Pattern:** `^[0-9]+$`
- **Description:** Digits only (no decimals, letters, or special characters)
- **Use Cases:**
  - Customer IDs (numeric)
  - Employee IDs (numeric)
  - Order numbers
  - Quantity fields
- **Examples:**
  - ✅ Valid: `12345`, `9876543210`, `001`
  - ❌ Invalid: `123.45`, `ABC123`, `12-34`

### Complete Regex Pattern List

| Pattern | Description | Example Valid | Example Invalid |
|---------|-------------|---------------|-----------------|
| **Mobile** | Mobile number (various formats) | 1234567890, +1-555-123-4567 | abc123, 12-34 |
| **Email** | Email address | user@example.com | user@, @example.com |
| **Alphanumeric** | Letters and numbers only | ABC123, User123 | User@123, ABC-123 |
| **String Only** | Letters and spaces only | John Doe, Mary Jane | John123, User1 |
| **Numeric Only** | Digits only | 12345, 9876543210 | 123.45, ABC123 |
| **Pincode** | 6-digit pincode | 123456, 560001 | 12345, 1234567 |
| **None** | No validation | Any value | - |

## How It Works

### Backend Processing Flow

```
1. User uploads Excel file
   ↓
2. Backend reads file and extracts headers
   ↓
3. User maps headers and selects:
   - Validation rules (regex patterns)
   - Validation options (checkboxes)
   ↓
4. Backend saves configuration to database
   ↓
5. User clicks "Verify Data"
   ↓
6. Backend processes file:
   - Reads Excel data
   - Applies selected regex validations
   - Checks duplicates (if enabled)
   - Checks empty values (if enabled)
   - Generates validation report
   ↓
7. User downloads Excel with errors column
```

### API Changes

#### 1. POST `/api/excel-uploads/{id}/map_headers/`

**Request Body:**
```json
{
  "mappings": {
    "Name": "Full Name",
    "Phone": "Mobile Number"
  },
  "validation_rules": {
    "Name": "string_only",
    "Phone": "mobile",
    "Email": "email",
    "Customer ID": "numeric_only"
  },
  "validation_options": {
    "check_duplicates": true,
    "check_empty_values": true
  }
}
```

**Response:**
```json
{
  "message": "Header mappings, validation rules, and options saved successfully",
  "file_id": 123,
  "mappings": {...},
  "validation_rules": {...},
  "validation_options": {...}
}
```

#### 2. POST `/api/excel-uploads/{id}/validate/`

**Response:**
```json
{
  "report_id": 456,
  "validation_summary": {
    "total_rows": 100,
    "valid_rows": 85,
    "invalid_rows": 15,
    "error_count": 20,
    "warning_count": 5
  },
  "message": "Validation complete. Download the Excel file to view all errors."
}
```

## Database Schema Updates

### ExcelUpload Model

New field added:
```python
validation_options = models.JSONField(
    default=dict, 
    blank=True, 
    help_text='Validation options like check_duplicates, check_empty_values'
)
```

**Example stored data:**
```json
{
  "check_duplicates": true,
  "check_empty_values": false
}
```

## UI Changes

### Validation Options Section

Located at the top of the header mapping page:

```
┌─────────────────────────────────────────────┐
│ Validation Options                          │
│                                             │
│ ☑ Check for Duplicates                     │
│ ☑ Check for Empty Values                   │
└─────────────────────────────────────────────┘
```

**Styling:**
- Purple gradient background
- Checkbox inputs with hover effects
- Responsive grid layout

### Validation Rule Dropdown

Each column now has a dropdown with all regex patterns including the new ones:

```
┌─────────────────────────────────────────┐
│ Original Header: Name                   │
│ Validation Rule: [String only (letters  │
│                   and spaces, no numbers)│
│                   ▼                      │
│                  - Mobile number         │
│                  - Email address         │
│                  - Alphanumeric          │
│                  → String only           │
│                  - Numeric only          │
│                  - 6-digit pincode       │
│                  - No validation         │
└─────────────────────────────────────────┘
```

## Example Use Case

### Customer Data Validation

**Input Excel:**
| Name | Mobile | Email | Customer ID | Pincode |
|------|--------|-------|-------------|---------|
| John Doe | 1234567890 | john@example.com | 12345 | 560001 |
| Jane123 | invalid | jane@example | ABC123 | 12345 |

**Mappings:**
- Name → Full Name (String only)
- Mobile → Mobile Number (Mobile)
- Email → Email Address (Email)
- Customer ID → Customer ID (Numeric only)
- Pincode → Pin Code (6-digit pincode)

**Options:**
- ✅ Check for Duplicates
- ✅ Check for Empty Values

**Validation Results:**

Row 2 errors:
- `Full Name: Invalid String only (letters and spaces, no numbers)` - contains "123"
- `Mobile Number: Invalid Mobile number (various formats)` - "invalid" is not a valid mobile
- `Email Address: Invalid Email address` - missing domain extension
- `Customer ID: Invalid Numeric only (digits only)` - contains letters "ABC"
- `Pin Code: Invalid 6-digit pincode` - only 5 digits

**Downloaded Excel:**
| Full Name | Mobile Number | Email Address | Customer ID | Pin Code | Validation Errors |
|-----------|---------------|---------------|-------------|----------|-------------------|
| John Doe | 1234567890 | john@example.com | 12345 | 560001 | |
| Jane123 | invalid | jane@example | ABC123 | 12345 | Full Name: Invalid String only, Mobile Number: Invalid Mobile number, Email Address: Invalid Email address, Customer ID: Invalid Numeric only, Pin Code: Invalid 6-digit pincode |

## Testing

### Test the New Features

1. **Start the servers:**
   ```powershell
   .\start-dev.ps1
   ```

2. **Create test Excel file** with columns:
   - Name (with some containing numbers)
   - Mobile (with some invalid formats)
   - Customer ID (with some containing letters)

3. **Upload and map:**
   - Name → String only
   - Mobile → Mobile
   - Customer ID → Numeric only

4. **Toggle options:**
   - Uncheck "Check for Duplicates" - no duplicate checks
   - Uncheck "Check for Empty Values" - no empty value checks

5. **Verify and download:**
   - Check that only enabled validations appear in errors
   - Verify error messages reference the correct patterns

## Benefits

✅ **Backend Processing** - More secure, scalable, and reliable  
✅ **User Control** - Choose which validations to apply  
✅ **Better Validation** - String-only and numeric-only patterns  
✅ **Flexible** - Easy to add more validation options in the future  
✅ **Performance** - Skip unnecessary validations for faster processing  

## Future Enhancements

Potential additional validation options:
- ☐ **Trim Whitespace** - Automatically trim leading/trailing spaces
- ☐ **Case Normalization** - Convert to uppercase/lowercase
- ☐ **Custom Regex** - User-defined validation patterns
- ☐ **Cross-field Validation** - Validate relationships between columns
- ☐ **Data Transformation** - Apply formatting/transformations
