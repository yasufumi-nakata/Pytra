# os_native.ps1 — native seam for pytra.std.os

function getcwd {
    param()
    return (Get-Location).Path
}

function mkdir {
    param($p)
    New-Item -ItemType Directory -Path $p -Force | Out-Null
}

function makedirs {
    param($p, $exist_ok = $false)
    if (-not (Test-Path $p)) {
        New-Item -ItemType Directory -Path $p -Force | Out-Null
    }
}

function listdir {
    param($p = ".")
    return @(Get-ChildItem -Path $p -Name)
}
