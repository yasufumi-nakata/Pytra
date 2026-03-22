# os_path_native.ps1 — native seam for pytra.std.os_path (os.path)

function join {
    param($a, $b)
    return [System.IO.Path]::Combine($a, $b)
}

function dirname {
    param($p)
    $d = [System.IO.Path]::GetDirectoryName($p)
    if ($d -eq $null) { return "" }
    return $d
}

function basename {
    param($p)
    return [System.IO.Path]::GetFileName($p)
}

function splitext {
    param($p)
    $ext = [System.IO.Path]::GetExtension($p)
    $stem = $p.Substring(0, $p.Length - $ext.Length)
    return @($stem, $ext)
}

function abspath {
    param($p)
    return [System.IO.Path]::GetFullPath($p)
}

function exists {
    param($p)
    return (Test-Path $p)
}
