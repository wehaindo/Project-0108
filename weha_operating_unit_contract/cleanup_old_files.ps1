# Cleanup Script for weha_operating_unit_hierarchy
# Run this AFTER confirming the new module works correctly

Write-Host "=== Cleanup Old Revenue Sharing Files ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will remove old revenue sharing files from weha_operating_unit_hierarchy" -ForegroundColor Yellow
Write-Host "Make sure the new module (weha_operating_unit_contract) is installed and working!" -ForegroundColor Yellow
Write-Host ""

$confirmation = Read-Host "Continue with cleanup? (yes/no)"

if ($confirmation -ne "yes") {
    Write-Host "Cleanup cancelled." -ForegroundColor Red
    exit
}

$basePath = "d:\OdooProject\Project-0108\weha_operating_unit_hierarchy"

Write-Host "`nRemoving model files..." -ForegroundColor Cyan

$modelFiles = @(
    "$basePath\models\revenue_sharing_rule.py",
    "$basePath\models\revenue_sharing_period.py",
    "$basePath\models\revenue_sharing_entry.py",
    "$basePath\models\pos_order.py"
)

foreach ($file in $modelFiles) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  [√] Removed: $(Split-Path $file -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "  [!] Not found: $(Split-Path $file -Leaf)" -ForegroundColor Yellow
    }
}

Write-Host "`nRemoving view files..." -ForegroundColor Cyan

$viewFiles = @(
    "$basePath\views\revenue_sharing_rule_views.xml",
    "$basePath\views\revenue_sharing_period_views.xml",
    "$basePath\views\revenue_sharing_entry_views.xml"
)

foreach ($file in $viewFiles) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  [√] Removed: $(Split-Path $file -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "  [!] Not found: $(Split-Path $file -Leaf)" -ForegroundColor Yellow
    }
}

Write-Host "`nRemoving security file..." -ForegroundColor Cyan

$securityFile = "$basePath\security\revenue_sharing_security.xml"
if (Test-Path $securityFile) {
    Remove-Item $securityFile -Force
    Write-Host "  [√] Removed: revenue_sharing_security.xml" -ForegroundColor Green
} else {
    Write-Host "  [!] Not found: revenue_sharing_security.xml" -ForegroundColor Yellow
}

Write-Host "`n=== Cleanup Completed ===" -ForegroundColor Green
Write-Host ""
Write-Host "Files removed from weha_operating_unit_hierarchy" -ForegroundColor White
Write-Host "The base module now contains only hierarchy management" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart Odoo server" -ForegroundColor White
Write-Host "2. Update apps list in Odoo" -ForegroundColor White
Write-Host "3. Verify both modules work correctly" -ForegroundColor White
