param(
    [ValidateSet("sast-red", "sast-green", "dast", "all")]
    [string]$Mode = "all"
)

# Windows PowerShell 5.1 converts harmless native stderr warnings into errors when
# this preference is Stop. Native commands are checked explicitly via LASTEXITCODE.
$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ReportsDir = Join-Path $ProjectRoot "reports"

function Invoke-SemgrepScenario {
    param(
        [ValidateSet("red", "green")]
        [string]$Scenario
    )

    if ($Scenario -eq "red") {
        $Target = "/workspace/target/juice-shop/routes/search.ts"
        $Expected = "fail"
    } else {
        & (Join-Path $PSScriptRoot "prepare-green.ps1")
        $Target = "/workspace/target/juice-shop-fixed/routes/search.ts"
        $Expected = "pass"
    }

    Write-Host "Semgrep - cenario $Scenario"
    docker compose --profile tools run --rm semgrep semgrep scan `
        --config /workspace/security/semgrep.yml `
        --json --output "/workspace/reports/semgrep-$Scenario.json" `
        $Target
    if ($LASTEXITCODE -ne 0) { throw "Falha operacional do Semgrep no cenário $Scenario." }

    docker compose --profile tools run --rm gate node /workspace/scripts/quality-gate.mjs `
        --semgrep "/workspace/reports/semgrep-$Scenario.json" `
        --threshold HIGH `
        --expect $Expected
    if ($LASTEXITCODE -ne 0) { throw "O resultado $Scenario não correspondeu à expectativa do gate." }
}

function Invoke-ZapScenario {
    Write-Host "Iniciando OWASP Juice Shop v20.2.0 em rede isolada"
    docker compose up -d juice-shop
    if ($LASTEXITCODE -ne 0) { throw "Falha ao iniciar o OWASP Juice Shop." }

    try {
        Write-Host "OWASP ZAP - spider + AJAX spider + active scan"
        docker compose --profile tools run --rm zap
        $ZapExit = $LASTEXITCODE
        if ($ZapExit -gt 1) { throw "Falha operacional do ZAP (código $ZapExit)." }

        docker compose --profile tools run --rm gate node /workspace/scripts/quality-gate.mjs `
            --zap "/workspace/reports/zap-juice-shop.json" `
            --threshold HIGH `
            --expect fail
        if ($LASTEXITCODE -ne 0) {
            throw "O ZAP não produziu o bloqueio HIGH esperado; revise descoberta, plano e relatório."
        }
    }
    finally {
        docker compose --profile tools down --remove-orphans | Out-Host
    }
}

New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null
Push-Location $ProjectRoot
try {
    docker info *> $null
    if ($LASTEXITCODE -ne 0) { throw "Docker Engine indisponível. Inicie o Docker Desktop." }

    & (Join-Path $PSScriptRoot "fetch-target.ps1")

    if ($Mode -in @("sast-red", "all")) { Invoke-SemgrepScenario -Scenario red }
    if ($Mode -in @("sast-green", "all")) { Invoke-SemgrepScenario -Scenario green }
    if ($Mode -in @("dast", "all")) { Invoke-ZapScenario }
}
finally {
    Pop-Location
}
