# Test Regex Validation Feature
# This script creates sample test files and instructions

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Regex Validation Feature - Test Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot

# Create test data folder
$testDataPath = "$projectRoot\test_data"
New-Item -ItemType Directory -Force -Path $testDataPath | Out-Null

# Test File 1: Mixed Valid and Invalid Data
Write-Host "Creating test file 1: Mixed valid/invalid data..." -ForegroundColor Yellow
$testData1 = @"
Name,Phone,Email,CustomerID,Pincode
John Doe,1234567890,john@example.com,CUST001,560001
Jane Smith,+1-555-123-4567,jane@example.com,CUST002,560002
Bob Johnson,invalid_phone,bob@example.com,CUST003,560003
Alice Brown,5551234567,not_an_email,CUST004,560004
Charlie Wilson,555-123-4567,charlie@example.com,CUST@05,12345
David Lee,9876543210,david@example.com,CUST006,560006
"@
$testData1 | Out-File -FilePath "$testDataPath\test_validation.csv" -Encoding UTF8

# Test File 2: All Valid Data
Write-Host "Creating test file 2: All valid data..." -ForegroundColor Yellow
$testData2 = @"
Name,Mobile,Email,ProductCode,ZipCode
Product A,1234567890,prod.a@company.com,ABC123,123456
Product B,9876543210,prod.b@company.com,XYZ789,654321
Product C,5551234567,prod.c@company.com,DEF456,111111
"@
$testData2 | Out-File -FilePath "$testDataPath\test_all_valid.csv" -Encoding UTF8

# Test File 3: Edge Cases
Write-Host "Creating test file 3: Edge cases..." -ForegroundColor Yellow
$testData3 = @"
Name,Phone,Email,Code,Pin
Test User 1,(555) 123-4567,user1@test.com,ABC123DEF,123456
Test User 2,+91-98765-43210,user2@test.com,999999,654321
Test User 3,555.123.4567,user3@test-domain.org,ONLY123,000000
Test User 4,abc,user4@,Special@Char,12345
Test User 5,12345,incomplete@,12,1234567
"@
$testData3 | Out-File -FilePath "$testDataPath\test_edge_cases.csv" -Encoding UTF8

Write-Host ""
Write-Host "✓ Test files created in: $testDataPath" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Instructions" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "File 1: test_validation.csv" -ForegroundColor Yellow
Write-Host "Expected Results:" -ForegroundColor White
Write-Host "  Row 4: ❌ Invalid mobile (value: 'invalid_phone')" -ForegroundColor Red
Write-Host "  Row 5: ❌ Invalid email (value: 'not_an_email')" -ForegroundColor Red
Write-Host "  Row 6: ❌ Invalid alphanumeric (value: 'CUST@05')" -ForegroundColor Red
Write-Host "  Row 6: ❌ Invalid pincode (value: '12345' - only 5 digits)" -ForegroundColor Red
Write-Host ""

Write-Host "File 2: test_all_valid.csv" -ForegroundColor Yellow
Write-Host "Expected Results:" -ForegroundColor White
Write-Host "  ✅ All rows should pass validation" -ForegroundColor Green
Write-Host ""

Write-Host "File 3: test_edge_cases.csv" -ForegroundColor Yellow
Write-Host "Expected Results:" -ForegroundColor White
Write-Host "  Row 5: Multiple validation errors" -ForegroundColor Red
Write-Host "  Row 6: Multiple validation errors" -ForegroundColor Red
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "How to Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Make sure servers are running:" -ForegroundColor White
Write-Host "   .\start-dev.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run database migration:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python manage.py migrate" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Open browser: http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "4. Upload test file: test_validation.csv" -ForegroundColor White
Write-Host ""
Write-Host "5. Set validation rules:" -ForegroundColor White
Write-Host "   - Phone → Select 'Mobile number (various formats)'" -ForegroundColor Gray
Write-Host "   - Email → Select 'Email address'" -ForegroundColor Gray
Write-Host "   - CustomerID → Select 'Alphanumeric (letters and numbers only)'" -ForegroundColor Gray
Write-Host "   - Pincode → Select '6-digit pincode'" -ForegroundColor Gray
Write-Host ""
Write-Host "6. Click 'Next: Verify Data'" -ForegroundColor White
Write-Host ""
Write-Host "7. Review validation report:" -ForegroundColor White
Write-Host "   - Should show 4 errors as listed above" -ForegroundColor Gray
Write-Host "   - Check error messages match expected results" -ForegroundColor Gray
Write-Host ""
Write-Host "8. Download verified Excel and check:" -ForegroundColor White
Write-Host "   - Error rows highlighted in red" -ForegroundColor Gray
Write-Host "   - Validation report sheet with details" -ForegroundColor Gray
Write-Host ""

Write-Host "Test files location: $testDataPath" -ForegroundColor Cyan
Write-Host ""
