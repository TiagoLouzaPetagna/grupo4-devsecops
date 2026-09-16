param(
    [string]$Version = "20.2.0"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$TargetRoot = Join-Path $ProjectRoot "target"
$TargetDir = Join-Path $TargetRoot "juice-shop"
$PackageFile = Join-Path $TargetDir "package.json"

if (Test-Path -LiteralPath $PackageFile) {
    $Package = Get-Content -LiteralPath $PackageFile -Raw | ConvertFrom-Json
    if ($Package.version -eq $Version) {
        Write-Host "OWASP Juice Shop v$Version já está preparado."
        exit 0
    }
    throw "A pasta target/juice-shop contém a versão $($Package.version), não $Version. Revise-a antes de substituir."
}

New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null
$Archive = Join-Path $TargetRoot "juice-shop-v$Version.zip"
$ExtractRoot = Join-Path $TargetRoot "extract-v$Version"
$Uri = "https://codeload.github.com/juice-shop/juice-shop/zip/refs/tags/v$Version"

Write-Host "Baixando o código oficial: $Uri"
Invoke-WebRequest -Uri $Uri -OutFile $Archive
Expand-Archive -LiteralPath $Archive -DestinationPath $ExtractRoot -Force

$ExtractedDir = Join-Path $ExtractRoot "juice-shop-$Version"
if (-not (Test-Path -LiteralPath (Join-Path $ExtractedDir "package.json"))) {
    throw "Estrutura inesperada no arquivo oficial baixado."
}

Move-Item -LiteralPath $ExtractedDir -Destination $TargetDir
$Package = Get-Content -LiteralPath $PackageFile -Raw | ConvertFrom-Json
if ($Package.version -ne $Version) {
    throw "A versão interna $($Package.version) não corresponde ao release solicitado $Version."
}

Write-Host "OWASP Juice Shop v$Version preparado em target/juice-shop."

