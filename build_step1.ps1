# AI Highlighter Build Script - Creates all system files
$base = "C:\Users\kency\AI_Highlighter"

# Create __init__.py files
"" | Out-File "$base\modules\__init__.py" -Encoding utf8
"" | Out-File "$base\api\__init__.py" -Encoding utf8
"" | Out-File "$base\tests\__init__.py" -Encoding utf8
"" | Out-File "$base\__init__.py" -Encoding utf8

Write-Host "Init files created"
