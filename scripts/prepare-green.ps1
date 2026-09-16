$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SourceFile = Join-Path $ProjectRoot "target\juice-shop\routes\search.ts"
$FixedDir = Join-Path $ProjectRoot "target\juice-shop-fixed\routes"
$FixedFile = Join-Path $FixedDir "search.ts"

if (-not (Test-Path -LiteralPath $SourceFile)) {
    throw "Código do Juice Shop ausente. Execute scripts/fetch-target.ps1 primeiro."
}

$Unsafe = @'
models.sequelize.query(`SELECT * FROM Products WHERE ((name LIKE '%${criteria}%' OR description LIKE '%${criteria}%') AND deletedAt IS NULL) ORDER BY name`)
'@

$Safe = @'
models.sequelize.query(`SELECT * FROM Products WHERE ((name LIKE :criteria OR description LIKE :criteria) AND deletedAt IS NULL) ORDER BY name`, { replacements: { criteria: `%${criteria}%` } })
'@

$Source = Get-Content -LiteralPath $SourceFile -Raw
if (-not $Source.Contains($Unsafe)) {
    throw "Trecho vulnerável esperado não foi encontrado no Juice Shop v20.2.0."
}

New-Item -ItemType Directory -Force -Path $FixedDir | Out-Null
$Fixed = $Source.Replace($Unsafe, $Safe)
Set-Content -LiteralPath $FixedFile -Value $Fixed -Encoding UTF8

Write-Host "Cópia corrigida criada em target/juice-shop-fixed/routes/search.ts."
