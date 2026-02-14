# LinkedIn Contact Extraction Batch Script
# Extracts visible contacts and appends to CSV

$csvPath = "C:\Users\Haide\.openclaw\workspace\linkedin_connections_full.csv"

# Read existing CSV to get already-extracted URLs
$existing = @{}
if (Test-Path $csvPath) {
    $existingData = Import-Csv $csvPath
    foreach ($row in $existingData) {
        if ($row.URL) {
            $existing[$row.URL] = $true
        }
    }
}

Write-Host "Existing contacts: $($existing.Count)"
Write-Host "Ready to extract from browser..."
