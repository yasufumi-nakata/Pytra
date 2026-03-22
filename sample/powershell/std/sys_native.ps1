# sys_native.ps1 — native seam for pytra.std.sys

$script:argv = @()
$script:path = @()
$script:stderr = $null
$script:stdout = $null

function get_argv {
    param()
    return $script:argv
}

function set_argv {
    param($values)
    $script:argv = @($values)
}

function get_path {
    param()
    return $script:path
}

function set_path {
    param($values)
    $script:path = @($values)
}

function exit_ {
    param($code = 0)
    [Environment]::Exit($code)
}

function write_stderr {
    param($text)
    [Console]::Error.Write($text)
}

function write_stdout {
    param($text)
    [Console]::Out.Write($text)
}
