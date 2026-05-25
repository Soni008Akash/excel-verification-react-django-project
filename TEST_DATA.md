# Sample Test Data for Excel Verify Project

## Test File 1: Valid Data
Create a file named `test_valid.xlsx` with the following data:

| Name | Mobile | Email | ID |
|------|--------|-------|-----|
| John Doe | 1234567890 | john@example.com | 101 |
| Jane Smith | 9876543210 | jane@example.com | 102 |
| Bob Johnson | 5551234567 | bob@example.com | 103 |

## Test File 2: Data with Errors
Create a file named `test_errors.xlsx` with the following data:

| Name | Mobile | Email | ID |
|------|--------|-------|-----|
| John Doe | 1234567890 | john@example.com | 101 |
| Jane Smith | invalid_phone | invalid_email | 102 |
| Bob Johnson | 5551234567 | bob@example.com | 103 |
| Alice Brown | 1112223333 | alice@example.com | 101 |

Expected Errors:
- Row 3: Invalid phone number format
- Row 3: Invalid email format
- Row 4: Duplicate ID (101)

## Test File 3: Data with Missing Values
Create a file named `test_missing.xlsx` with the following data:

| Name | Mobile | Email | ID |
|------|--------|-------|-----|
| John Doe | 1234567890 | john@example.com | 101 |
| Jane Smith |  | jane@example.com | 102 |
| Bob Johnson | 5551234567 |  | 103 |

Expected Warnings:
- Row 3: Missing mobile number
- Row 4: Missing email

## Test File 4: Complex Scenario
Create a file named `test_complex.xlsx` with the following data:

| Full Name | Phone Number | E-mail Address | Customer ID | Age |
|-----------|--------------|----------------|-------------|-----|
| John Doe | +1-555-123-4567 | john@example.com | C001 | 30 |
| Jane Smith | (555) 987-6543 | jane@example.com | C002 | 25 |
| Bob Johnson | 555.111.2222 | bob@test.com | C003 | 45 |
| Alice Brown | +1-555-123-4567 | alice@example.com | C004 | 35 |
| Charlie Wilson | invalid | not_an_email | C002 | 28 |
| David Lee |  | david@example.com | C006 | 40 |

Expected Results:
- Valid phone formats: rows 2, 3, 4
- Invalid phone: row 6 (format error)
- Invalid email: row 6 (format error)
- Duplicate phone: rows 2 and 5
- Duplicate ID: rows 3 and 6
- Missing phone: row 7

## How to Use Test Files

1. Create Excel files with the data above
2. Upload to the application
3. Map headers (e.g., "Full Name" → "Name", "Phone Number" → "Mobile")
4. Run validation
5. Verify that errors/warnings match expectations
6. Download verified Excel and check:
   - Headers are mapped correctly
   - Error rows are highlighted in red
   - Warning rows are highlighted in yellow
   - Validation report sheet contains details

## Quick Test Commands (PowerShell)

```powershell
# Create a simple CSV test file
$testData = @"
Name,Mobile,Email,ID
John Doe,1234567890,john@example.com,101
Jane Smith,invalid,jane@example.com,102
Bob Johnson,5551234567,bob@example.com,103
"@

$testData | Out-File -FilePath "backend\media\test_sample.csv" -Encoding UTF8
```
