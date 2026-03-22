# glob_native.ps1 — native seam for pytra.std.glob

function glob {
    param($pattern)
    $items = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    if ($items -eq $null) { return @() }
    return @($items | ForEach-Object { $_.FullName })
}
