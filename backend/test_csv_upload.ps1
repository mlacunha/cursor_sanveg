# Script PowerShell para testar upload de CSV
# Uso: .\test_csv_upload.ps1 -CsvPath "caminho\do\seu\arquivo.csv" -Username "seu_usuario" -Password "sua_senha"

param(
    [Parameter(Mandatory=$true)]
    [string]$CsvPath,
    
    [Parameter(Mandatory=$true)]
    [string]$Username,
    
    [Parameter(Mandatory=$true)]
    [string]$Password,
    
    [string]$ApiUrl = "http://localhost:8000"
)

# Desabilitar o progresso para melhor performance
$ProgressPreference = 'SilentlyContinue'

Write-Host "=== Teste de Importação CSV ===" -ForegroundColor Cyan

# 1. Fazer login
Write-Host "`n[1/2] Fazendo login..." -ForegroundColor Yellow
$loginBody = @{
    username = $Username
    password = $Password
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$ApiUrl/api/auth/login" `
        -Method POST `
        -Body $loginBody `
        -ContentType "application/json"
    
    $token = $loginResponse.access_token
    Write-Host "✓ Login bem-sucedido!" -ForegroundColor Green
    Write-Host "Token: $($token.Substring(0, 20))..." -ForegroundColor Gray
}
catch {
    Write-Host "✗ Erro no login: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Upload do CSV
Write-Host "`n[2/2] Fazendo upload do CSV..." -ForegroundColor Yellow
Write-Host "Arquivo: $CsvPath" -ForegroundColor Gray

if (-not (Test-Path $CsvPath)) {
    Write-Host "✗ Arquivo não encontrado: $CsvPath" -ForegroundColor Red
    exit 1
}

# Preparar o multipart/form-data
$boundary = [System.Guid]::NewGuid().ToString()
$fileContent = [System.IO.File]::ReadAllBytes($CsvPath)
$fileName = [System.IO.Path]::GetFileName($CsvPath)

$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
    "Content-Type: text/csv",
    "",
    [System.Text.Encoding]::UTF8.GetString($fileContent),
    "--$boundary--"
)

$body = $bodyLines -join "`r`n"

try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    $response = Invoke-RestMethod -Uri "$ApiUrl/api/relatorio-mapa/import-csv" `
        -Method POST `
        -Headers $headers `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $body
    
    Write-Host "`n✓ Upload concluído!" -ForegroundColor Green
    Write-Host "`nResultado:" -ForegroundColor Cyan
    Write-Host "- Importados: $($response.imported)" -ForegroundColor Green
    Write-Host "- Erros: $($response.errors.Count)" -ForegroundColor $(if ($response.errors.Count -gt 0) { "Yellow" } else { "Green" })
    
    if ($response.errors.Count -gt 0) {
        Write-Host "`nDetalhes dos erros:" -ForegroundColor Yellow
        foreach ($error in $response.errors | Select-Object -First 5) {
            Write-Host "  Linha $($error.row): $($error.error)" -ForegroundColor Red
        }
        if ($response.errors.Count -gt 5) {
            Write-Host "  ... e mais $($response.errors.Count - 5) erros" -ForegroundColor Gray
        }
    }
    
    # Salvar resposta completa em JSON
    $outputFile = "csv_import_result_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    $response | ConvertTo-Json -Depth 10 | Out-File $outputFile
    Write-Host "`nResposta completa salva em: $outputFile" -ForegroundColor Gray
}
catch {
    Write-Host "✗ Erro no upload: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Detalhes: $responseBody" -ForegroundColor Red
    }
    exit 1
}

Write-Host "`n=== Fim do teste ===" -ForegroundColor Cyan
