# Usage: .\scripts\push-github.ps1 -RepoUrl "https://github.com/USER/REPO.git"
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoUrl
)

$ErrorActionPreference = "Stop"
$git = "C:\Program Files\Git\bin\git.exe"
Set-Location (Split-Path $PSScriptRoot -Parent)

& $git remote remove origin 2>$null
& $git remote add origin $RepoUrl
& $git push -u origin main
Write-Host "Pushed to $RepoUrl"
